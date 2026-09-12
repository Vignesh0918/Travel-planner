from __future__ import annotations

from src.agents.issue_detector import IssueDetectionAgent
from src.agents.issue_resolver import IssueResolutionAgent
from src.agents.issue_validator import IssueValidationAgent
from src.models.schemas import ApprovalDecision, ResolutionTask, WorkflowState
from src.orchestration.approval_gate import ApprovalGate
from src.orchestration.state_store import StateStore


class IssueResolutionWorkflow:
    def __init__(
        self,
        repository: str,
        store: StateStore,
        detector: IssueDetectionAgent,
        validator: IssueValidationAgent,
        resolver: IssueResolutionAgent,
        approval_gate: ApprovalGate,
    ) -> None:
        self.repository = repository
        self.store = store
        self.detector = detector
        self.validator = validator
        self.resolver = resolver
        self.approval_gate = approval_gate

    def process_issue(self, issue_number: int) -> WorkflowState:
        try:
            payload = self.detector.detect_issue(issue_number)
        except Exception as exc:
            self.store.transition(
                self.repository,
                issue_number,
                WorkflowState.NEEDS_HUMAN_REVIEW,
                error_message=f"detection_failed: {exc}",
            )
            return WorkflowState.NEEDS_HUMAN_REVIEW
        if payload is None:
            self.store.transition(self.repository, issue_number, WorkflowState.DUPLICATE)
            return WorkflowState.DUPLICATE

        self.store.transition(self.repository, issue_number, WorkflowState.DETECTED, payload=payload.to_dict())
        self.store.transition(self.repository, issue_number, WorkflowState.VALIDATING)

        try:
            report = self.validator.validate(payload)
        except Exception as exc:
            self.store.transition(
                self.repository,
                issue_number,
                WorkflowState.NEEDS_HUMAN_REVIEW,
                payload=payload.to_dict(),
                error_message=f"validation_failed: {exc}",
            )
            return WorkflowState.NEEDS_HUMAN_REVIEW
        if report.duplicate:
            self.store.transition(self.repository, issue_number, WorkflowState.DUPLICATE, payload=report.to_dict())
            return WorkflowState.DUPLICATE
        if not report.valid:
            self.store.transition(self.repository, issue_number, WorkflowState.INVALID, payload=report.to_dict())
            return WorkflowState.INVALID

        self.store.transition(self.repository, issue_number, WorkflowState.VALID, payload=report.to_dict())
        self.store.transition(self.repository, issue_number, WorkflowState.WAITING_FOR_APPROVAL, payload=report.to_dict())

        self.approval_gate.request_approval(self.repository, payload.title, payload.description, report)
        decision = self.approval_gate.get_decision(self.repository, issue_number)
        if not decision:
            return WorkflowState.WAITING_FOR_APPROVAL
        if not decision.approved:
            self.store.transition(self.repository, issue_number, WorkflowState.REJECTED, payload=decision.to_dict())
            return WorkflowState.REJECTED

        return self._resolve(payload, report, decision)

    def resume_approved_issue(self, issue_number: int) -> WorkflowState:
        record = self.store.get_record(self.repository, issue_number)
        if not record:
            raise ValueError("Issue has no workflow record")
        if record.state not in {WorkflowState.WAITING_FOR_APPROVAL, WorkflowState.APPROVED}:
            raise ValueError("Issue is not waiting for approval")
        decision = self.approval_gate.get_decision(self.repository, issue_number)
        if not decision or not decision.approved:
            return WorkflowState.WAITING_FOR_APPROVAL

        payload = self.detector.get_cached_payload(issue_number)
        report = self.validator.get_cached_report(issue_number)
        if not payload or not report:
            raise ValueError("Missing cached payload/report")
        return self._resolve(payload, report, decision)

    def _resolve(self, payload, report, decision: ApprovalDecision) -> WorkflowState:
        self.store.transition(self.repository, payload.issue_number, WorkflowState.APPROVED, payload=decision.to_dict())
        self.store.transition(self.repository, payload.issue_number, WorkflowState.IMPLEMENTING)

        task = ResolutionTask(issue=payload, validation=report, approval=decision)
        try:
            outcome = self.resolver.resolve(task)
        except Exception as exc:
            self.store.transition(
                self.repository,
                payload.issue_number,
                WorkflowState.IMPLEMENTATION_FAILED,
                error_message=f"implementation_failed: {exc}",
            )
            return WorkflowState.IMPLEMENTATION_FAILED

        self.store.transition(self.repository, payload.issue_number, WorkflowState.TESTING, payload=outcome)
        if not outcome.get("tests_passed", False):
            self.store.transition(
                self.repository,
                payload.issue_number,
                WorkflowState.TEST_FAILED,
                payload=outcome,
                error_message=outcome.get("error", "tests failed"),
            )
            return WorkflowState.TEST_FAILED

        self.store.transition(self.repository, payload.issue_number, WorkflowState.READY_FOR_REVIEW, payload=outcome)
        self.store.transition(self.repository, payload.issue_number, WorkflowState.PR_CREATED, payload=outcome)
        return WorkflowState.PR_CREATED
