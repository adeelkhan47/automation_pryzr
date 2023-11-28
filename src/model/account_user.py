from fastapi_sqlalchemy import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base



class AccountUser(Base):
    __tablename__ = "account_user"


    account_id = Column(Integer, ForeignKey("user.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="accounts")
    account = relationship("Account", back_populates="users")
    # primary_user = relationship(
    #     "User",
    #     foreign_keys=[primary_user_id],
    #     primaryjoin="UserAccount.primary_user_id == User.id",
    #     back_populates="user_accounts"
    # )
    #
    # secondary_user = relationship(
    #     "User",
    #     foreign_keys=[secondary_user_id],
    #     primaryjoin="UserAccount.secondary_user_id == User.id",
    #     # back_populates="secondary_user"
    # )
    #
    @classmethod
    def delete_all_by_user_id(cls, user_id: int):
        db.session.query(cls).filter_by(user_id=user_id).delete(synchronize_session='fetch')
    #
    # @classmethod
    # def delete_all_by_secondary_user_id(cls, secondary_user_id: int):
    #     db.session.query(cls).filter_by(secondary_user_id=secondary_user_id).delete(synchronize_session='fetch')