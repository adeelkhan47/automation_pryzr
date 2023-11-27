from fastapi_sqlalchemy import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base



class UserAccount(Base):
    __tablename__ = "user_account"

    primary_user_id = Column(Integer, ForeignKey("user.id"))
    secondary_user_id = Column(Integer, ForeignKey("user.id"))

    primary_user = relationship(
        "User",
        foreign_keys=[primary_user_id],
        primaryjoin="UserAccount.primary_user_id == User.id",
        back_populates="user_accounts"
    )

    secondary_user = relationship(
        "User",
        foreign_keys=[secondary_user_id],
        primaryjoin="UserAccount.secondary_user_id == User.id",
        # back_populates="secondary_user"
    )

    @classmethod
    def delete_all_by_primary_user(cls, primary_user_id: int):
        db.session.query(cls).filter_by(primary_user_id=primary_user_id).delete(synchronize_session='fetch')

    @classmethod
    def delete_all_by_secondary_user_id(cls, secondary_user_id: int):
        db.session.query(cls).filter_by(secondary_user_id=secondary_user_id).delete(synchronize_session='fetch')