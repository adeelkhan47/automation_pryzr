from fastapi_sqlalchemy import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class UserPlatform(Base):
    __tablename__ = "user_platform"

    user_id = Column(Integer, ForeignKey("user.id"))
    platform_id = Column(Integer, ForeignKey("platform.id"))

    user = relationship("User", back_populates="platforms")
    platform = relationship("Platform", back_populates="users")

    @classmethod
    def get_platform_for_user(cls, platform_id, user_id):
        row = db.session.query(cls).filter_by(platform_id=platform_id, user_id=user_id).first()
        return row
