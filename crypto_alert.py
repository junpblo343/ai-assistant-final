import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Target thresholds ---
THRESHOLDS = {
    "bitcoin": 65000,    # Alert if above this
    "solana": 150,       # Example value
    "algorand": 0.30     # Example value
}

# --- Fetch crypto prices ---
def get_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data[symbol]["usd"]

# --- Send email ---
def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# --- Check prices ---
def check_prices():
    print("Checking crypto prices...")
    for coin, target in THRESHOLDS.items():
        price = get_price(coin)
        print(f"{coin.capitalize()}: ${price}")

        if price >= target:
            subject = f"🚀 {coin.capitalize()} Price Alert!"
            body = f"{coin.capitalize()} has reached ${price}, above your target of ${target}."
            send_email(subject, body)
            print(f"✅ Email alert sent for {coin}!")
        else:
            print(f"No alert. {coin} still below target.")

# --- Schedule the checks ---
scheduler = BlockingScheduler()
scheduler.add_job(check_prices, 'interval', hours=1)  # check every hour

print("📬 Crypto price monitor running... (Press Ctrl+C to stop)")
check_prices()  # run once at start
scheduler.start()
