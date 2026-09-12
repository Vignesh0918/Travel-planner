from __future__ import annotations

from src.models.schemas import ApprovalDecision, ValidationReport
from src.notifications.developer_notify import DeveloperNotifier
from src.orchestration.state_store import StateStore


class ApprovalGate:
    def __init__(self, store: StateStore, notifier: DeveloperNotifier) -> None:
        self.store = store
        self.notifier = notifier

    def request_approval(self, repository: str, issue_title: str, issue_description: str, validation: ValidationReport) -> str:
        message = self.notifier.build_approval_message(issue_title, issue_description, validation)
        self.notifier.send(message)
        return message

    def record_decision(self, repository: str, decision: ApprovalDecision) -> None:
        self.store.save_approval(repository, decision)

    def is_approved(self, repository: str, issue_number: int) -> bool:
        decision = self.store.get_approval(repository, issue_number)
        return bool(decision and decision.approved)

    def get_decision(self, repository: str, issue_number: int) -> ApprovalDecision | None:
        return self.store.get_approval(repository, issue_number)
