import json
import logging
import os
import uuid

import requests
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from fastapi_sqlalchemy import db
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse

from api.user.schemas import GetUser
from common.enums import EmailStatus
from config import settings
from helpers.deps import Auth
from helpers.jwt import create_access_token
from platform_scripts.gamevault import run_script
from model import Email, UserEmail, UserAccount
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


@router.get("/get_user", response_model=GetUser)
def get_user(request: Request, user: User = Depends(Auth())):
    if user:
        return user
    raise HTTPException(status_code=404, detail="Not Found")


@router.get("/login")
def login(request: Request):
    flow = get_google_oauth2_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        approval_prompt='force',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)


@router.get("/secondary_login")
# def secondary_login(request: Request, email: str, user: User = Depends(Auth())):
def secondary_login(request: Request, email: str):
    my_user = User.get_by_email("mmadikhan1998@gmail.com")

    unique_id = uuid.uuid4().hex
    if User.get_by_email(email):
        raise HTTPException(status_code=405, detail="Already Exist.")
    user = User(email=email, user_auth={}, status=True, is_primary=False, authorised=False, primary_email=my_user.email,
                unique_id=str(unique_id))
    user.insert()
    flow = get_google_oauth2_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        approval_prompt='force',
        include_granted_scopes='true'
    )
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
        print(user_email)
        user = User.get_by_email(user_email)
        if user:
            user.update(id=user.id, to_update={"user_auth": json.dumps(creds_data)})
        else:
            unique_id = uuid.uuid4().hex
            user = User(
                email=user_email,
                user_auth=json.dumps(creds_data),
                status=True,
                is_primary=True,
                authorised=True,
                primary_email=user_email,
                unique_id=str(unique_id)

            )
            user.insert()
        if not user.is_primary and user.authorised:
            raise HTTPException(status_code=405, detail="Not Allowed.")
        if not user.is_primary and not user.authorised:
            user.update(id=user.id, to_update={"authorised": True})
            primary_user = User.get_by_email(user.primary_email)
            user_account = UserAccount(primary_user_id=primary_user.id, secondary_user_id=user.id)
            user_account.insert()
            return "authorised"
        access, refresh = create_access_token(user.id)
        token = {
            "full_name": user_full_name,
            "access_token": access,
            "refresh_token": refresh,
            "email": user.email
        }
        return token
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@router.get("/new_emails")
def process_emails(request: Request):
    # emails = vblink("test000111",1,"justest","justest1")
    # emails = orionstar("Test111_",1,"KingsofvOR","Admin8913")
    # emails = juwa("_test000111",1,"KingsofvaJW","Vite837")

    # emails = kirin("Test000_", 1, "fiverr333", "fiverr333")
    emails = run_script("test000111", 1, "KingsofvaGV", "Life726")
    print(emails)
    # emails = acebook("test000111", 1, "CashierHA", "Cash616")
    return {"Data": emails}


@router.get("/platforms")
def user_info(request: Request, unique_id: str, user: User = Depends(Auth())):
    sub_user = User.get_by_unique_id(unique_id)
    if sub_user.id == user.id:
        data = [each.platform for each in user.platforms]
        return {"Data": data}
    for each in user.user_accounts:
        if sub_user.id == each.secondary_user_id:
            data = [each.platform for each in sub_user.platforms]
            return {"Data": data}
    raise HTTPException(status_code=403, detail="Unauthorized.")


# @router.get("/new_emails")
# def process_emails(request: Request):
#     taichi("kelso919", 1)
#     return {"Data": "emails"}


@router.get("/emails")
def process_emails(request: Request, unique_id: str, user: User = Depends(Auth()), status: EmailStatus = "",
                   start: int = 1,
                   limit: int = 20,
                   order_by: str = ""):
    authorised = False
    sub_user = User.get_by_unique_id(unique_id)
    if sub_user.id == user.id:
        authorised = True
    else:
        for each in user.user_accounts:
            if sub_user.id == each.secondary_user_id:
                authorised = True
    if authorised:
        args = dict(request.query_params)
        if "status" in args.keys():
            args["status:eq"] = args["status"]
            del args["status"]
        # if user is not None:
        #     args["user_id:eq"] = user.id

        query = db.session.query(Email)

        # If user_id is provided, join with UserEmail to filter by user_id
        if user is not None:
            query = query.join(UserEmail).filter(UserEmail.user_id == sub_user.id)
        emails, count = Email.filter_and_order(args, query)
        return {"data": emails, "total_rows": count, "error": None}
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")


@router.get("/set_primary")
def set_primary_user(request: Request, unique_id: str, user: User = Depends(Auth())):
    new_accounts = []
    new_accounts.append(user.id)

    authorised = False
    sub_user = User.get_by_unique_id(unique_id)
    if sub_user.id == user.id:
        authorised = True
    else:
        for each in user.user_accounts:
            if sub_user.id == each.secondary_user_id:
                authorised = True
            else:
                new_accounts.append(each.secondary_user_id)
    if authorised:

        User.update(id=user.id, to_update={"is_primary": False, "primary_email": sub_user.email})
        User.update(id=sub_user.id, to_update={"is_primary": True, "primary_email": sub_user.email})

        UserAccount.delete_all_by_primary_user(user.id)
        for each in new_accounts:
            user_account = UserAccount(primary_user_id=sub_user.id, secondary_user_id=each)
            user_account.insert()
        access, refresh = create_access_token(sub_user.id)
        token = {
            "access_token": access,
            "refresh_token": refresh,
            "email": user.email
        }
        return token
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")


@router.get("/delete_sub_user")
def delete_sub_user(request: Request, unique_id: str, user: User = Depends(Auth())):
    authorised = False
    sub_user = User.get_by_unique_id(unique_id)
    if sub_user.id == user.id:
        raise HTTPException(status_code=405, detail="Not Allowed.")
    else:
        for each in user.user_accounts:
            if sub_user.id == each.secondary_user_id:
                authorised = True
    if authorised:
        UserAccount.delete_all_by_secondary_user_id(sub_user.id)
        sub_user.delete()
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")


@router.get("/update_status")
def update_status(request: Request, status: bool, unique_id: str,user: User = Depends(Auth())):
    authorised = False
    sub_user = User.get_by_unique_id(unique_id)
    if sub_user.id == user.id:
        authorised = True
    else:
        for each in user.user_accounts:
            if sub_user.id == each.secondary_user_id:
                authorised = True
    if authorised:
        User.update(id=sub_user.id, to_update={"status": status})
        return "ok"
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")

