from src.agents.issue_detector import IssueDetectionAgent
from src.models.schemas import WorkflowState
from src.orchestration.state_store import StateStore


class FakeIssueService:
    def get_issue(self, issue_number: int):
        return {
            "number": issue_number,
            "title": "Login error",
            "body": "Steps to reproduce",
            "labels": [{"name": "bug"}],
            "user": {"login": "alice"},
            "assignees": [{"login": "bob"}],
            "created_at": "2026-01-01T00:00:00Z",
            "state": "open",
        }

    def get_issue_comments(self, issue_number: int):
        return [{"user": {"login": "eve"}, "body": "same here"}]


def test_issue_detection_and_duplicate_prevention(tmp_path) -> None:
    store = StateStore(str(tmp_path / "state.db"))
    agent = IssueDetectionAgent("o/r", FakeIssueService(), store)

    payload = agent.detect_issue(1)
    assert payload is not None
    assert payload.issue_number == 1

    store.transition("o/r", 1, WorkflowState.DETECTED)
    assert agent.detect_issue(1) is None
