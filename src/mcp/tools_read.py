from __future__ import annotations

from src.github.issues import GitHubIssueService


class ReadTools:
    def __init__(self, issue_service: GitHubIssueService) -> None:
        self.issue_service = issue_service

    def list_issues(self) -> list[dict]:
        return self.issue_service.list_open_issues()

    def get_issue(self, issue_number: int) -> dict:
        return self.issue_service.get_issue(issue_number)

    def get_issue_comments(self, issue_number: int) -> list[dict]:
        return self.issue_service.get_issue_comments(issue_number)

    def search_issues(self, title: str, issue_number: int) -> list[dict]:
        return self.issue_service.search_duplicates(title, issue_number)
