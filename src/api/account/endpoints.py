from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request
from fastapi_sqlalchemy import db

from api.account.schemas import GetAccounts
from common.enums import Platforms
from config import settings
from helpers.deps import Auth, Admin_Auth
from helpers.jwt import create_admin_access_token
from model import Email, User
from model.account import Account
from model.account_user import AccountUser
from model.user_emails import UserEmail
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()


@router.post("/get_accounts", response_model=GetAccounts)
def get_accounts(request: Request, found: bool = Depends(Admin_Auth())):
    accounts, count = Account.filter_and_order({"start": 1, "limit": 200})
    data = {"accounts": accounts, "count": count}
    return data


@router.get("/get_agents_stats")
def get_accounts(request: Request, account_unique_key: str, start_date: Optional[str] = None,
                 end_date: Optional[str] = None, found: bool = Depends(Admin_Auth())):
    args = {{"start": 1, "limit": 200}}

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + timedelta(days=1, minutes=-1)

        args = {"start": 1, "limit": 200,"created_at:gte": start_date, "created_at:lte": end_date}

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
            inner_data[email.platform] += int(email.amount)
        data.append({each.user.email: inner_data})
    return data


@router.get("/admin_secret")
def admin_secret(secret_key, request: Request):
    if secret_key == settings.admin_secret_key:
        access, refresh = create_admin_access_token(secret_key)
        token = {
            "access_token": access
        }
        return token
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")
