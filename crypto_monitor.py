import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Detect Render environment
RUNNING_ON_RENDER = os.environ.get("RENDER") == "true"

# Crypto alert targets — ensure float conversion ALWAYS happens
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


def get_price(coin):
    """Returns float price or None if API fails"""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        print("API RESPONSE:", data)

        # Handle API errors (like rate limits)
        if "status" in data and "error_code" in data["status"]:
            return None  # force skip

        if coin not in data:
            return None

        return float(data[coin]["usd"])

    except Exception as e:
        print(f"❌ API ERROR for {coin}: {e}")
        return None


def send_email(subject, message):
    """Skip email alerts on Render"""
    if RUNNING_ON_RENDER:
        print("📭 Email sending skipped on Render.")
        return

    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Missing email credentials — skipping.")
        return

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
        print(f"❌ Email error: {e}")


def check_prices(skip_email=False):
    summary = ""

    for coin, targets in CRYPTO_TARGETS.items():

        price = get_price(coin)

        # If API failed (rate limit or connection problem)
        if price is None:
            summary += f"⚠️ Unable to fetch {coin} price (API limit or connection error).\n"
            continue

        summary += f"💰 {coin.capitalize()} price: ${price}\n"

        up_target = float(targets["up"])
        down_target = float(targets["down"])

        # Compare safely
        if price >= up_target:
            if not skip_email:
                send_email(
                    f"🚀 {coin.capitalize()} Price Alert!",
                    f"{coin.capitalize()} is now ${price} (above ${up_target})!"
                )
            summary += "🚀 Above target!\n"

        elif price <= down_target:
            if not skip_email:
                send_email(
                    f"📉 {coin.capitalize()} Price Alert!",
                    f"{coin.capitalize()} dropped to ${price} (below ${down_target})!"
                )
            summary += "📉 Below target!\n"

    return summary


if __name__ == "__main__":
    print(check_prices())
