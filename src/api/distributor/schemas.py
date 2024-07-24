from typing import List, Optional

from pydantic import BaseModel


class CreateAccount(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    phone_number: str


class Distributor(BaseModel):
    username: str
    email: str
    #password: str
    phone_number: str
    unique_id: str
    status: bool
    is_email_authorised: bool

    class Config:
        orm_mode = True


class Account(BaseModel):
    username: str
   # password: str
    status: bool
    phone_number: str
    unique_id: str
    credit_last_seven : int
    credit_last_thirty : int

    class Config:
        orm_mode = True


class SubAccount(BaseModel):
    account: Account

    class Config:
        orm_mode = True


class DistAccounts(Distributor):
    accounts: List[SubAccount]

    class Config:
        orm_mode = True


class GetDistributor(BaseModel):
    distributors: List[DistAccounts]
    count: int

    class Config:
        orm_mode = True
