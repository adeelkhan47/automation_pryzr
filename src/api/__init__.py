from fastapi import APIRouter

from .platform import endpoints as platform_endpoints
from .user import endpoints as user_endpoints
from .account import endpoints as account_endpoints
from .distributor import endpoints as distributor_endpoints

api_router = APIRouter()

api_router.include_router(
    user_endpoints.router, prefix="/user", tags=["User"],
)
api_router.include_router(
    platform_endpoints.router, prefix="/platform", tags=["Platform"]
)
api_router.include_router(
    account_endpoints.router, prefix="/account", tags=["Account"]
)

api_router.include_router(
    distributor_endpoints.router, prefix="/distributor", tags=["Distributor"]
)