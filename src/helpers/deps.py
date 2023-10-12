from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from helpers.jwt import decode_token
from helpers.response import error
from model.user import User


class Auth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(Auth, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(Auth, self).__call__(
            request
        )
        if credentials:
            if not credentials.scheme == "Bearer":
                raise error("Invalid authentication scheme.", code=403)
            user_id, message = decode_token(credentials.credentials)
            if user_id is None:
                raise error(message, code=401)
            user = User.get_by_id(user_id)
            if not user:
                raise error("User not found", code=401)
            return user
        raise error("Invalid authorization code.", code=401)
