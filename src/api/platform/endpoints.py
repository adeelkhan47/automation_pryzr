from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request

from common.enums import Platforms
from helpers.deps import Auth
from model import Platform, User, UserPlatform
from model.account import Account

router = APIRouter()


@router.post("/create")
def process_emails(request: Request, unique_id: str, platform: Platforms, username: str, password: str,
                   url_key: str = "",
                   account: Account = Depends(Auth())):
    if not account:
        raise HTTPException(status_code=400, detail="User Not Found.")

    authorised = False
    user = User.get_by_unique_id(unique_id)
    for each in user.accounts:
        if account.id == each.account_id:
            authorised = True
    if authorised:
        found = False
        user_platform_id = None
        for each in user.platforms:
            if each.platform.name == platform:
                found = True
                user_platform_id = each.id

        if found:
            user_platform = UserPlatform.get_by_id(user_platform_id)
            user_platform.delete()
        platform = Platform(name=platform, username=username, password=password, url_key=url_key)
        platform.insert()
        user_platform = UserPlatform(platform_id=platform.id, user_id=user.id)
        user_platform.insert()
        return {"Status": "Created", "error": None}
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")


@router.delete('/{id}')
def delete_platform(request: Request, unique_id, id: int, account: Account = Depends(Auth())):
    authorised = False
    user = User.get_by_unique_id(unique_id)
    user = User.get_by_unique_id(unique_id)
    for each in user.accounts:
        if account.id == each.account_id:
            authorised = True
    if authorised:
        user_platform = UserPlatform.get_platform_for_user(id, user.id)
        if not user_platform:
            raise HTTPException(status_code=404, detail="User Platform Not Found.")
        user_platform.delete()
        platform = Platform.get_by_id(id)
        platform.delete()
        return {"Status": "OK", "error": None}
    else:
        raise HTTPException(status_code=403, detail="Unauthorized.")
