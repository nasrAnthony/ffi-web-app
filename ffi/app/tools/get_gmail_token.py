# tools/get_gmail_token.py
import os
import pathlib
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

load_dotenv()

SCOPES = [os.getenv("GMAIL_SCOPES", "")]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("secrets/client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)  # opens browser; log into your Gmail
    pathlib.Path("secrets/gmail_token.json").write_text(creds.to_json(), encoding="utf-8")
    print("Saved gmail_token.json next to this script.")

if __name__ == "__main__":
    main()
