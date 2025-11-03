from flask import Flask, render_template, request
import requests
import os
from groq import Groq


app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "sk-" + "placeholder")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def chat():
    user_message = ""
    ai_response = ""

    if request.method == "POST":
        user_message = request.form.get("message")

        if user_message:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            payload = {
                "model": "llama-3.1-8b-instant",  # ✅ new working model
                "messages": [
                    {"role": "system", "content": "You are a helpful and friendly AI assistant."},
                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

            try:
                ai_response = data["choices"][0]["message"]["content"]
            except Exception as e:
                ai_response = f"Error: {data}"

    return render_template("index.html", user_message=user_message, ai_response=ai_response)

if __name__ == "__main__":
    print("🚀 Flask AI assistant running on http://127.0.0.1:8080")
    app.run(debug=True, port=8080)
