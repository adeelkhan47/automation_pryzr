import json
import logging
import os

import requests
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from fastapi_sqlalchemy import db
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse

from common.enums import EmailStatus
from config import settings
from helpers.deps import Auth
from helpers.jwt import create_access_token
from helpers.platform import taichi, vblink, kirin, orionstar

from model import Email, UserEmail
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
    user_full_name = None
    if userinfo_response.status_code == 200:
        user_info = userinfo_response.json()
        user_email = user_info.get('email', 'No email found')  # Extract email from the response
        user_full_name = user_info.get('name', 'No name found')
        creds_data["email"] = user_email
    else:
        print("Failed to fetch user info")
    # request.session["credentials"] = creds_data

    if user_email:
        print(user_email)
        user = User.get_by_email(user_email)
        if user:

            user.update(id=user.id, to_update={"user_auth": json.dumps(creds_data)})
            logging.info("User already Registered.")
        else:
            user = User(
                email=user_email,
                user_auth=json.dumps(creds_data),
            )
            user.insert()
        access, refresh = create_access_token(user.id)
        token = {
            "full_name": user_full_name,
            "access_token": access,
            "refresh_token": refresh,
            "email": user.email
        }
        return token
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/new_emails")
def process_emails(request: Request):
    # emails = vblink("test000111",1,"justest","justest1")
    # emails = orionstar("Test111_",1,"KingsofvOR","Admin8913")
    emails = kirin("Test000_", 1)
    return {"Data": emails}


@router.get("/platforms")
def user_info(request: Request, user: User = Depends(Auth())):
    data = [each.platform for each in user.platforms]
    return {"Data": data}


# @router.get("/new_emails")
# def process_emails(request: Request):
#     taichi("kelso919", 1)
#     return {"Data": "emails"}


@router.get("/emails")
def process_emails(request: Request, user: User = Depends(Auth()), status: EmailStatus = "",
                   start: int = 1,
                   limit: int = 20,
                   order_by: str = ""):
    args = dict(request.query_params)
    if "status" in args.keys():
        args["status:eq"] = args["status"]
        del args["status"]
    # if user is not None:
    #     args["user_id:eq"] = user.id

    query = db.session.query(Email)

    # If user_id is provided, join with UserEmail to filter by user_id
    if user is not None:
        query = query.join(UserEmail).filter(UserEmail.user_id == user.id)
    emails, count = Email.filter_and_order(args, query)
    return {"data": emails, "total_rows": count, "error": None}
