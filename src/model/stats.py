from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, Integer, ForeignKey

from .base import Base


class Stats(Base):
    __tablename__ = "stats"

    distributor_id = Column(Integer, ForeignKey("distributor.id"))
    account_username = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)

    @classmethod
    def get_by_distributor_id(cls, distributor_id: int):
        rows = db.session.query(cls).filter_by(distributor_id=distributor_id).all()
        return rows

    @classmethod
    def get_by_account_username(cls, account_username: int):
        rows = db.session.query(cls).filter_by(account_username=account_username).all()
        return rows

    @classmethod
    def get_by_distributor_id_account_username(cls, account_username: int, distributor_id: int):
        rows = db.session.query(cls).filter_by(distributor_id=distributor_id, account_username=account_username).all()
        return rows