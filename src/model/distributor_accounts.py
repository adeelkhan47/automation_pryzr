from fastapi_sqlalchemy import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base



class DistributorAccounts(Base):
    __tablename__ = "distributor_accounts"

    distributor_id = Column(Integer, ForeignKey("distributor.id"))
    account_id = Column(Integer, ForeignKey("account.id"))

    distributor = relationship("Distributor", back_populates="accounts")
    account = relationship("Account", back_populates="distributors")

    @classmethod
    def delete_all_by_account_id(cls, account_id: int):
        db.session.query(cls).filter_by(account_id=account_id).delete(synchronize_session='fetch')
