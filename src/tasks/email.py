import logging

from common.enums import EmailStatus
from helpers.common import get_emails
from model import Email
from model.user import User
from tasks.celery import DbTask, celery_app

logger = logging.getLogger(__file__)


@celery_app.task(bind=True, base=DbTask)
def process_new(self, *args, **kwargs):
    session = self.session
    email_accounts = session.query(User).all()
    for each in email_accounts:
        emails = get_emails(each.user_auth, 3)
        for email in emails:
            subject = email["subject"]
            existing_email = session.query(Email).filter_by(email_id=email["email_id"]).first()
            reason = ""
            try:
                if not existing_email:

                    status = EmailStatus.Skipped.value
                    # If it doesn't exist, create a new record
                    if "cashapp" not in subject.lower():
                        reason = "Not Related to CashApp"
                        new_email = Email(
                            email_id=email["email_id"],
                            subject=email["subject"],
                            sender_email=email["sender"],
                            sender_name=email["sender_name"],
                            status=EmailStatus.Skipped.value,
                            reason=reason
                        )
                    else:
                        new_email = Email(
                            email_id=email["email_id"],
                            subject=email["subject"],
                            sender_email=email["sender"],
                            sender_name=email["sender_name"],
                            status=EmailStatus.Successful.value,
                            reason=reason
                        )

                    session.add(new_email)
            except Exception as e:
                logging.exception(e)
                new_email = Email(
                    email_id=email["email_id"],
                    subject=email["subject"],
                    sender_email=email["sender"],
                    sender_name=email["sender_name"],
                    status=EmailStatus.Failed.value,
                    reason="Internal Server Error."
                )
                session.add(new_email)
            session.commit()
