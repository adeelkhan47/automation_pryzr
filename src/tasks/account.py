import logging
from datetime import datetime, timedelta

from datetime import timezone

import math

from common.enums import EmailStatus
from helpers.call_platform import run_platform
from helpers.common import get_emails
from model import Email
from model.user import User
from model.user_emails import UserEmail
from tasks.celery import DbTask, celery_app

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


@celery_app.task(bind=True, base=DbTask)
def process_unauthorized_accounts(self, *args, **kwargs):
    session = self.session
    users = session.query(User).filter_by(authorised=False).all()

    for user in users:
        try:
            current_time = datetime.now(user.created_at.tzinfo)
            time_difference = current_time - user.created_at
            # Calculating the difference
            time_difference = current_time - user.created_at

            # Checking if the difference is greater than 15 minutes
            if time_difference > timedelta(minutes=10):
                session.query(User).filter_by(id=user.id).first().delete()
                session.commit()
        except Exception as e:
            logging.error(f"Account -> {user.email} Failed.")
