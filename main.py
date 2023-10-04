import os
import re

from fastapi import FastAPI, Request, HTTPException, status
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from itsdangerous import URLSafeTimedSerializer
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

app = FastAPI()
secret_key = "some-secret-key"  # Replace this with your actual secret key
signer = URLSafeTimedSerializer(secret_key)

app.add_middleware(
    SessionMiddleware, secret_key=secret_key, max_age=3600 * 24  # Session age: 1 day
)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
CLIENT_ID = "562930917300-5t89lqdelnh5q69jlt34b1qut8o8lpkj.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8000/login/callback"
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def get_google_oauth2_flow() -> Flow:
    flow = Flow.from_client_config({
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


@app.get("/login")
def login(request: Request):
    flow = get_google_oauth2_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        approval_prompt='force',  # Add this line
        include_granted_scopes='true'
    )
    request.session["state"] = state
    return RedirectResponse(authorization_url)


@app.get("/login/callback")
def login_callback(request: Request):
    flow = get_google_oauth2_flow()
    flow.fetch_token(authorization_response=str(request.url))
    creds_data = {
        "token": flow.credentials.token,
        "refresh_token": flow.credentials.refresh_token,
        "token_uri": flow.credentials.token_uri,
        "client_id": flow.credentials.client_id,
        "client_secret": flow.credentials.client_secret,
        "scopes": flow.credentials.scopes
    }
    request.session["credentials"] = creds_data

    return RedirectResponse(url="/emails")


@app.get("/emails")
def get_emails(request: Request):
    if "credentials" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in"
        )
    creds_data = request.session["credentials"]
    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"]
    )

    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    emails = []
    for message in messages:
        email_data = service.users().messages().get(userId="me", id=message["id"]).execute()
        # emails.append(email_data)
        headers = email_data['payload']['headers']
        email_id = message["id"]
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender_full = next((header['value'] for header in headers if header['name'] == 'From'), None)
        match = re.search(r'(?:"?(.*?)"?\s)?<(.*?)>', sender_full)
        sender_name = match.group(1) if match and match.group(1) else None
        sender_email = match.group(2) if match else sender_full
        emails.append({
            'email_id': email_id,
            'subject': subject,
            'sender': sender_email,
            'sender_name': sender_name
        })
    print(emails)

    return emails


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
