from fastapi_sqlalchemy import db
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base


class Platform(Base):
    __tablename__ = "platform"
    name = Column(String, index=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    url_key = Column(String, nullable=True,default="")
    users = relationship("UserPlatform", back_populates="platform")

    @classmethod
    def get_by_name(cls, name: str):
        with db():
            row = db.session.query(cls).filter_by(name=name).first()
        return row
