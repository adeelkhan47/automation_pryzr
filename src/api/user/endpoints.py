import json
import re

import requests
from fastapi import APIRouter
from fastapi import Request, HTTPException, status
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from starlette.responses import RedirectResponse
import os
from config import settings
from model.user import User

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
router = APIRouter()


def get_google_oauth2_flow() -> Flow:
    flow = Flow.from_client_config({
        "web": {
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": [settings.REDIRECT_URI],
        }
    }, settings.SCOPES)
    flow.redirect_uri = settings.REDIRECT_URI
    return flow


@router.get("/login")
def login(request: Request):
    flow = get_google_oauth2_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        approval_prompt='force',  # Add this line
        include_granted_scopes='true'
    )
    request.session["state"] = state
    return RedirectResponse(authorization_url)


@router.get("/login/callback")
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
    headers = {'Authorization': 'Bearer {}'.format(flow.credentials.token)}
    userinfo_response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers)
    user_email = None
    if userinfo_response.status_code == 200:
        user_info = userinfo_response.json()
        user_email = user_info.get('email', 'No email found')  # Extract email from the response
        creds_data["email"] = user_email
    else:
        print("Failed to fetch user info")
    request.session["credentials"] = creds_data

    if user_email:
        print(user_email)
        user = User.get_by_email(user_email)
        if user:
            print("User Exist.")
        else:
            db_user = User(
                email=user_email,
                user_auth=json.dumps(creds_data),
            )
            db_user = db_user.insert()
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/emails")
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
