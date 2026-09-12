from src.agents.issue_resolver import IssueResolutionAgent
from src.models.schemas import ApprovalDecision, IssuePayload, ValidationReport, WorkflowState
from src.notifications.developer_notify import DeveloperNotifier
from src.orchestration.approval_gate import ApprovalGate
from src.orchestration.state_store import StateStore
from src.orchestration.workflow import IssueResolutionWorkflow


class FakeDetector:
    def __init__(self, payload: IssuePayload | None, fail: bool = False):
        self.payload = payload
        self.fail = fail

    def detect_issue(self, issue_number: int):
        if self.fail:
            raise RuntimeError("detection failure")
        return self.payload

    def get_cached_payload(self, issue_number: int):
        return self.payload


class FakeValidator:
    def __init__(self, report: ValidationReport, fail: bool = False):
        self.report = report
        self.fail = fail

    def validate(self, payload: IssuePayload):
        if self.fail:
            raise RuntimeError("validation failure")
        return self.report

    def get_cached_report(self, issue_number: int):
        return self.report


class FakeResolver(IssueResolutionAgent):
    def __init__(self, result: dict | None = None, fail: bool = False):
        self.result = result or {"tests_passed": True, "pr_reference": "pr://1", "changed_files": []}
        self.fail = fail

    def resolve(self, task):
        if self.fail:
            raise RuntimeError("resolver failure")
        return self.result


class SilentNotifier(DeveloperNotifier):
    def __init__(self):
        self.messages = []

    def send(self, message: str) -> None:
        self.messages.append(message)


def _issue() -> IssuePayload:
    return IssuePayload(repository="o/r", issue_number=1, title="bug", description="details")


def _report(valid=True, duplicate=False) -> ValidationReport:
    return ValidationReport(
        issue_number=1,
        valid=valid,
        duplicate=duplicate,
        reproducible=True,
        severity="medium",
        priority="high",
        summary="",
        root_cause="root",
        affected_files=["src/a.py"],
        affected_components=["app"],
        technical_analysis="analysis",
        recommended_solution="fix",
        tests_required=["test_a"],
        implementation_complexity="medium",
        confidence=90,
    )


def test_workflow_waits_for_approval(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    notifier = SilentNotifier()
    workflow = IssueResolutionWorkflow(
        repository="o/r",
        store=store,
        detector=FakeDetector(_issue()),
        validator=FakeValidator(_report()),
        resolver=FakeResolver(),
        approval_gate=ApprovalGate(store, notifier),
    )
    state = workflow.process_issue(1)
    assert state == WorkflowState.WAITING_FOR_APPROVAL
    assert notifier.messages


def test_workflow_rejected_after_decision(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    notifier = SilentNotifier()
    gate = ApprovalGate(store, notifier)
    gate.record_decision("o/r", ApprovalDecision(issue_number=1, approved=False, approved_by="dev"))
    workflow = IssueResolutionWorkflow("o/r", store, FakeDetector(_issue()), FakeValidator(_report()), FakeResolver(), gate)
    state = workflow.process_issue(1)
    assert state == WorkflowState.REJECTED


def test_workflow_approved_and_pr_created(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    notifier = SilentNotifier()
    gate = ApprovalGate(store, notifier)
    gate.record_decision("o/r", ApprovalDecision(issue_number=1, approved=True, approved_by="dev"))
    workflow = IssueResolutionWorkflow("o/r", store, FakeDetector(_issue()), FakeValidator(_report()), FakeResolver(), gate)
    state = workflow.process_issue(1)
    assert state == WorkflowState.PR_CREATED


def test_workflow_invalid_issue(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    workflow = IssueResolutionWorkflow(
        "o/r",
        store,
        FakeDetector(_issue()),
        FakeValidator(_report(valid=False)),
        FakeResolver(),
        ApprovalGate(store, SilentNotifier()),
    )
    state = workflow.process_issue(1)
    assert state == WorkflowState.INVALID


def test_workflow_duplicate_issue(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    workflow = IssueResolutionWorkflow(
        "o/r",
        store,
        FakeDetector(_issue()),
        FakeValidator(_report(valid=False, duplicate=True)),
        FakeResolver(),
        ApprovalGate(store, SilentNotifier()),
    )
    state = workflow.process_issue(1)
    assert state == WorkflowState.DUPLICATE


def test_workflow_handles_detection_failure(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    workflow = IssueResolutionWorkflow(
        "o/r",
        store,
        FakeDetector(_issue(), fail=True),
        FakeValidator(_report()),
        FakeResolver(),
        ApprovalGate(store, SilentNotifier()),
    )
    assert workflow.process_issue(1) == WorkflowState.NEEDS_HUMAN_REVIEW


def test_workflow_handles_validation_failure(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    workflow = IssueResolutionWorkflow(
        "o/r",
        store,
        FakeDetector(_issue()),
        FakeValidator(_report(), fail=True),
        FakeResolver(),
        ApprovalGate(store, SilentNotifier()),
    )
    assert workflow.process_issue(1) == WorkflowState.NEEDS_HUMAN_REVIEW


def test_workflow_handles_implementation_failure(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    gate = ApprovalGate(store, SilentNotifier())
    gate.record_decision("o/r", ApprovalDecision(issue_number=1, approved=True, approved_by="dev"))
    workflow = IssueResolutionWorkflow(
        "o/r",
        store,
        FakeDetector(_issue()),
        FakeValidator(_report()),
        FakeResolver(fail=True),
        gate,
    )
    assert workflow.process_issue(1) == WorkflowState.IMPLEMENTATION_FAILED


def test_workflow_handles_test_failure(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    gate = ApprovalGate(store, SilentNotifier())
    gate.record_decision("o/r", ApprovalDecision(issue_number=1, approved=True, approved_by="dev"))
    workflow = IssueResolutionWorkflow(
        "o/r",
        store,
        FakeDetector(_issue()),
        FakeValidator(_report()),
        FakeResolver(result={"tests_passed": False, "error": "pytest failed", "changed_files": []}),
        gate,
    )
    assert workflow.process_issue(1) == WorkflowState.TEST_FAILED
