from __future__ import annotations

import subprocess
from pathlib import Path

from src.github.pull_requests import GitHubPullRequestService
from src.models.schemas import ResolutionTask


class LocalGitExecutor:
    def __init__(self, repository_root: str, pr_service: GitHubPullRequestService | None = None) -> None:
        self.repository_root = Path(repository_root)
        self.pr_service = pr_service

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, cwd=self.repository_root, text=True, capture_output=True, check=False)

    def create_branch(self, branch_name: str) -> str:
        result = self._run("git", "checkout", "-b", branch_name)
        if result.returncode != 0 and "already exists" not in (result.stderr or ""):
            raise RuntimeError(f"Branch creation failed: {result.stderr}")
        return branch_name

    def apply_fix(self, task: ResolutionTask) -> list[str]:
        # Integration point for AI coding agent implementation.
        # This intentionally does not mutate code automatically without explicit implementation logic.
        return task.validation.affected_files

    def run_tests(self) -> tuple[bool, str]:
        result = self._run("python", "-m", "pytest", "-q")
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output.strip()

    def create_pull_request(self, task: ResolutionTask, branch_name: str, changed_files: list[str]) -> str:
        if not self.pr_service:
            return f"manual-pr-required:{branch_name}"
        title = f"fix: resolve issue #{task.issue.issue_number}"
        body = (
            "## Summary\n"
            f"Automated issue resolution workflow prepared changes for issue #{task.issue.issue_number}.\n\n"
            "## Root Cause\n"
            f"{task.validation.root_cause}\n\n"
            "## Changes\n"
            + "\n".join(f"- {f}" for f in changed_files)
            + "\n\n## Tests\n- pytest -q\n\n"
            f"## Related Issue\nCloses #{task.issue.issue_number}\n"
        )
        result = self.pr_service.create_pull_request(title=title, body=body, head=branch_name)
        return result.get("html_url", "")
