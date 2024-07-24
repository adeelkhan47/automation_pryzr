from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request

from api.account.schemas import GetAccounts
from common.enums import Platforms
from config import settings
from helpers.deps import DistAuth, Auth
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
    distributor_id = account.distributors[0].distributor_id
    user_emails = Stats.get_user_email_by_distributor_id(distributor_id)
    data = []
    # users = [each.user for each in account.users]
    for email in user_emails:
        inner_data = {}
        for platform in Platforms:
            inner_data[platform.value] = 0
            if date:
                args = {"account_username:eq": account.username, "user_email:eq": email, "start": 1, "limit": 1000,
                        "created_at:gte": start_date, "created_at:lte": end_date, "platform:eq": platform.value}
            else:
                args = {"account_username:eq": account.username, "user_email:eq": email, "start": 1, "limit": 1000,
                        "platform:eq": platform.value}
            stats, _ = Stats.filter_and_order(args)
            for stat in stats:
                inner_data[platform.value] += stat.amount
        data.append({email: inner_data})
    return data
