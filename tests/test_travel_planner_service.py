import pytest

from src.travel_planner.service import plan_trip


class DummyProvider:
    def __init__(self) -> None:
        self.called = False

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.called = True
        return "itinerary"


def test_plan_trip_rejects_zero_days() -> None:
    provider = DummyProvider()

    with pytest.raises(ValueError, match="Number of days must be greater than 0."):
        plan_trip(provider, destination="Paris", days="0", budget="1000")

    assert not provider.called
