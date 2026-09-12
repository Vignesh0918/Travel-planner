from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_token: str = ""
    github_repository: str = ""
    github_api_base_url: str = "https://api.github.com"
    llm_provider: str = "OPENAI"
    llm_model: str = "gpt-4o"
    openai_api_key: str = ""
    state_db_path: str = "state/workflow_state.db"
    log_level: str = "INFO"
    approval_channel: str = "stdout"
    max_retries: int = 2

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            github_token=os.getenv("GITHUB_TOKEN", ""),
            github_repository=os.getenv("GITHUB_REPOSITORY", ""),
            github_api_base_url=os.getenv("GITHUB_API_BASE_URL", "https://api.github.com"),
            llm_provider=os.getenv("LLM_PROVIDER", "OPENAI").upper(),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            state_db_path=os.getenv("STATE_DB_PATH", "state/workflow_state.db"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            approval_channel=os.getenv("APPROVAL_CHANNEL", "stdout"),
            max_retries=int(os.getenv("MAX_RETRIES", "2")),
        )
