from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class GitHubClient:
    token: str
    repository: str
    base_url: str = "https://api.github.com"

    def __post_init__(self) -> None:
        if "/" not in self.repository:
            raise ValueError("repository must be owner/repo")

    @property
    def owner(self) -> str:
        return self.repository.split("/", 1)[0]

    @property
    def repo(self) -> str:
        return self.repository.split("/", 1)[1]

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            auth_value = "Bearer " + self.token
            headers["Authorization"] = auth_value
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=self._headers(),
            timeout=30,
            **kwargs,
        )
        if response.status_code >= 400:
            if response.status_code in {401, 403}:
                raise RuntimeError("GitHub authentication or permission failure")
            if response.status_code == 429:
                raise RuntimeError("GitHub API rate limited")
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")
        if not response.text:
            return {}
        return response.json()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, payload: dict[str, Any]) -> Any:
        return self._request("POST", path, json=payload)
