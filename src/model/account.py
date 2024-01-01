from datetime import datetime, timedelta

from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class Account(Base):
    __tablename__ = "account"

    username = Column(String, index=True, nullable=False, unique=True)
    status = Column(Boolean, default=True)
    phone_number = Column(String, nullable=False)
    password = Column(String, nullable=False)
    unique_id = Column(String, index=True)
    users = relationship("AccountUser", back_populates="account")
    platforms = relationship("AccountPlatform", back_populates="account")
    distributors = relationship("DistributorAccounts", back_populates="account")

    @property
    def credit_last_thirty(self):
        from . import Stats
        session = db.session
        current_time = datetime.now()

        # Subtract 5 days from the current time
        thirty_days = current_time - timedelta(days=30)

        # Query to get emails older than 5 days directly
        stats = session.query(Stats).filter(Stats.account_username == self.username).filter(Stats.created_at > thirty_days).all()
        value = 0
        for stat in stats:
            value += stat.amount
        return value

    @property
    def credit_last_seven(self):
        from . import Stats
        session = db.session
        current_time = datetime.now()

        # Subtract 5 days from the current time
        thirty_days = current_time - timedelta(days=7)

        # Query to get emails older than 5 days directly
        stats = session.query(Stats).filter(Stats.account_username == self.username).filter(
            Stats.created_at > thirty_days).all()
        value = 0
        for stat in stats:
            value += stat.amount
        return value

    @classmethod
    def get_by_username(cls, username: str):
        row = db.session.query(cls).filter_by(username=username).first()
        return row

    @classmethod
    def get_by_username_pass(cls, username: str, password: str):
        row = db.session.query(cls).filter_by(username=username, password=password).first()
        return row

    @classmethod
    def get_by_unique_id(cls, unique_id: str):
        row = db.session.query(cls).filter_by(unique_id=unique_id).first()
        return row
