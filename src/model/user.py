from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "user"
    email = Column(String, index=True, nullable=False, unique=True)
    user_auth = Column(JSON, nullable=True)
    status = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    authorised = Column(Boolean, default=False)
    primary_email = Column(String, index=True)
    unique_id = Column(String, index=True)
    # primary_user = relationship("UserAccount", back_populates="user")
    # secondary_user = relationship("UserAccount", back_populates="user")
    user_accounts = relationship(
        "UserAccount",
        primaryjoin="User.id == UserAccount.primary_user_id",
        back_populates="primary_user"
    )

    # secondary_user = relationship(
    #     "UserAccount",
    #     primaryjoin="User.id == UserAccount.secondary_user_id",
    #     back_populates="secondary_user"
    # )
    emails = relationship("UserEmail", back_populates="user")
    platforms = relationship("UserPlatform", back_populates="user")

    @classmethod
    def get_by_email(cls, email: str):
        row = db.session.query(cls).filter_by(email=email).first()
        return row

    @classmethod
    def get_by_unique_id(cls, unique_id: str):
        row = db.session.query(cls).filter_by(unique_id=unique_id).first()
        return row

