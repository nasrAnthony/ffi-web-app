import base64, json, os, threading
from email.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = [os.getenv("GMAIL_SCOPES", "")]
_TOKEN_LOCK = threading.Lock()
current_dir = os.path.dirname(os.path.abspath(__file__))
gmail_token_path = os.path.join(current_dir, 'tools', 'secrets', 'gmail_token.json')
PROJECT_ROOT = os.path.dirname(current_dir)

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "app", "templates", "app", "emails")
ack_template = os.path.join(TEMPLATES_DIR, "contact_ack.html")
forward_template = os.path.join(TEMPLATES_DIR, "contact_forward.html")

def _load_creds(path: str) -> Credentials:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Credentials.from_authorized_user_info(data, SCOPES)

def _persist_creds(creds: Credentials, path: str):
    with _TOKEN_LOCK:
        with open(path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass

def _gmail_service(creds: Credentials):
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())             # refresh access token via HTTPS
            _persist_creds(creds, gmail_token_path)
        else:
            raise RuntimeError("Gmail credentials invalid and cannot be refreshed.")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def _raw_email(subject: str, from_email: str, to_list: list[str], html: str, reply_to: str | None = None) -> str:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_list)
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(strip_tags(html))                 # text fallback
    msg.add_alternative(html, subtype="html")         # html part
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()

def _send_raw(creds: Credentials, raw: str):
    svc = _gmail_service(creds)
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()

def send_contact_emails(*, ctx: dict, customer_email: str, internal_email: str, from_identity: str):
    """
    ctx keys: name, email, phone?, subject, message, firm_name, submitted_at
    """
    token_path = gmail_token_path
    print(token_path)
    print(ack_template)
    print(forward_template)
    creds = _load_creds(token_path)
    # 1) Acknowledgment to customer (replies go to your internal mailbox)
    html_ack = render_to_string(ack_template, ctx)
    raw_ack = _raw_email(
        subject=f"We received your message: {ctx['subject']}",
        from_email=from_identity,
        to_list=[customer_email],
        html=html_ack,
        reply_to=internal_email,
    )
    _send_raw(creds, raw_ack)

    # 2) Forward to internal team (replies go back to the customer)
    html_fwd = render_to_string(forward_template, ctx)
    raw_fwd = _raw_email(
        subject=f"[Website Contact] {ctx['subject']}",
        from_email=from_identity,
        to_list=[internal_email],
        html=html_fwd,
        reply_to=ctx["email"],
    )
    _send_raw(creds, raw_fwd)
