import pytest

from src.mcp.tools_write import WriteTools


class FakeGate:
    def __init__(self, approved: bool):
        self.approved = approved

    def is_approved(self, repository: str, issue_number: int) -> bool:
        return self.approved


class FakePRService:
    def create_branch(self, branch_name: str):
        return {"ref": branch_name}

    def create_pull_request(self, title: str, body: str, head: str):
        return {"url": "https://example/pr/1"}


def test_write_tools_block_without_approval() -> None:
    tools = WriteTools(FakeGate(False), "o/r", FakePRService())
    with pytest.raises(PermissionError):
        tools.create_branch(1, "fix/issue-1")


def test_write_tools_allow_with_approval() -> None:
    tools = WriteTools(FakeGate(True), "o/r", FakePRService())
    response = tools.create_branch(1, "fix/issue-1")
    assert response["ref"] == "fix/issue-1"
