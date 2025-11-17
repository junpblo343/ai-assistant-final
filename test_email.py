import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()  # loads EMAIL_ADDRESS and EMAIL_PASSWORD from .env

EMAIL_ADDRESS = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")

# Create a test email
msg = MIMEText("✅ This is a test email from your Crypto Alert system.")
msg["Subject"] = "Test Email: Crypto Alert"
msg["From"] = EMAIL_ADDRESS
msg["To"] = EMAIL_ADDRESS

print("🔍 Testing Gmail login and email sending...")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    print("✅ Test email sent successfully! Check your Gmail inbox.")
except smtplib.SMTPAuthenticationError as e:
    print("❌ Gmail authentication failed.")
    print("Details:", e)
except Exception as e:
    print("⚠️ Another error occurred:", e)
