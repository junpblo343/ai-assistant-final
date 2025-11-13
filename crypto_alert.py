import os
import smtplib
import time
import requests
import schedule
import argparse
import logging
from logging.handlers import RotatingFileHandler
from email.mime.text import MIMEText
from dotenv import load_dotenv
from colorama import Fore, Style, init
from datetime import datetime

SUMMARY_FILE = "daily_summary.txt"

def log_alert(name, message):
    """Save alert messages for daily summary."""
    with open(SUMMARY_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {name}: {message}\n")

def send_daily_summary():
    """Send one daily email summarizing all alerts."""
    if not os.path.exists(SUMMARY_FILE) or os.stat(SUMMARY_FILE).st_size == 0:
        color_log("🕗 No alerts today. Skipping summary email.", "info")
        return

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        summary = f.read()

    subject = f"📊 Daily Crypto Alert Summary — {datetime.now().strftime('%B %d, %Y')}"
    body = f"Here’s your summary of today’s crypto alerts:\n\n{summary}"

    send_email(subject, body)
    color_log("✅ Daily summary email sent!", "success")

    # Clear file after sending
    open(SUMMARY_FILE, "w").close()

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")

CRYPTOCURRENCIES = {
    "bitcoin": 100000,
    "solana": 200,
    "algorand": 0.30
}

# 🪵 Rotating logging setup (1 MB per file, keep 5 backups)
log_handler = RotatingFileHandler("alert_log.txt", maxBytes=1_000_000, backupCount=5, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[log_handler]
)

def color_log(message, level="info"):
    """Print and log colored messages."""
    color_map = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    color = color_map.get(level, Fore.WHITE)
    print(color + message + Style.RESET_ALL)

    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)


def send_email(subject, body):
    """Send an email alert."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        color_log(f"✅ Email sent successfully! Subject: {subject}", "success")
    except smtplib.SMTPAuthenticationError as e:
        color_log("❌ Gmail authentication failed — check your App Password.", "error")
        color_log(str(e), "error")
    except Exception as e:
        color_log(f"⚠️ Email sending failed: {e}", "error")


def check_prices():
    """Check crypto prices and send alerts."""
    color_log("🔍 Checking crypto prices...", "info")
    for name, target in CRYPTOCURRENCIES.items():
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={name}&vs_currencies=usd"
            response = requests.get(url)
            response.raise_for_status()
            price = response.json()[name]["usd"]
            color_log(f"{name.capitalize()}: ${price:,}", "info")

            if price >= target:
                subject = f"🚀 {name.capitalize()} Alert!"
                body = f"{name.capitalize()} is now ${price:,}, above your target of ${target:,}!"
                send_email(subject, body)
                log_alert(name, body)   # 👈 Add this line
                color_log(f"📈 {name.capitalize()} is above target! Email sent.", "success")

            elif price <= target * 0.9:
                subject = f"📉 {name.capitalize()} Dropped!"
                body = f"{name.capitalize()} fell to ${price:,}, below your threshold."
                send_email(subject, body)
                log_alert(name, body)   # 👈 Add this line
                color_log(f"📉 {name.capitalize()} dropped significantly! Email sent.", "warning")

        except Exception as e:
            color_log(f"⚠️ Error checking {name}: {e}", "error")
             

def test_email():
    """Send a test email to verify Gmail credentials."""
    color_log("🔍 Testing Gmail login and email sending...", "info")
    msg = MIMEText("✅ This is a test email from your Crypto Alert system.")
    msg["Subject"] = "Test Email: Crypto Alert"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        color_log("✅ Test email sent successfully! Check your Gmail inbox.", "success")
    except smtplib.SMTPAuthenticationError as e:
        color_log("❌ Gmail authentication failed.", "error")
        color_log(str(e), "error")
    except Exception as e:
        color_log(f"⚠️ Another error occurred: {e}", "error")


def main():
    parser = argparse.ArgumentParser(description="Crypto Price Monitor with Email Alerts")
    parser.add_argument("--test", action="store_true", help="Send a test email to verify Gmail setup")
    args = parser.parse_args()

    if args.test:
        test_email()
        return

    color_log("📬 Crypto price monitor running... (Press Ctrl+C to stop)", "info")
    check_prices()
    schedule.every(60).minutes.do(check_prices)
    schedule.every().day.at("18:00").do(send_daily_summary)  # 8 PM summary

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()
