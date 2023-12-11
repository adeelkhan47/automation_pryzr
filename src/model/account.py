from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class Account(Base):
    __tablename__ = "account"
    email = Column(String, index=True, nullable=False, unique=True)
    username = Column(String, index=True, nullable=False, unique=True)
    status = Column(Boolean, default=True)
    phone_number = Column(String, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    unique_id = Column(String, index=True)
    is_email_authorised = Column(Boolean, default=False)
    users = relationship("AccountUser", back_populates="account")

    @classmethod
    def get_by_email(cls, email: str):
        row = db.session.query(cls).filter_by(email=email).first()
        return row

    @classmethod
    def get_by_username(cls, username: str):
        row = db.session.query(cls).filter_by(username=username).first()
        return row

    @classmethod
    def get_by_email_pass(cls, email: str, password: str):
        row = db.session.query(cls).filter_by(email=email, password=password).first()
        return row

    @classmethod
    def get_by_username_pass(cls, username: str, password: str):
        row = db.session.query(cls).filter_by(username=username, password=password).first()
        return row

    @classmethod
    def get_by_unique_id(cls, unique_id: str):
        row = db.session.query(cls).filter_by(unique_id=unique_id).first()
        return row
