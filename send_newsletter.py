import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from newsletter_api.database import get_all_subscribers

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
HTML_PATH = "data/vector_daily.html"
LOGO_PATH = "data/logo.png"
SUBJECT = "📰 The Vector Daily - AI Newsletter"

def send_email(recipient_email):
    if not os.path.exists(HTML_PATH):
        print(f"❌ Newsletter file not found at {HTML_PATH}")
        return

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    msg = MIMEMultipart("related")
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = SUBJECT

    alt = MIMEMultipart("alternative")
    msg.attach(alt)
    alt.attach(MIMEText(html_content, "html"))

    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header("Content-ID", "<logo>")
            logo.add_header("Content-Disposition", "inline", filename="logo.jpg")
            msg.attach(logo)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"✅ Sent newsletter to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send to {recipient_email}: {e}")

def main():
    subscribers = get_all_subscribers()
    if not subscribers:
        print("⚠️ No subscribers found in database.")
        return

    print(f"📬 Sending newsletter to {len(subscribers)} subscribers...")
    for email in subscribers:
        send_email(email)

if __name__ == "__main__":
    main()
