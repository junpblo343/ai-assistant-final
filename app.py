from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from groq import Groq
from crypto_monitor import check_prices
from apscheduler.schedulers.background import BackgroundScheduler  # ✅ NEW

app = Flask(__name__)

load_dotenv()

# ✅ Groq API setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ✅ Scheduler setup
scheduler = BackgroundScheduler()

def scheduled_price_check():
    print("🕐 Scheduled crypto price check running...")
    result = check_prices()
    print(result)

scheduler.add_job(scheduled_price_check, "interval", hours=1)  # Run every hour
scheduler.start()

@app.route("/", methods=["GET", "POST"])
def chat():
    user_message = ""
    ai_response = ""

    if request.method == "POST":
        if "message" in request.form:
            user_message = request.form.get("message")
            if user_message:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": user_message}
                    ]
                }
                response = requests.post(url, headers=headers, json=payload)
                data = response.json()
                try:
                    ai_response = data["choices"][0]["message"]["content"]
                except Exception as e:
                    ai_response = f"Error: {data}"

        elif "check_prices" in request.form:
            ai_response = check_prices()
            user_message = "Checked crypto prices and alerts."

    return render_template("index.html", user_message=user_message, ai_response=ai_response)

if __name__ == "__main__":
    print("🚀 Flask AI assistant running on http://127.0.0.1:8080")
    app.run(debug=True, port=8080)
