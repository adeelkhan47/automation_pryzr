import json
import os
import uuid

import requests
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from fastapi_sqlalchemy import db
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse

from api.user.schemas import GetAccount
from common.enums import EmailStatus
from config import settings
from helpers.call_platform import run_platform
from helpers.deps import Auth
from helpers.jwt import create_access_token
from model import Email, UserEmail, AccountUser
from model.account import Account
from model.user import User
from platform_scripts.dragonworld import run_script

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
    # emails = run_script("5999326", 1, "boss", "Brandon99",3806020)
    emails = run_script("test1231234", 1, "TropicGamersDW", "TropicGamersDW")
    # print(emails)
    # emails = acebook("test000111", 1, "CashierHA", "Cash616")
    # session = db.session
    # accounts = session.query(Account).all()
    # for account in accounts:
    #     account_user = [temp.user for temp in account.users]
    #     for each in account_user:
    #         logging.info(f"{each.email}")
    #         emails = get_emails(each.user_auth, 20)
    return {"Data": emails[0]}


@router.get("/platforms")
def user_info(request: Request, account: Account = Depends(Auth())):
    data = [each.platform for each in account.platforms]
    return {"Data": data}


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


@router.get("/retry_email")
def retry_email(request: Request,email_id: str, account: Account = Depends(Auth())):
    email = Email.get_by_email_id(email_id)
    if email:
        if email.status == EmailStatus.Failed.value:
            #result, reason, platform = run_platform("", account, email.username, email.amount[:-1], email.platform)
            result = True
            if result:
                Email.update(id=email.id, to_update={"status": EmailStatus.Successful.value})
                return "ok"
        else:
            raise HTTPException(status_code=403, detail="Not applicable.")
    else:
        raise HTTPException(status_code=404, detail="Not Found.")


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
