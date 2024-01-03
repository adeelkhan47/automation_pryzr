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

    @classmethod
    def get_user_email_by_distributor_id(cls, distributor_id: int):
        user_emails = db.session.query(cls.user_email) \
            .filter_by(distributor_id=distributor_id) \
            .group_by(cls.user_email) \
            .all()

        user_emails = [item[0] for item in user_emails]

        return user_emails

    @classmethod
    def get_account_usernames_by_distributor_id(cls, distributor_id: int):
        # Query the database for unique account usernames
        account_usernames = db.session.query(cls.account_username) \
            .filter_by(distributor_id=distributor_id) \
            .group_by(cls.account_username) \
            .all()
        account_usernames = [item[0] for item in account_usernames]

        return account_usernames
