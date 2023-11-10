import logging

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
def process_new(self, *args, **kwargs):
    session = self.session
    email_accounts = session.query(User).filter_by(status=True).all()
    for each in email_accounts:
        try:
            logging.info(f"{each.email}")
            emails = get_emails(each.user_auth, 20)
            for email in emails:
                subject = email["subject"]
                sender_email = email["sender"]
                existing_email = session.query(Email).filter_by(email_id=email["email_id"]).first()
                reason = ""
                try:
                    if not existing_email and sender_email != each.email:
                        status = EmailStatus.Skipped.value
                        if "cash@square.com" == sender_email:
                            platform = ""
                            subject_ele = subject.split(" ")
                            subject_platform = subject_ele[len(subject_ele) - 1]
                            user_name = subject_ele[len(subject_ele) - 2]
                            amount = None
                            for each_subject_ele in subject_ele:
                                if "$" in each_subject_ele:
                                    amount = each_subject_ele.replace("$", "")
                                    amount = math.floor(float(amount))
                            result, reason, platform = run_platform(subject_platform, each, user_name, amount)
                            if result:
                                status = EmailStatus.Successful.value
                        else:
                            reason = "Not Related to CashApp"
                            status = EmailStatus.Skipped.value
                        new_email = Email(
                            email_id=email["email_id"],
                            subject=email["subject"],
                            sender_email=email["sender"],
                            sender_name=email["sender_name"],
                            status=status,
                            reason=reason,
                            platform=platform
                        )
                        session.add(new_email)
                        session.commit()
                        user_email = UserEmail(user_id=each.id, email_id=new_email.id)
                        session.add(user_email)
                        session.commit()
                        logging.error(f"{each.email} Success.")
                except Exception as e:
                    logging.exception(e)
                    new_email = Email(
                        email_id=email["email_id"],
                        subject=email["subject"],
                        sender_email=email["sender"],
                        sender_name=email["sender_name"],
                        status=EmailStatus.Failed.value,
                        reason="Internal Server Error.",
                        platform=""
                    )
                    session.add(new_email)
                    session.commit()
                    user_email = UserEmail(user_id=each.id, email_id=new_email.id)
                    session.add(user_email)
                    session.commit()
        except Exception as e:
            logging.error(f"{each.email} Failed.")
