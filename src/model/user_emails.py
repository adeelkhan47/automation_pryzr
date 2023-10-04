from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class UserEmail(Base):
    __tablename__ = "user_email"

    user_id = Column(Integer, ForeignKey("user.id"))
    email_id = Column(Integer, ForeignKey("email.id"))

    user = relationship("User", back_populates="emails")
    email = relationship("Email", back_populates="users")