import json
import os

import requests
from fastapi import APIRouter
from fastapi import Request, HTTPException
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse

from config import settings
from helpers.common import get_emails
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
            db_user.insert()
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/emails")
def process_emails(request: Request):
    user = User.get_by_email("fireblink777@gmail.com")
    emails = get_emails(user.user_auth)
    return emails
