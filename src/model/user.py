from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "user"
    email = Column(String, index=True, nullable=False, unique=True)
    user_auth = Column(JSON, nullable=True)
    status = Column(Boolean, default=True)
    emails = relationship("UserEmail", back_populates="user")
    platforms = relationship("UserPlatform", back_populates="user")

    @classmethod
    def get_by_email(cls, email: str):
        row = db.session.query(cls).filter_by(email=email).first()
        return row
