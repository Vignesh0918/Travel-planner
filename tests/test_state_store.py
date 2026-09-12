from src.models.schemas import ApprovalDecision, WorkflowState
from src.orchestration.state_store import StateStore


def test_state_transitions_and_approval_storage(tmp_path) -> None:
    db = tmp_path / "state.db"
    store = StateStore(str(db))

    store.transition("o/r", 10, WorkflowState.DETECTED)
    store.transition("o/r", 10, WorkflowState.VALIDATING)
    store.transition("o/r", 10, WorkflowState.VALID)
    record = store.get_record("o/r", 10)

    assert record is not None
    assert record.state == WorkflowState.VALID

    decision = ApprovalDecision(issue_number=10, approved=True, approved_by="dev")
    store.save_approval("o/r", decision)
    loaded = store.get_approval("o/r", 10)
    assert loaded is not None and loaded.approved
