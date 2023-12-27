from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    status: bool
    authorised: bool
    email: str
    unique_id: str

    class Config:
        orm_mode = True


class Account(BaseModel):
    username: str
    password: str
    phone_number: str
    unique_id: str


class UserAccounts(BaseModel):
    # primary_user: UserBase
    user: UserBase

    class Config:
        orm_mode = True


class GetUser(UserBase):
    user_accounts: List[UserAccounts]

    class Config:
        orm_mode = True


class AccountUsers(Account):
    users: List[UserAccounts]

    class Config:
        orm_mode = True


class GetAccounts(BaseModel):
    accounts: List[Account]
    count: int

    class Config:
        orm_mode = True
