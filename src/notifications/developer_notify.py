from __future__ import annotations

from src.models.schemas import ValidationReport


class DeveloperNotifier:
    def send(self, message: str) -> None:
        print(message)

    def build_approval_message(self, issue_title: str, issue_description: str, report: ValidationReport) -> str:
        files = "\n".join(f"- {path}" for path in report.affected_files) or "- None"
        tests = "\n".join(f"- {name}" for name in report.tests_required) or "- None"
        return (
            f"Issue #{report.issue_number}\n\n"
            f"Title:\n{issue_title}\n\n"
            f"Description:\n{issue_description}\n\n"
            f"Validation:\n{'VALID' if report.valid else 'INVALID'}\n\n"
            f"Root Cause:\n{report.root_cause}\n\n"
            f"Affected Files:\n{files}\n\n"
            f"Recommended Solution:\n{report.recommended_solution}\n\n"
            f"Severity: {report.severity}\n"
            f"Priority: {report.priority}\n"
            f"Confidence: {report.confidence}%\n\n"
            f"Tests:\n{tests}\n\n"
            f"Actions:\n[Approve Fix]\n[Reject Fix]"
        )
