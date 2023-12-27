from typing import List,Optional

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
    authorised: bool
    email: str
    unique_id: str
    class Config:
        orm_mode = True

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import uuid

router = APIRouter()

# Define the Pydantic model for the request body
class CreateAccount(BaseModel):

    username: str
    password: str
class SignupRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    phone_number: str
class Account(BaseModel):
    name: str
    email: str
    username: str
    password: str
    phone_number: str
    unique_id : str
    is_email_authorised : Optional[bool]
class UserAccounts(BaseModel):
    #primary_user: UserBase
    user: UserBase
    class Config:
        orm_mode = True

class GetUser(UserBase):
    user_accounts: List[UserAccounts]

    class Config:
        orm_mode = True

class GetAccount(Account):
    users: List[UserAccounts]
    class Config:
        orm_mode = True