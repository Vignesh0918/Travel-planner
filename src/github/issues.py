from __future__ import annotations

from typing import Any

from src.github.client import GitHubClient


class GitHubIssueService:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def list_open_issues(self) -> list[dict[str, Any]]:
        return self.client.get(f"/repos/{self.client.owner}/{self.client.repo}/issues", params={"state": "open"})

    def get_issue(self, issue_number: int) -> dict[str, Any]:
        return self.client.get(f"/repos/{self.client.owner}/{self.client.repo}/issues/{issue_number}")

    def get_issue_comments(self, issue_number: int) -> list[dict[str, Any]]:
        return self.client.get(f"/repos/{self.client.owner}/{self.client.repo}/issues/{issue_number}/comments")

    def search_duplicates(self, title: str, issue_number: int) -> list[dict[str, Any]]:
        q = f'repo:{self.client.repository} is:issue in:title "{title}"'
        result = self.client.get("/search/issues", params={"q": q})
        items = result.get("items", [])
        return [item for item in items if int(item.get("number", -1)) != issue_number]

    def create_issue_comment(self, issue_number: int, message: str) -> dict[str, Any]:
        return self.client.post(
            f"/repos/{self.client.owner}/{self.client.repo}/issues/{issue_number}/comments",
            payload={"body": message},
        )
