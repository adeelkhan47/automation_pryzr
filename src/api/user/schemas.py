from typing import List

from pydantic import BaseModel


# class TempUser(BaseModel):
#     id: int
#     status: bool
#     is_primary: bool
#     authorised: bool
#     email: str
#     unique_id: str
#     class Config:
#         orm_mode = True
class UserBase(BaseModel):
    id: int
    status: bool
    is_primary: bool
    authorised: bool
    email: str
    primary_email: str
    unique_id: str
    class Config:
        orm_mode = True


class UserAccounts(BaseModel):
    primary_user: UserBase
    secondary_user: UserBase
    class Config:
        orm_mode = True

class GetUser(UserBase):
    user_accounts: List[UserAccounts]

    class Config:
        orm_mode = True