import os
import smtplib
from pathlib import Path
from typing import Optional
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # 587 (STARTTLS) or 465 (SSL)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

MAIL_FROM = os.getenv("MAIL_FROM", "support@realwin.ai")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Realwin Support")

PASSWORD_RESET_EXPIRES_MIN = int(os.getenv("PASSWORD_RESET_EXPIRES_MIN", "30"))
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL", "https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app/reset-password")

SMTP_DEBUG = int(os.getenv("SMTP_DEBUG", "0"))


EMAIL_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "emails"

env = Environment(
    loader=FileSystemLoader(EMAIL_TEMPLATES_DIR.as_posix()),
    autoescape=select_autoescape(["html", "xml"]),
)

def render_template(template_name: str, **kwargs) -> str:
    try:
        template = env.get_template(template_name)
        return template.render(**kwargs)
    except TemplateNotFound as e:
        raise RuntimeError(
            f"Email template not found: '{template_name}'\n"
            f"Tried directory: {EMAIL_TEMPLATES_DIR}"
        ) from e

def send_email(to_email: str, subject: str, html: str) -> None:
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"] = to_email

    if SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
            if SMTP_DEBUG:
                smtp.set_debuglevel(1)
            if SMTP_USER and SMTP_PASS:
                smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            if SMTP_DEBUG:
                smtp.set_debuglevel(1)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            if SMTP_USER and SMTP_PASS:
                smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)


def send_reset_email(to_email: str, name: Optional[str], token: str) -> None:
    display_name = name or to_email.split("@")[0]
    reset_link = f"{FRONTEND_RESET_URL}?token={token}"

    html = render_template(
        "reset_password.html",
        name=display_name,
        reset_link=reset_link,
        expire_minutes=PASSWORD_RESET_EXPIRES_MIN,
        brand_name=MAIL_FROM_NAME,
        support_email=MAIL_FROM,
    )

    send_email(to_email, "Password Reset Request", html)
