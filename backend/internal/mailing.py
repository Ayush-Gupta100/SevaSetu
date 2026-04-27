import logging
import os
import smtplib
from email.message import EmailMessage


logger = logging.getLogger(__name__)

MAIL_SUBJECT = "Community Coordination Notification"


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_mail_password(value: str) -> str:
    cleaned = str(value or "").strip()
    if cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned.replace(" ", "")


def send_mail(to_mail: str, message: str) -> bool:
    """Send a notification email with a fixed subject.

    Uses MAIL_* environment variables.
    Returns True on successful delivery, otherwise False.
    """
    if not to_mail or not message:
        return False

    mail_server = os.getenv("MAIL_SERVER", "").strip()
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_use_tls = _parse_bool(os.getenv("MAIL_USE_TLS", "true"))
    mail_username = os.getenv("MAIL_USERNAME", "").strip()
    mail_password = _normalize_mail_password(os.getenv("MAIL_PASSWORD", ""))

    if not mail_server or not mail_username or not mail_password:
        logger.warning("Email not sent: MAIL_SERVER/MAIL_USERNAME/MAIL_PASSWORD are required.")
        return False

    msg = EmailMessage()
    msg["Subject"] = MAIL_SUBJECT
    msg["From"] = mail_username
    msg["To"] = to_mail
    msg.set_content(message)

    try:
        with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        return True
    except Exception as exc:
        logger.exception("Failed to send mail to %s: %s", to_mail, exc)
        return False


def send_email(to_mail: str, message_body: str) -> bool:
    """Backward-compatible alias."""
    return send_mail(to_mail, message_body)