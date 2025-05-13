#Travel-planner
# 🗺️ AI Travel Planner using GPT-4o | LangChain + OpenAI

Plan your dream trip in seconds using the power of **OpenAI GPT-4o** and **LangChain**. This AI travel assistant takes a **destination**, **number of days**, and **budget**, then generates a **customized travel itinerary** with recommendations for places to visit, food to try, stay options, and a complete **budget breakdown**.

Ideal for students, backpackers, families, or solo travelers looking to explore smartly without spending hours on research.

---

## 📸 Demo

> _Add a screenshot or demo GIF here showing the terminal in action._

---

## ✨ Key Features

- 🧭 **AI-generated Travel Itineraries** tailored to your preferences.
- 🗺️ Includes **places to visit**, **things to do**, and **cultural tips**.
- 🍱 Suggests **local foods** and must-try cuisines.
- 🛏️ Recommends **accommodation options**.
- 💸 Provides a **realistic cost breakdown** (travel, stay, food, etc.).
- 🔁 Fully interactive via **command line interface**.
- 🤖 Built using **LangChain + GPT-4o** for natural, smart planning.

---

## 🧠 Powered By

| Tool/Library    | Purpose                             |
|----------------|-------------------------------------|
| `LangChain`     | Manage prompts and LLM chains      |
| `OpenAI GPT-4o` | Generate high-quality itinerary     |
| `python-dotenv` | Securely load API keys             |
| `Python`        | Application scripting              |

---

## 📁 Project Structure

.
├── travel_planner.py # Main Python script
├── .env # Contains OpenAI API key (not shared)
├── requirements.txt # Python dependencies
└── README.md # Documentation file

yaml
Copy
Edit

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
2. Create and Activate a Virtual Environment (optional)
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Add OpenAI API Key
Create a .env file in the project root and add your key like this:

env
Copy
Edit
OPENAI_API_KEY=your_openai_api_key_here
▶️ How to Use
Run the script from your terminal:

bash
Copy
Edit
python travel_planner.py
You will be prompted for:

✈️ Destination (e.g., Goa)

🗓️ Number of Days (e.g., 3)

💰 Total Budget (₹) (e.g., 15000)

The AI will then generate a full itinerary plan in seconds.

✅ Example
Input:

text
Copy
Edit
Enter destination: Jaipur
Enter number of days: 3
Enter total budget in ₹: 10000
Output:

text
Copy
Edit
Your AI-generated Travel Plan:

Day 1:
- Arrival and check-in at a budget hotel in Pink City (~₹1,000)
- Visit Hawa Mahal, City Palace, and local bazaars
- Dinner at Laxmi Mishtan Bhandar (~₹300)

Day 2:
- Amber Fort, Jaigarh Fort, Elephant ride (~₹1,500)
- Lunch at Rawat Kachori (~₹250)
- Evening at Nahargarh Fort sunset point

Day 3:
- Shopping at Johari Bazaar
- Try Rajasthani Thali at Chokhi Dhani (~₹600)

Total Estimated Budget:
- Stay: ₹3,000
- Food: ₹1,500
- Travel: ₹2,000
- Entry & Activities: ₹2,000
- Misc: ₹1,500
📌 Requirements
Make sure these packages are installed (in requirements.txt):

nginx
Copy
Edit
langchain
langchain-openai
openai
python-dotenv
To install manually:

bash
Copy
Edit
pip install langchain langchain-openai openai python-dotenv
🚀 Deployment Ideas
While this is a command-line tool now, you can easily extend it:

🎛️ Add a web UI using Streamlit or Gradio

🌐 Deploy as a REST API using FastAPI

📲 Turn it into a mobile app using Flutter + Python backend

☁️ Deploy on Streamlit Cloud, Render, or HuggingFace Spaces

🛣️ Roadmap
 Add international trip planning support

 Include live weather data and best season info

 Add QR code export of itinerary

 Generate PDF itinerary

 Allow custom preferences (e.g., beach vs. adventure vs. temples)

🛡️ License
This project is licensed under the MIT License. See LICENSE for details.

🙋‍♀️ Author
Vicky
💡 AI Builder | 🏃‍♀️ Athlete | 💻 MCA Student
📬 Email: your-email@example.com
🔗 GitHub: @yourusername
🔗 LinkedIn: linkedin.com/in/yourname

