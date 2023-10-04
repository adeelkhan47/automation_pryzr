from pydantic import BaseModel


class SubscriptionBase(BaseModel):
    name: str
    price: float
    description: str = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(SubscriptionBase):
    pass


class SubscriptionInDBBase(SubscriptionBase):
    id: int

    class Config:
        orm_mode = True


class Subscription(SubscriptionInDBBase):
    pass
