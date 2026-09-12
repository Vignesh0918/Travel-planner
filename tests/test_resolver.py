from src.agents.issue_resolver import IssueResolutionAgent
from src.models.schemas import ApprovalDecision, IssuePayload, ResolutionTask, ValidationReport


class FakeExecutor:
    def __init__(self, pass_tests=True):
        self.pass_tests = pass_tests
        self.branch = None

    def create_branch(self, branch_name: str) -> str:
        self.branch = branch_name
        return branch_name

    def apply_fix(self, task: ResolutionTask) -> list[str]:
        return ["src/x.py"]

    def run_tests(self) -> tuple[bool, str]:
        return self.pass_tests, "ok" if self.pass_tests else "fail"

    def create_pull_request(self, task: ResolutionTask, branch_name: str, changed_files: list[str]) -> str:
        return "https://example/pr/1"


def _task(approved: bool) -> ResolutionTask:
    issue = IssuePayload(repository="o/r", issue_number=9, title="x", description="y")
    report = ValidationReport(
        issue_number=9,
        valid=True,
        duplicate=False,
        reproducible=True,
        severity="medium",
        priority="high",
        summary="",
        root_cause="",
        affected_files=["src/x.py"],
        affected_components=["app"],
        technical_analysis="",
        recommended_solution="",
        tests_required=["test_x"],
        implementation_complexity="low",
        confidence=90,
    )
    decision = ApprovalDecision(issue_number=9, approved=approved, approved_by="dev")
    return ResolutionTask(issue=issue, validation=report, approval=decision)


def test_agent3_blocked_without_approval() -> None:
    agent = IssueResolutionAgent(executor=FakeExecutor())
    result = agent.resolve(_task(False))
    assert not result["approved"]


def test_agent3_executes_with_approval() -> None:
    agent = IssueResolutionAgent(executor=FakeExecutor(pass_tests=True))
    result = agent.resolve(_task(True))
    assert result["tests_passed"]
    assert result["pr_reference"]


def test_agent3_handles_test_failures() -> None:
    agent = IssueResolutionAgent(executor=FakeExecutor(pass_tests=False))
    result = agent.resolve(_task(True))
    assert not result["tests_passed"]
