from fastapi_sqlalchemy import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class AccountPlatform(Base):
    __tablename__ = "account_platform"

    account_id = Column(Integer, ForeignKey("account.id"))
    platform_id = Column(Integer, ForeignKey("platform.id"))

    account = relationship("Account", back_populates="platforms")
    platform = relationship("Platform", back_populates="accounts")

    @classmethod
    def get_platform_for_account(cls, platform_id, account_id):
        row = db.session.query(cls).filter_by(platform_id=platform_id, account_id=account_id).first()
        return row
