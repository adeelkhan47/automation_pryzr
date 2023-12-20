from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request

from common.enums import Platforms
from helpers.deps import Auth
from model import Platform, User, AccountPlatform
from model.account import Account

router = APIRouter()


@router.post("/create")
def process_emails(request: Request, platform: Platforms, username: str, password: str,
                   url_key: str = "",
                   account: Account = Depends(Auth())):
    found = False
    account_platform_id = None
    for each in account.platforms:
        if each.platform.name == platform:
            found = True
            account_platform_id = each.id

    if found and account_platform_id:
        account_platform = AccountPlatform.get_by_id(account_platform_id)
        account_platform.delete()
    platform = Platform(name=platform, username=username, password=password, url_key=url_key)
    platform.insert()
    account_platform = AccountPlatform(platform_id=platform.id, account_id=account.id)
    account_platform.insert()
    return {"Status": "Created", "error": None}


@router.delete('/{id}')
def delete_platform(request: Request, id: int, account: Account = Depends(Auth())):
    account_platform = AccountPlatform.get_platform_for_account(id, account.id)
    if not account_platform:
        raise HTTPException(status_code=404, detail="Account Platform Not Found.")
    account_platform.delete()
    platform = Platform.get_by_id(id)
    platform.delete()
    return {"Status": "OK", "error": None}
