from src.models.schemas import ApprovalDecision, IssuePayload, ResolutionTask, ValidationReport


def test_issue_payload_requires_positive_issue_number() -> None:
    try:
        IssuePayload(repository="o/r", issue_number=0, title="x", description="y")
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_resolution_task_requires_matching_issue_ids() -> None:
    issue = IssuePayload(repository="o/r", issue_number=1, title="x", description="y")
    report = ValidationReport(
        issue_number=2,
        valid=True,
        duplicate=False,
        reproducible=True,
        severity="medium",
        priority="high",
        summary="ok",
        root_cause="root",
        affected_files=[],
        affected_components=[],
        technical_analysis="analysis",
        recommended_solution="fix",
        tests_required=[],
        implementation_complexity="low",
        confidence=90,
    )
    decision = ApprovalDecision(issue_number=1, approved=True)
    try:
        ResolutionTask(issue=issue, validation=report, approval=decision)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
