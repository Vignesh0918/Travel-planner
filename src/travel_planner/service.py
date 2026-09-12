from __future__ import annotations

from src.llm.provider import LLMProvider


def _parse_days(days: str) -> int:
    try:
        parsed_days = int(days)
    except (TypeError, ValueError) as exc:
        raise ValueError("Days must be a positive integer.") from exc

    if parsed_days <= 0:
        raise ValueError("Days must be a positive integer.")

    return parsed_days


def plan_trip(provider: LLMProvider, destination: str, days: str, budget: str) -> str:
    parsed_days = _parse_days(days)
    system_prompt = (
        "You are a smart travel planner who creates travel itineraries. "
        "Your response should include places to visit, food, travel tips, and estimated budget breakdown."
    )
    user_prompt = (
        f"Plan a {parsed_days}-day trip to {destination} under ₹{budget}. "
        "Include best places to visit, food options, stay, and cost breakdown."
    )
    return provider.complete(system_prompt, user_prompt)
