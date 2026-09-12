from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.models.schemas import ResolutionTask


class ResolutionExecutor(Protocol):
    def create_branch(self, branch_name: str) -> str: ...
    def apply_fix(self, task: ResolutionTask) -> list[str]: ...
    def run_tests(self) -> tuple[bool, str]: ...
    def create_pull_request(self, task: ResolutionTask, branch_name: str, changed_files: list[str]) -> str: ...


@dataclass
class DefaultNoopExecutor:
    def create_branch(self, branch_name: str) -> str:
        return branch_name

    def apply_fix(self, task: ResolutionTask) -> list[str]:
        return task.validation.affected_files

    def run_tests(self) -> tuple[bool, str]:
        return True, "tests passed"

    def create_pull_request(self, task: ResolutionTask, branch_name: str, changed_files: list[str]) -> str:
        return f"PR for issue #{task.issue.issue_number} on branch {branch_name}"


class IssueResolutionAgent:
    def __init__(self, executor: ResolutionExecutor | None = None) -> None:
        self.executor = executor or DefaultNoopExecutor()

    def resolve(self, task: ResolutionTask) -> dict:
        if not task.approval.approved:
            return {
                "issue_number": task.issue.issue_number,
                "approved": False,
                "tests_passed": False,
                "error": "Developer approval is required",
            }

        branch = f"fix/issue-{task.issue.issue_number}"
        self.executor.create_branch(branch)
        changed_files = self.executor.apply_fix(task)
        tests_passed, test_output = self.executor.run_tests()
        if not tests_passed:
            return {
                "issue_number": task.issue.issue_number,
                "approved": True,
                "branch": branch,
                "changed_files": changed_files,
                "tests_passed": False,
                "error": test_output,
            }

        pr_reference = self.executor.create_pull_request(task, branch, changed_files)
        return {
            "issue_number": task.issue.issue_number,
            "approved": True,
            "branch": branch,
            "changed_files": changed_files,
            "tests_passed": True,
            "pr_reference": pr_reference,
        }
