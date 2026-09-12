from __future__ import annotations

from src.github.pull_requests import GitHubPullRequestService
from src.orchestration.approval_gate import ApprovalGate


class WriteTools:
    def __init__(self, approval_gate: ApprovalGate, repository: str, pr_service: GitHubPullRequestService) -> None:
        self.approval_gate = approval_gate
        self.repository = repository
        self.pr_service = pr_service

    def create_branch(self, issue_number: int, branch_name: str) -> dict:
        self._ensure_approved(issue_number)
        return self.pr_service.create_branch(branch_name)

    def create_pull_request(self, issue_number: int, title: str, body: str, head: str) -> dict:
        self._ensure_approved(issue_number)
        return self.pr_service.create_pull_request(title=title, body=body, head=head)

    def _ensure_approved(self, issue_number: int) -> None:
        if not self.approval_gate.is_approved(self.repository, issue_number):
            raise PermissionError("Issue is not approved by developer")
