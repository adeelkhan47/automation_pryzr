from fastapi import APIRouter, HTTPException, Depends
from fastapi import Request

from common.enums import Platforms
from helpers.deps import Auth
from model import Platform, User, UserPlatform

router = APIRouter()


@router.post("/create")
def process_emails(request: Request, platform: Platforms, username: str, password: str,
                   user: User = Depends(Auth())):
    if not user:
        raise HTTPException(status_code=400, detail="User Not Found.")

    # platform = Platform.get_by_name(platform)
    # if not platform:
    #     raise HTTPException(status_code=400, detail="Platform Not Found.")
    found = False
    user_platform_id = None
    for each in user.platforms:
        if each.platform.name == platform:
            found = True
            user_platform_id = each.id

    if found:
        user_platform = UserPlatform.get_by_id(user_platform_id)
        user_platform.delete()
    platform = Platform(name=platform, username=username, password=password)
    platform.insert()
    user_platform = UserPlatform(platform_id=platform.id, user_id=user.id)
    user_platform.insert()
    return {"Status": "Created", "error": None}


@router.delete('/{id}')
def delete_platform(request: Request, id: int, user: User = Depends(Auth())):
    user_platform = UserPlatform.get_platform_for_user(id, user.id)
    if not user_platform:
        raise HTTPException(status_code=400, detail="User Platform Not Found.")
    user_platform.delete()
    platform = Platform.get_by_id(id)
    platform.delete()
    return {"Status": "OK", "error": None}
