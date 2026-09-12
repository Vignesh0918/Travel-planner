from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class WorkflowState(str, Enum):
    NEW = "NEW"
    DETECTED = "DETECTED"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    IMPLEMENTING = "IMPLEMENTING"
    TESTING = "TESTING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    PR_CREATED = "PR_CREATED"
    MERGED = "MERGED"
    INVALID = "INVALID"
    DUPLICATE = "DUPLICATE"
    REJECTED = "REJECTED"
    IMPLEMENTATION_FAILED = "IMPLEMENTATION_FAILED"
    TEST_FAILED = "TEST_FAILED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IssuePayload:
    repository: str
    issue_number: int
    title: str
    description: str
    labels: list[str] = field(default_factory=list)
    author: str = ""
    assignees: list[str] = field(default_factory=list)
    comments: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    status: str = "open"

    def __post_init__(self) -> None:
        if self.issue_number <= 0:
            raise ValueError("issue_number must be positive")
        if not self.repository:
            raise ValueError("repository is required")
        if not self.title:
            raise ValueError("title is required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    issue_number: int
    valid: bool
    duplicate: bool
    reproducible: bool
    severity: str
    priority: str
    summary: str
    root_cause: str
    affected_files: list[str]
    affected_components: list[str]
    technical_analysis: str
    recommended_solution: str
    tests_required: list[str]
    implementation_complexity: str
    confidence: int

    def __post_init__(self) -> None:
        if self.issue_number <= 0:
            raise ValueError("issue_number must be positive")
        if not 0 <= self.confidence <= 100:
            raise ValueError("confidence must be 0-100")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ApprovalDecision:
    issue_number: int
    approved: bool
    approved_by: str = ""
    approved_at: str = field(default_factory=now_utc_iso)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResolutionTask:
    issue: IssuePayload
    validation: ValidationReport
    approval: ApprovalDecision

    def __post_init__(self) -> None:
        if self.issue.issue_number != self.validation.issue_number:
            raise ValueError("Issue and validation mismatch")
        if self.issue.issue_number != self.approval.issue_number:
            raise ValueError("Issue and approval mismatch")

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue": self.issue.to_dict(),
            "validation": self.validation.to_dict(),
            "approval": self.approval.to_dict(),
        }


@dataclass
class WorkflowRecord:
    repository: str
    issue_number: int
    state: WorkflowState
    workflow_version: str = "v1"
    updated_at: str = field(default_factory=now_utc_iso)
    correlation_id: str = ""
    payload_json: str = ""
    error_message: str = ""

    def idempotency_key(self) -> str:
        return f"{self.repository}:{self.issue_number}:{self.workflow_version}"
