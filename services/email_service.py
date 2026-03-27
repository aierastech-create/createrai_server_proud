import os
import random
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def generate_otp() -> str:
    """Return a 6-digit OTP string."""
    return str(random.randint(100000, 999999))


def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Send an OTP email via SMTP.
    Returns True on success, False on failure (so the route can decide).
    """
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("⚠️  SMTP_USER / SMTP_PASS not set — skipping real email send")
        logger.info(f"[DEV MODE] OTP for {to_email}: {otp}")
        return True  # treat as success in local dev

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your CreatorAI Verification Code"
        msg["From"] = f"CreatorAI <{SMTP_USER}>"
        msg["To"] = to_email

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background:#f4f4f4; padding:30px;">
            <div style="max-width:480px; margin:auto; background:#fff; border-radius:10px; padding:30px;">
              <h2 style="color:#6c63ff;">CreatorAI Email Verification</h2>
              <p>Use the code below to verify your email address. It expires in <strong>10 minutes</strong>.</p>
              <div style="font-size:36px; font-weight:bold; letter-spacing:10px;
                          color:#6c63ff; text-align:center; margin:20px 0;">
                {otp}
              </div>
              <p style="color:#888; font-size:12px;">
                If you did not request this, please ignore this email.
              </p>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        logger.info(f"✅ OTP email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send OTP email: {e}")
        return False
