from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi_sqlalchemy import db

from api.account.schemas import GetAccounts
from common.enums import Platforms
from model import Email, User
from model.account import Account
from model.account_user import AccountUser
from model.user_emails import UserEmail

router = APIRouter()


@router.post("/get_accounts", response_model=GetAccounts)
def get_accounts(request: Request, secret_key: str):
    accounts, count = Account.filter_and_order({})
    data = {"accounts": accounts, "count": count}
    return data


@router.get("/get_accounts")
def get_accounts(request: Request, account_unique_key: str):
    account = Account.get_by_unique_id(account_unique_key)
    if not account:
        raise HTTPException(status_code=404, detail="Not Found")
    args = {}
    data = {}
    for each in account.users:
        print(each.user.email)
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
        data[each.user.email] = inner_data
    return data
