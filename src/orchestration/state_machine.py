from __future__ import annotations

from src.models.schemas import WorkflowState

VALID_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.NEW: {WorkflowState.DETECTED, WorkflowState.INVALID, WorkflowState.DUPLICATE},
    WorkflowState.DETECTED: {WorkflowState.VALIDATING, WorkflowState.INVALID, WorkflowState.DUPLICATE},
    WorkflowState.VALIDATING: {WorkflowState.VALID, WorkflowState.INVALID, WorkflowState.DUPLICATE},
    WorkflowState.VALID: {WorkflowState.WAITING_FOR_APPROVAL},
    WorkflowState.WAITING_FOR_APPROVAL: {WorkflowState.APPROVED, WorkflowState.REJECTED},
    WorkflowState.APPROVED: {WorkflowState.IMPLEMENTING},
    WorkflowState.IMPLEMENTING: {WorkflowState.TESTING, WorkflowState.IMPLEMENTATION_FAILED},
    WorkflowState.TESTING: {WorkflowState.READY_FOR_REVIEW, WorkflowState.TEST_FAILED},
    WorkflowState.READY_FOR_REVIEW: {WorkflowState.PR_CREATED, WorkflowState.NEEDS_HUMAN_REVIEW},
    WorkflowState.PR_CREATED: {WorkflowState.MERGED, WorkflowState.NEEDS_HUMAN_REVIEW},
    WorkflowState.MERGED: set(),
    WorkflowState.INVALID: set(),
    WorkflowState.DUPLICATE: set(),
    WorkflowState.REJECTED: set(),
    WorkflowState.IMPLEMENTATION_FAILED: {WorkflowState.NEEDS_HUMAN_REVIEW},
    WorkflowState.TEST_FAILED: {WorkflowState.NEEDS_HUMAN_REVIEW},
    WorkflowState.NEEDS_HUMAN_REVIEW: set(),
}


def can_transition(current: WorkflowState, target: WorkflowState) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())
