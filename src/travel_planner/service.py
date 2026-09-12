from __future__ import annotations

from src.llm.provider import LLMProvider


def plan_trip(provider: LLMProvider, destination: str, days: str, budget: str) -> str:
    day_count = int(days)
    if day_count <= 0:
        raise ValueError("Number of days must be greater than 0.")

    system_prompt = (
        "You are a smart travel planner who creates travel itineraries. "
        "Your response should include places to visit, food, travel tips, and estimated budget breakdown."
    )
    user_prompt = (
        f"Plan a {days}-day trip to {destination} under ₹{budget}. "
        "Include best places to visit, food options, stay, and cost breakdown."
    )
    return provider.complete(system_prompt, user_prompt)
