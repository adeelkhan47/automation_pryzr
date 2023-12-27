import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request
from fastapi_sqlalchemy import db
from starlette.responses import RedirectResponse

from api.distributor.schemas import SignupRequest, CreateAccount
from common.enums import Platforms
from config import settings
from helpers.deps import DistAuth, Admin_Auth
from helpers.email_service import send_email
from helpers.jwt import create_access_token
from helpers.response import jinja2_env
from model import Account, Email, UserEmail, User, AccountUser
from model.distributor import Distributor
from model.distributor_accounts import DistributorAccounts

router = APIRouter()

@router.post("/get_distributors")
def get_accounts(request: Request, found: bool = Depends(Admin_Auth())):
    distributors, count = Distributor.filter_and_order({"start": 1, "limit": 200})
    data = {"distributors": distributors, "count": count}
    return data

@router.get("/get_distributor_stats")
def get_accounts(request: Request, account_unique_key: str, start_date: Optional[str] = None,
                 end_date: Optional[str] = None, found: bool = Depends(Admin_Auth())):
    args = {"start": 1, "limit": 200}

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + timedelta(days=1, minutes=-1)

        args = {"start": 1, "limit": 200, "created_at:gte": start_date, "created_at:lte": end_date}

    account = Account.get_by_unique_id(account_unique_key)
    if not account:
        raise HTTPException(status_code=404, detail="Not Found")

    data = []
    for each in account.users:
        inner_data = {}
        query = db.session.query(Email).filter(Email.status == "Successful")
        query = query.join(UserEmail, UserEmail.email_id == Email.id)
        query = query.join(User, User.id == UserEmail.user_id)  # Changed UserEmail.id to UserEmail.user_id
        query = query.filter(User.email == each.user.email)  # Filter by the user's email
        query = query.join(AccountUser, AccountUser.user_id == User.id)
        query = query.filter(AccountUser.account_id == account.id)
        emails, count = Email.filter_and_order(args, query)
        for platform in Platforms:
            inner_data[platform.value] = 0
        for email in emails:
            if "$" in email.amount and len(email.amount) >= 2:
                inner_data[email.platform] += int(email.amount[:-1])
        data.append({each.user.email: inner_data})
    return data
@router.post("/signup")
def signup(request_body: SignupRequest, request: Request):
    unique_id = uuid.uuid4().hex
    if Distributor.get_by_email(request_body.email):
        raise HTTPException(status_code=405, detail="Email Already Exists.")
    if Distributor.get_by_username(request_body.username):
        raise HTTPException(status_code=405, detail="Username Already Exists.")

    # Create the account
    distributor = Distributor(name=request_body.name, email=request_body.email, username=request_body.username,
                              status=True, phone_number=request_body.phone_number,
                              password=request_body.password, unique_id=unique_id, is_email_authorised=False)

    access, refresh = create_access_token(distributor.id)
    token = {
        "full_name": distributor.name,
        "access_token": access,
        "refresh_token": refresh,
        "email": distributor.email
    }
    template = jinja2_env.get_template("email_confirmation.html")
    send_email(
        distributor.email,
        "Autom8 Email Verification.",
        template.render(
            fullName=distributor.name,
            settings=settings,
            unique_id=distributor.unique_id,
        ),
    )
    distributor.insert()
    return token


@router.get("/login")
def login(email_or_username, password, request: Request):
    distributor = Distributor.get_by_email_pass(email_or_username, password)
    if not distributor:
        distributor = Distributor.get_by_username_pass(email_or_username, password)
        if not distributor:
            raise HTTPException(status_code=404, detail="Not Found.")

    access, refresh = create_access_token(distributor.id)
    token = {
        "full_name": distributor.name,
        "access_token": access,
        "refresh_token": refresh,
        "email": distributor.email
    }
    return token

@router.get("/confirm_email")
def confirm_email(unique_id: str):
    distributor = Distributor.get_by_unique_id(unique_id)
    if not distributor:
        raise HTTPException(status_code=404, detail="Not Found.")

    current_time = datetime.now(distributor.created_at.tzinfo)
    time_difference = current_time - distributor.created_at

    # Checking if the difference is greater than 15 minutes
    if time_difference > timedelta(days=7):
        raise HTTPException(status_code=404, detail="Expired Found.")
    Distributor.update(distributor.id, {"is_email_authorised": True})
    return RedirectResponse(f"{settings.FE_URL}/signin")


@router.post("/create_account")
def create_account(request_body: CreateAccount, request: Request, distributor: Distributor = Depends(DistAuth())):
    unique_id = uuid.uuid4().hex
    if Distributor.get_by_username(request_body.username):
        raise HTTPException(status_code=405, detail="Username Already Exists.")
    # Create the account
    account = Account(username=request_body.username,
                      status=True, phone_number="",
                      password=request_body.password, unique_id=unique_id)
    account.insert()
    temp = DistributorAccounts(distributor_id=distributor.id, account_id=account.id)
    temp.insert()
    return "ok"


@router.get("/delete_account")
def delete_account(unique_id, request: Request, distributor: Distributor = Depends(DistAuth())):
    account = Account.get_by_unique_id(unique_id)
    if not account:
        raise HTTPException(status_code=404, detail="Not found.")
    DistributorAccounts.delete_all_by_account_id(account.id)
    account.delete()
    return "ok"
