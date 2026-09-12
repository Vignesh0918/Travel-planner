from src.agents.issue_validator import IssueValidationAgent
from src.models.schemas import IssuePayload


class FakeIssueService:
    def __init__(self, duplicates=False):
        self.duplicates = duplicates

    def search_duplicates(self, title: str, issue_number: int):
        return [{"number": issue_number + 1}] if self.duplicates else []


class FailingLLM:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise RuntimeError("llm failed")


def test_valid_issue_validation(tmp_path) -> None:
    code = tmp_path / "app.py"
    code.write_text("def login():\n    return 'ok'\n", encoding="utf-8")
    issue = IssuePayload(repository="o/r", issue_number=1, title="login broken", description="login fails")
    agent = IssueValidationAgent(str(tmp_path), FakeIssueService(False), llm_provider=None)

    report = agent.validate(issue)
    assert report.valid
    assert report.reproducible


def test_duplicate_issue_validation(tmp_path) -> None:
    issue = IssuePayload(repository="o/r", issue_number=2, title="dup", description="has repro")
    agent = IssueValidationAgent(str(tmp_path), FakeIssueService(True), llm_provider=None)
    report = agent.validate(issue)
    assert report.duplicate
    assert not report.valid


def test_llm_failure_is_handled(tmp_path) -> None:
    issue = IssuePayload(repository="o/r", issue_number=3, title="x", description="y")
    agent = IssueValidationAgent(str(tmp_path), FakeIssueService(False), llm_provider=FailingLLM())
    report = agent.validate(issue)
    assert "LLM analysis unavailable" in report.technical_analysis
