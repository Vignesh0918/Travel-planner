from __future__ import annotations

import argparse
from dotenv import load_dotenv

from src.agents.executors import LocalGitExecutor
from src.agents.issue_detector import IssueDetectionAgent
from src.agents.issue_resolver import IssueResolutionAgent
from src.agents.issue_validator import IssueValidationAgent
from src.config.settings import Settings
from src.github.client import GitHubClient
from src.github.issues import GitHubIssueService
from src.github.pull_requests import GitHubPullRequestService
from src.llm.factory import build_llm_provider
from src.models.schemas import ApprovalDecision
from src.notifications.developer_notify import DeveloperNotifier
from src.orchestration.approval_gate import ApprovalGate
from src.orchestration.state_store import StateStore
from src.orchestration.workflow import IssueResolutionWorkflow
from src.utils.logging import StructuredLogger, configure_logging


def build_workflow(settings: Settings) -> IssueResolutionWorkflow:
    github_client = GitHubClient(
        token=settings.github_token,
        repository=settings.github_repository,
        base_url=settings.github_api_base_url,
    )
    issues_service = GitHubIssueService(github_client)
    pr_service = GitHubPullRequestService(github_client)
    store = StateStore(settings.state_db_path)

    llm_provider = None
    if settings.openai_api_key and settings.llm_provider == "OPENAI":
        llm_provider = build_llm_provider(settings)

    detector = IssueDetectionAgent(settings.github_repository, issues_service, store)
    validator = IssueValidationAgent(repository_root=".", issues_service=issues_service, llm_provider=llm_provider)
    executor = LocalGitExecutor(repository_root=".", pr_service=pr_service)
    resolver = IssueResolutionAgent(executor=executor)
    approval_gate = ApprovalGate(store=store, notifier=DeveloperNotifier())

    return IssueResolutionWorkflow(
        repository=settings.github_repository,
        store=store,
        detector=detector,
        validator=validator,
        resolver=resolver,
        approval_gate=approval_gate,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-powered GitHub Issue Resolution workflow")
    parser.add_argument("command", choices=["process", "approve", "reject", "resume"], help="Workflow command")
    parser.add_argument("--issue", type=int, required=True, help="Issue number")
    parser.add_argument("--by", type=str, default="developer", help="Decision actor")
    parser.add_argument("--reason", type=str, default="", help="Decision reason")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    logger = StructuredLogger("issue-resolution")

    if not settings.github_repository:
        raise ValueError("GITHUB_REPOSITORY is required (owner/repo)")

    workflow = build_workflow(settings)
    args = parse_args()

    if args.command in {"approve", "reject"}:
        decision = ApprovalDecision(
            issue_number=args.issue,
            approved=args.command == "approve",
            approved_by=args.by,
            reason=args.reason,
        )
        workflow.approval_gate.record_decision(settings.github_repository, decision)
        logger.info("approval decision recorded", issue_number=args.issue, approved=decision.approved, actor=args.by)
        return 0

    if args.command == "process":
        state = workflow.process_issue(args.issue)
    else:
        state = workflow.resume_approved_issue(args.issue)

    logger.info("workflow completed", issue_number=args.issue, state=state.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
