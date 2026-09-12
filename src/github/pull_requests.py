from __future__ import annotations

from src.github.client import GitHubClient


class GitHubPullRequestService:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def get_default_branch(self) -> str:
        repo_data = self.client.get(f"/repos/{self.client.owner}/{self.client.repo}")
        return repo_data.get("default_branch", "main")

    def create_branch(self, branch: str, from_branch: str | None = None) -> dict:
        source = from_branch or self.get_default_branch()
        ref_data = self.client.get(f"/repos/{self.client.owner}/{self.client.repo}/git/ref/heads/{source}")
        sha = ref_data["object"]["sha"]
        return self.client.post(
            f"/repos/{self.client.owner}/{self.client.repo}/git/refs",
            payload={"ref": f"refs/heads/{branch}", "sha": sha},
        )

    def create_pull_request(self, title: str, body: str, head: str, base: str | None = None) -> dict:
        return self.client.post(
            f"/repos/{self.client.owner}/{self.client.repo}/pulls",
            payload={
                "title": title,
                "body": body,
                "head": head,
                "base": base or self.get_default_branch(),
                "maintainer_can_modify": False,
                "draft": False,
            },
        )
