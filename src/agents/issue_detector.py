from __future__ import annotations

from src.github.issues import GitHubIssueService
from src.models.schemas import IssuePayload, WorkflowState
from src.orchestration.state_store import StateStore


class IssueDetectionAgent:
    def __init__(self, repository: str, issues: GitHubIssueService, store: StateStore) -> None:
        self.repository = repository
        self.issues = issues
        self.store = store
        self._cache: dict[int, IssuePayload] = {}

    def already_processed(self, issue_number: int) -> bool:
        record = self.store.get_record(self.repository, issue_number)
        if not record:
            return False
        return record.state not in {WorkflowState.NEW, WorkflowState.NEEDS_HUMAN_REVIEW}

    def detect_issue(self, issue_number: int) -> IssuePayload | None:
        if self.already_processed(issue_number):
            return None

        issue = self.issues.get_issue(issue_number)
        comments = self.issues.get_issue_comments(issue_number)
        payload = IssuePayload(
            repository=self.repository,
            issue_number=int(issue["number"]),
            title=issue.get("title", "").strip(),
            description=issue.get("body", "").strip(),
            labels=[label.get("name", "") for label in issue.get("labels", []) if label.get("name")],
            author=issue.get("user", {}).get("login", ""),
            assignees=[a.get("login", "") for a in issue.get("assignees", []) if a.get("login")],
            comments=[{"author": c.get("user", {}).get("login", ""), "body": c.get("body", "")} for c in comments],
            created_at=issue.get("created_at", ""),
            status=issue.get("state", "open"),
        )
        self._cache[issue_number] = payload
        return payload

    def get_cached_payload(self, issue_number: int) -> IssuePayload | None:
        return self._cache.get(issue_number)
