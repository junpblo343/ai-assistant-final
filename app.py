from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from groq import Groq
from crypto_monitor import check_prices
from apscheduler.schedulers.background import BackgroundScheduler

# Detect Render environment
RUNNING_ON_RENDER = os.environ.get("RENDER") == "true"

app = Flask(__name__)

load_dotenv()

# Load Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY is missing!")
else:
    print("✅ Loaded GROQ_API_KEY successfully")

client = Groq(api_key=GROQ_API_KEY)

# Scheduler (disabled on Render)
scheduler = BackgroundScheduler()

def scheduled_price_check():
    print("🕒 Scheduled crypto price check executing…")
    result = check_prices()
    print(result)

# Enable scheduler ONLY locally
if not RUNNING_ON_RENDER:
    scheduler.add_job(scheduled_price_check, "interval", hours=1)
    scheduler.start()

@app.route("/", methods=["GET", "POST"])
def chat():
    user_message = ""
    ai_response = ""

    if request.method == "POST":

        # --- Chat Request ---
        if "message" in request.form:
            user_message = request.form.get("message")

            if GROQ_API_KEY is None:
                ai_response = "❌ ERROR: GROQ_API_KEY is missing on server."
            else:
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
                except:
                    ai_response = f"Error from Groq: {data}"

        # --- Crypto Check Button ---
        elif "check_prices" in request.form:

            # Skip emails on Render
            if RUNNING_ON_RENDER:
                ai_response = check_prices(skip_email=True)
            else:
                ai_response = check_prices()

            user_message = ai_response

    return render_template("index.html",
                           user_message=user_message,
                           ai_response=ai_response)

# Local-run only
if __name__ == "__main__" and not RUNNING_ON_RENDER:
    print("🚀 Running locally at http://127.0.0.1:8080")
    app.run(debug=True, port=8080)
