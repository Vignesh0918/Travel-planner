import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def plan_trip(destination, days, budget):
    llm = ChatOpenAI(model="gpt-4o",temperature=0.7)

    system_prompt = (
        "You are a smart travel planner who creates travel itineraries. "
        "Your response should include places to visit, food, travel tips, and estimated budget breakdown."
    )

    user_prompt = (
        f"Plan a {days}-day trip to {destination} under ₹{budget}. "
        f"Include best places to visit, food options, stay, and cost breakdown."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm(messages)
    return response.content

# For command-line testing
if __name__ == "__main__":
    dest = input("Enter destination: ")
    days = input("Enter number of days: ")
    budget = input("Enter total budget in ₹: ")
    itinerary = plan_trip(dest, days, budget)
    print("\nYour AI-generated Travel Plan:\n")
    print(itinerary)
