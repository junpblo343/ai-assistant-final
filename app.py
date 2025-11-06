from flask import Flask, render_template, request
import requests
import os
from groq import Groq
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# -------------------------------
# APP SETUP
# -------------------------------
app = Flask(__name__)
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# -------------------------------
# AI CHAT FEATURE
# -------------------------------
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
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a helpful and friendly AI assistant."},
                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

            try:
                ai_response = data["choices"][0]["message"]["content"]
            except Exception:
                ai_response = f"Error: {data}"

    return render_template("index.html", user_message=user_message, ai_response=ai_response)


# -------------------------------
# CRYPTO PRICE MONITOR FEATURE
# -------------------------------
def get_crypto_price(symbol: str):
    """Fetch real-time price from CoinGecko (no API key needed)."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data[symbol]["usd"]


def send_email_alert(subject, body, to_email):
    """Send email alerts via Gmail (use App Password)."""
    sender_email = os.getenv("ALERT_EMAIL")
    sender_password = os.getenv("ALERT_EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("⚠️ Email credentials not set in environment variables.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)


@app.route("/crypto")
def crypto_prices():
    """Show Bitcoin, Solana, and Algorand prices, and send alerts if thresholds are hit."""
    btc = get_crypto_price("bitcoin")
    sol = get_crypto_price("solana")
    algo = get_crypto_price("algorand")

    # Example alerts
    if btc > 80000:
        send_email_alert("🚀 Bitcoin Alert", f"BTC is now ${btc}!", os.getenv("ALERT_RECEIVER"))
    elif btc < 60000:
        send_email_alert("📉 Bitcoin Dip Alert", f"BTC dropped to ${btc}", os.getenv("ALERT_RECEIVER"))

    return render_template("crypto.html", btc=btc, sol=sol, algo=algo)


# -------------------------------
# APP STARTUP
# -------------------------------
if __name__ == "__main__":
    print("🚀 Flask AI assistant with Crypto Monitor running on http://127.0.0.1:8080")
    app.run(debug=True, port=8080)
