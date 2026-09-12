from __future__ import annotations

from pathlib import Path

from src.github.issues import GitHubIssueService
from src.llm.provider import LLMProvider
from src.models.schemas import IssuePayload, ValidationReport


class IssueValidationAgent:
    def __init__(self, repository_root: str, issues_service: GitHubIssueService, llm_provider: LLMProvider | None = None) -> None:
        self.repository_root = Path(repository_root)
        self.issues_service = issues_service
        self.llm_provider = llm_provider
        self._cache: dict[int, ValidationReport] = {}

    def _find_affected_files(self, issue: IssuePayload) -> list[str]:
        hits: list[str] = []
        keywords = {word.lower() for word in (issue.title + " " + issue.description).split() if len(word) > 3}
        for path in self.repository_root.rglob("*.py"):
            if ".git" in path.parts or "tests" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if any(keyword in text for keyword in list(keywords)[:20]):
                hits.append(str(path.relative_to(self.repository_root)))
        return hits[:10]

    def _is_duplicate(self, issue: IssuePayload) -> bool:
        try:
            duplicates = self.issues_service.search_duplicates(issue.title, issue.issue_number)
        except Exception:
            return False
        return len(duplicates) > 0

    def validate(self, issue: IssuePayload) -> ValidationReport:
        duplicate = self._is_duplicate(issue)
        affected_files = self._find_affected_files(issue)
        reproducible = bool(issue.description.strip())
        valid = not duplicate and reproducible

        root_cause = "Insufficient information to determine root cause"
        technical_analysis = "Issue description and repository were analyzed using static matching heuristics."
        recommended = "Collect reproduction steps and implement a targeted fix in affected files."

        if self.llm_provider and issue.description:
            system_prompt = "You are a senior software engineer validating GitHub issues. Return concise technical findings."
            user_prompt = (
                f"Issue title: {issue.title}\nIssue description: {issue.description}\n"
                f"Affected files candidates: {affected_files}\n"
                "Provide likely root cause and recommended safe solution."
            )
            try:
                llm_text = self.llm_provider.complete(system_prompt, user_prompt)
                technical_analysis = llm_text[:4000]
                root_cause = llm_text.split("\n")[0][:300] or root_cause
                recommended = "Implement minimal safe code change plus tests aligned with the report."
            except Exception:
                technical_analysis += " LLM analysis unavailable due to provider failure."

        report = ValidationReport(
            issue_number=issue.issue_number,
            valid=valid,
            duplicate=duplicate,
            reproducible=reproducible,
            severity="medium" if valid else "low",
            priority="high" if valid else "low",
            summary="Issue appears actionable" if valid else "Issue cannot be actioned safely yet",
            root_cause=root_cause,
            affected_files=affected_files,
            affected_components=["application"] if affected_files else ["unknown"],
            technical_analysis=technical_analysis,
            recommended_solution=recommended,
            tests_required=[f"test_issue_{issue.issue_number}_resolution"],
            implementation_complexity="medium" if affected_files else "low",
            confidence=85 if valid else 55,
        )
        self._cache[issue.issue_number] = report
        return report

    def get_cached_report(self, issue_number: int) -> ValidationReport | None:
        return self._cache.get(issue_number)
