from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from src.models.schemas import ApprovalDecision, WorkflowRecord, WorkflowState
from src.orchestration.state_machine import can_transition


class StateStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_state (
                    repository TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    workflow_version TEXT NOT NULL,
                    state TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    correlation_id TEXT,
                    payload_json TEXT,
                    error_message TEXT,
                    PRIMARY KEY (repository, issue_number, workflow_version)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    repository TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    approved INTEGER NOT NULL,
                    approved_by TEXT,
                    approved_at TEXT NOT NULL,
                    reason TEXT,
                    PRIMARY KEY (repository, issue_number)
                )
                """
            )

    def get_record(self, repository: str, issue_number: int, workflow_version: str = "v1") -> WorkflowRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT repository, issue_number, workflow_version, state, updated_at, correlation_id, payload_json, error_message
                FROM workflow_state
                WHERE repository = ? AND issue_number = ? AND workflow_version = ?
                """,
                (repository, issue_number, workflow_version),
            ).fetchone()
        if not row:
            return None
        return WorkflowRecord(
            repository=row["repository"],
            issue_number=row["issue_number"],
            workflow_version=row["workflow_version"],
            state=WorkflowState(row["state"]),
            updated_at=row["updated_at"],
            correlation_id=row["correlation_id"] or "",
            payload_json=row["payload_json"] or "",
            error_message=row["error_message"] or "",
        )

    def upsert_record(self, record: WorkflowRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_state (repository, issue_number, workflow_version, state, updated_at, correlation_id, payload_json, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(repository, issue_number, workflow_version)
                DO UPDATE SET state=excluded.state, updated_at=excluded.updated_at, correlation_id=excluded.correlation_id,
                              payload_json=excluded.payload_json, error_message=excluded.error_message
                """,
                (
                    record.repository,
                    record.issue_number,
                    record.workflow_version,
                    record.state.value,
                    record.updated_at,
                    record.correlation_id,
                    record.payload_json,
                    record.error_message,
                ),
            )

    def transition(
        self,
        repository: str,
        issue_number: int,
        target: WorkflowState,
        payload: dict | None = None,
        workflow_version: str = "v1",
        correlation_id: str = "",
        error_message: str = "",
    ) -> WorkflowRecord:
        current = self.get_record(repository, issue_number, workflow_version)
        if current is None:
            if target not in {WorkflowState.NEW, WorkflowState.DETECTED, WorkflowState.INVALID, WorkflowState.DUPLICATE}:
                raise ValueError("Missing initial state")
            current_state = WorkflowState.NEW
        else:
            current_state = current.state
            if not can_transition(current_state, target) and current_state != target:
                raise ValueError(f"Invalid transition {current_state.value} -> {target.value}")

        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        record = WorkflowRecord(
            repository=repository,
            issue_number=issue_number,
            state=target,
            workflow_version=workflow_version,
            correlation_id=correlation_id,
            payload_json=payload_json,
            error_message=error_message,
        )
        self.upsert_record(record)
        return record

    def save_approval(self, repository: str, decision: ApprovalDecision) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO approvals (repository, issue_number, approved, approved_by, approved_at, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(repository, issue_number)
                DO UPDATE SET approved=excluded.approved, approved_by=excluded.approved_by,
                              approved_at=excluded.approved_at, reason=excluded.reason
                """,
                (
                    repository,
                    decision.issue_number,
                    1 if decision.approved else 0,
                    decision.approved_by,
                    decision.approved_at,
                    decision.reason,
                ),
            )

    def get_approval(self, repository: str, issue_number: int) -> ApprovalDecision | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT issue_number, approved, approved_by, approved_at, reason
                FROM approvals
                WHERE repository = ? AND issue_number = ?
                """,
                (repository, issue_number),
            ).fetchone()
        if not row:
            return None
        return ApprovalDecision(
            issue_number=row["issue_number"],
            approved=bool(row["approved"]),
            approved_by=row["approved_by"] or "",
            approved_at=row["approved_at"],
            reason=row["reason"] or "",
        )
