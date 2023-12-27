from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request

from api.account.schemas import GetAccounts
from common.enums import Platforms
from config import settings
from helpers.deps import DistAuth
from helpers.jwt import create_admin_access_token, create_access_token
from model import Distributor
from model.account import Account
from model.stats import Stats

router = APIRouter()


@router.get("/get_accounts", response_model=GetAccounts)
def get_accounts(request: Request, distributor: Distributor = Depends(DistAuth())):
    accounts = [each.account for each in distributor.accounts]
    return {"accounts": accounts, "count": len(accounts)}


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


@router.get("/login")
def login(username, password, request: Request):
    account = Account.get_by_username_pass(username, password)
    if not account:
        raise HTTPException(status_code=404, detail="Not Found.")
    access, refresh = create_access_token(account.id)
    token = {
        "access_token": access,
        "refresh_token": refresh,
    }
    return token


@router.get("/get_account_stats")
def get_accounts(request: Request, account_unique_key: str, start_date: Optional[str] = None,
                 end_date: Optional[str] = None, found: bool = Depends(DistAuth())):
    date = False
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + timedelta(days=1, minutes=-1)
        date = True

    account = Account.get_by_unique_id(account_unique_key)
    if not account:
        raise HTTPException(status_code=404, detail="Not Found")

    data = []
    users = [each.user for each in account.users]
    for user in users:
        inner_data = {}
        for platform in Platforms:
            if date:
                args = {"account_username:eq": account.username, "user_email:eq": user.email, "start": 1, "limit": 1000,
                        "created_at:gte": start_date, "created_at:lte": end_date, "platform:eq": platform.value}
            else:
                args = {"account_username:eq": account.username, "user_email:eq": user.email, "start": 1, "limit": 1000,
                        "platform:eq": platform.value}
            stats, _ = Stats.filter_and_order(args)
            for stat in stats:
                inner_data[platform.value] += stat.amount
        data.append({user.email: inner_data})

    #
    # account = Account.get_by_unique_id(account_unique_key)

    #
    # data = []
    # for each in account.users:
    #     inner_data = {}
    #     query = db.session.query(Email).filter(Email.status == "Successful")
    #     query = query.join(UserEmail, UserEmail.email_id == Email.id)
    #     query = query.join(User, User.id == UserEmail.user_id)  # Changed UserEmail.id to UserEmail.user_id
    #     query = query.filter(User.email == each.user.email)  # Filter by the user's email
    #     query = query.join(AccountUser, AccountUser.user_id == User.id)
    #     query = query.filter(AccountUser.account_id == account.id)
    #     emails, count = Email.filter_and_order(args, query)
    #     for platform in Platforms:
    #         inner_data[platform.value] = 0
    #     for email in emails:
    #         if "$" in email.amount and len(email.amount) >= 2:
    #             inner_data[email.platform] += int(email.amount[:-1])
    #     data.append({each.user.email: inner_data})
    data = {}
    return data
