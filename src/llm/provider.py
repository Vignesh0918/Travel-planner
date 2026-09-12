from __future__ import annotations

from abc import ABC, abstractmethod

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class OpenAILLMProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, temperature: float = 0.2) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OPENAI provider")
        self.llm = ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        response = self.llm.invoke(messages)
        return response.content if isinstance(response.content, str) else str(response.content)
