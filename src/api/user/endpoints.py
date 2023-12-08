import json
import logging
import os
import uuid
from datetime import timezone, datetime, timedelta

import requests
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from fastapi_sqlalchemy import db
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse

from api.user.schemas import GetUser, SignupRequest, GetAccount
from common.enums import EmailStatus
from config import settings
from helpers.common import get_emails
from helpers.deps import Auth
from helpers.jwt import create_access_token
from model.account import Account
from platform_scripts.goldenDragon import run_script
from model import Email, UserEmail, AccountUser
from model.user import User
from helpers.email_service import send_email
from helpers.hash import create_hash, is_correct
from helpers.jwt import create_access_token, get_expiry_time
from helpers.response import jinja2_env

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


@router.get("/get_user", response_model=GetAccount)
def get_user(request: Request, account: Account = Depends(Auth())):
    if account:
        return account
    raise HTTPException(status_code=404, detail="Not Found")


@router.post("/signup")
def signup(request_body: SignupRequest, request: Request):
    unique_id = uuid.uuid4().hex
    if Account.get_by_email(request_body.email):
        raise HTTPException(status_code=405, detail="Email Already Exists.")
    if Account.get_by_username(request_body.username):
        raise HTTPException(status_code=405, detail="Username Already Exists.")

    # Create the account
    account = Account(name=request_body.name, email=request_body.email, username=request_body.username,
                      status=True, phone_number=request_body.phone_number,
                      password=request_body.password, unique_id=unique_id, is_email_authorised=False)

    access, refresh = create_access_token(account.id)
    print(account.name)
    # Prepare the response token
    token = {
        "full_name": account.name,
        "access_token": access,
        "refresh_token": refresh,
        "email": account.email
    }
    template = jinja2_env.get_template("email_confirmation.html")
    send_email(
        account.email,
        "Autom8 Email Verification.",
        template.render(
            fullName=account.name,
            settings=settings,
            unique_id=account.unique_id,
        ),
    )
    account.insert()
    return token


@router.get("/login")
def login(email_or_username, password, request: Request):
    account = Account.get_by_email_pass(email_or_username, password)
    if not account:
        account = Account.get_by_username_pass(email_or_username, password)
        if not account:
            raise HTTPException(status_code=404, detail="Not Found.")

    access, refresh = create_access_token(account.id)
    token = {
        "full_name": account.name,
        "access_token": access,
        "refresh_token": refresh,
        "email": account.email
    }
    return token


@router.get("/confirm_email")
def confirm_email(unique_id: str):
    account = Account.get_by_unique_id(unique_id)
    if not account:
        raise HTTPException(status_code=404, detail="Not Found.")

    current_time = datetime.now(account.created_at.tzinfo)
    time_difference = current_time - account.created_at
    # Calculating the difference
    time_difference = current_time - account.created_at

    # Checking if the difference is greater than 15 minutes
    if time_difference > timedelta(days=7):
        raise HTTPException(status_code=404, detail="Expired Found.")
    Account.update(account.id, {"is_email_authorised": True})
    return "ok"


@router.get("/secondary_login")
def secondary_login(request: Request, email: str, account_unique_id: str):
    # def secondary_login(request: Request, email: str):
    account = Account.get_by_unique_id(account_unique_id)
    if not account:
        raise HTTPException(status_code=403, detail="Unauthorized.")
    unique_id = uuid.uuid4().hex
    if User.get_by_email(email.lower()):
        raise HTTPException(status_code=405, detail="Already Exist.")

    flow = get_google_oauth2_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        approval_prompt='force',
        include_granted_scopes='true'
    )
    user = User(email=email.lower(), user_auth={}, status=True, authorised=False,
                unique_id=str(unique_id))
    user.insert()
    account_user = AccountUser(user_id=user.id, account_id=account.id)
    account_user.insert()
    return RedirectResponse(authorization_url)


@router.get("/login/callback")
def login_callback(request: Request):
    flow = get_google_oauth2_flow()
    state = request.query_params.get('state')
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
        user_email = user_info.get('email', 'No email found')
        user_full_name = user_info.get('name', 'No name found')
        creds_data["email"] = user_email
    else:
        print("Failed to fetch user info")
    # request.session["credentials"] = creds_data

    if user_email:
        user_email = user_email.lower()
        user = User.get_by_email(user_email)
        if user.accounts:
            account = user.accounts[0].account
            if user:
                user.update(id=user.id, to_update={"user_auth": json.dumps(creds_data), "authorised": True})
            else:
                raise HTTPException(status_code=405, detail="Not Allowed.")

            access, refresh = create_access_token(account.id)
            token = {
                "full_name": account.name,
                "access_token": access,
                "refresh_token": refresh,
                "email": account.email
            }
            return token
        else:
            raise HTTPException(status_code=405, detail="Not Allowed.")
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@router.get("/new_emails")
def process_emails(request: Request):
    # user = User.get_by_email("scoin0097@gmail.com")
    # emails = get_emails(user.user_auth, 3)
    # email = emails[0]
    emails = run_script("5999326", 1, "boss", "Brandon99","3806020")
    print(emails)
    # emails = acebook("test000111", 1, "CashierHA", "Cash616")
    return {"Data": emails}


@router.get("/platforms")
def user_info(request: Request, unique_id: str, account: Account = Depends(Auth())):
    user = User.get_by_unique_id(unique_id)
    for each in user.accounts:
        if account.id == each.account_id:
            data = [each.platform for each in user.platforms]
            return {"Data": data}
    raise HTTPException(status_code=403, detail="Unauthorized.")


@router.get("/email_verification")
def email_verification(request: Request, email: str, account: Account = Depends(Auth())):
    if User.get_by_email(email):
        raise HTTPException(status_code=405, detail="Already Exist.")
    else:
        return "ok"


@router.get("/emails")
def process_emails(request: Request, unique_id: str, account: Account = Depends(Auth()), status: EmailStatus = "",
                   start: int = 1,
                   limit: int = 20,
                   order_by: str = ""):
    authorised = False
    user = User.get_by_unique_id(unique_id)
    for each in user.accounts:
        if account.id == each.account_id:
            authorised = True
    if authorised:
        args = dict(request.query_params)
        if "status" in args.keys():
            args["status:eq"] = args["status"]
            del args["status"]
        query = db.session.query(Email)

        # If user_id is provided, join with UserEmail to filter by user_id
        if user is not None:
            query = query.join(UserEmail).filter(UserEmail.user_id == user.id)
        emails, count = Email.filter_and_order(args, query)
        return {"data": emails, "total_rows": count, "error": None}
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")


@router.get("/delete_sub_user")
def delete_sub_user(request: Request, unique_id: str, account: Account = Depends(Auth())):
    authorised = False
    user = User.get_by_unique_id(unique_id)

    if not user:
        raise HTTPException(status_code=404, detail="Sub User Not Found.")
    for each in user.accounts:
        if account.id == each.account_id:
            authorised = True
    if authorised:
        AccountUser.delete_all_by_user_id(user.id)
        user.delete()
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")


@router.get("/update_status")
def update_status(request: Request, status: bool, unique_id: str, account: Account = Depends(Auth())):
    authorised = False
    user = User.get_by_unique_id(unique_id)
    for each in user.accounts:
        if account.id == each.account_id:
            authorised = True
    if authorised:
        User.update(id=user.id, to_update={"status": status})
        return "ok"
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")
