import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Crypto alert thresholds
CRYPTO_TARGETS = {
    "bitcoin": {
        "up": float(os.getenv("BITCOIN_TARGET_UP", 100000)),
        "down": float(os.getenv("BITCOIN_TARGET_DOWN", 60000))
    },
    "solana": {
        "up": float(os.getenv("SOLANA_TARGET_UP", 300)),
        "down": float(os.getenv("SOLANA_TARGET_DOWN", 100))
    },
    "algorand": {
        "up": float(os.getenv("ALGORAND_TARGET_UP", 0.5)),
        "down": float(os.getenv("ALGORAND_TARGET_DOWN", 0.1))
    }
}

# Function to get current price (CoinGecko API)
def get_price(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data[coin]["usd"]

# Function to send email alert
def send_email(subject, message):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Monitor crypto prices
def check_prices():
    summary = ""
    for coin, targets in CRYPTO_TARGETS.items():
        price = get_price(coin)
        summary += f"💰 {coin.capitalize()} price: ${price}\n"

        if price >= targets["up"]:
            send_email(
                f"🚀 {coin.capitalize()} Price Alert!",
                f"{coin.capitalize()} has reached ${price} (above your target of ${targets['up']})!"
            )
            summary += f"🚀 {coin.capitalize()} is above your target (${targets['up']})!\n"

        elif price <= targets["down"]:
            send_email(
                f"📉 {coin.capitalize()} Price Drop Alert!",
                f"{coin.capitalize()} dropped to ${price} (below your target of ${targets['down']})!"
            )
            summary += f"📉 {coin.capitalize()} is below your target (${targets['down']})!\n"

    return summary

if __name__ == "__main__":
    check_prices()
