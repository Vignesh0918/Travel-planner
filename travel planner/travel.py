import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config.settings import Settings
from src.llm.factory import build_llm_provider
from src.travel_planner.service import plan_trip


# Load API key from .env
load_dotenv()


def run_travel_planner(destination: str, days: str, budget: str) -> str:
    os.environ.setdefault("LLM_PROVIDER", "OPENAI")
    settings = Settings.from_env()
    provider = build_llm_provider(settings)
    return plan_trip(provider, destination, days, budget)


# For command-line testing
if __name__ == "__main__":
    dest = input("Enter destination: ")
    days = input("Enter number of days: ")
    budget = input("Enter total budget in ₹: ")
    itinerary = run_travel_planner(dest, days, budget)
    print("\nYour AI-generated Travel Plan:\n")
    print(itinerary)
