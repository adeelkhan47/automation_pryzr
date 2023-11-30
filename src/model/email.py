from fastapi_sqlalchemy import db
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base


class Email(Base):
    __tablename__ = "email"
    email_id = Column(String, index=True, unique=True, nullable=False)
    subject = Column(String(200))
    reason = Column(String(200))
    sender_email = Column(String)
    username = Column(String, default="")
    sender_name = Column(String)
    status = Column(String)
    platform = Column(String, default="")
    amount = Column(String, default="")
    users = relationship("UserEmail", back_populates="email")

    @classmethod
    def get_by_email_id(cls, email_id: str):
        with db():
            row = db.session.query(cls).filter_by(email_id=email_id).first()
        return row
