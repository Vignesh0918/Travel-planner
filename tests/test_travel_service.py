from src.travel_planner.service import plan_trip


class FakeLLMProvider:
    def __init__(self) -> None:
        self.last_system_prompt = ""
        self.last_user_prompt = ""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return "ok"


def test_plan_trip_accepts_positive_days() -> None:
    provider = FakeLLMProvider()
    response = plan_trip(provider, destination="Paris", days="3", budget="50000")
    assert response == "ok"
    assert "Plan a 3-day trip to Paris under ₹50000." in provider.last_user_prompt


def test_plan_trip_rejects_zero_days() -> None:
    provider = FakeLLMProvider()
    try:
        plan_trip(provider, destination="Paris", days="0", budget="50000")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Days must be a positive integer."


def test_plan_trip_rejects_negative_days() -> None:
    provider = FakeLLMProvider()
    try:
        plan_trip(provider, destination="Paris", days="-2", budget="50000")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Days must be a positive integer."
