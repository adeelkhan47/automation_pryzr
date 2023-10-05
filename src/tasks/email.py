import logging
from datetime import datetime

import pytz
from googleapiclient.discovery import build

from common.enums import EmailAccountStatus, EmailStatus, QueueStatus
from conf import settings
from helpers.gmail import (
    ensure_mailwall_label,
    generate_whitelist_from_contacts,
    generate_whitelist_from_received_mails,
    generate_whitelist_from_sent_mails,
    get_emails,
    move_email_to_blocked,
    whitelist_match,
)
from helpers.transaction import is_balance_enough
from model.email import Email
from model.email_account import EmailAccount
from model.queue import Queue
from model.whitelist import Whitelist
from service.redis import (
    get_last_email_sync,
    get_last_whitelist_sync,
    set_last_email_sync,
    set_last_whitelist_sync,
)
from tasks.celery import DbTask, celery_app

logger = logging.getLogger(__file__)


@celery_app.task(bind=True, base=DbTask)
def fetch_new(self, *args, **kwargs):
    session = self.session
    email_accounts = (
        session.query(EmailAccount)
        .filter(EmailAccount.status == EmailAccountStatus.CONFIRMED)
        .all()
    )
    updated_sync = int(datetime.now(pytz.UTC).timestamp())
    last_sync = int(get_last_email_sync()) - settings.SYNC_TIME_SUBTRACT
    for account in email_accounts:
        cred = account.gmail_cred(session)
        logging.info(f"* Process started for {account.email}")
        if not cred:
            logging.info(f"Skipping {account.email} due to credentials")
            continue
        service = build("gmail", "v1", credentials=cred)
        mailwall_label = ensure_mailwall_label(service)
        emails = get_emails(service, last_sync)
        whitelist = (
            session.query(Whitelist)
            .filter_by(user_id=account.user_id, status="1")
            .all()
        )
        whitelist_rules = account.user.whitelisting_rules
        email_code = account.user.price_configs.free_email_code
        for email in emails:
            is_whitelisted = False
            logging.info(f"* Process started for {email['subject']}")
            if not account.user.mailwall_status:
                logging.info(f"Skipping {account.email} (mailwall off)")
                is_whitelisted = True
            self_account = EmailAccount.get_by_email(email["sender"], session)
            if self_account and self_account.user_id == account.user_id:
                logging.info("Sent to self, skip")
                continue
            thread_old_email = (
                session.query(Email)
                .filter_by(
                    to=account.email,
                    thread_id=email["thread_id"],
                    status=EmailStatus.PAID,
                )
                .first()
            )
            if thread_old_email:
                logging.info("Already paid, skip")
                continue
            already_processed = Email.get_received_by_message_id(
                account.email, email["id"], session
            )
            if already_processed:
                logging.info("Already processed, skip")
                continue
            for item in whitelist:
                # User disabled whitelisting for all items with X reason, don't try
                if not whitelist_rules.is_allowed(item.reason):
                    continue
                match, reason = whitelist_match(item.key, item.type, email["sender"])
                if match:
                    is_whitelisted = True
                    logging.info(f"Whitelist filter {reason} {item.key} matched")
                    break
            if email["sender"] in settings.WHITELIST:
                is_whitelisted = True
                logging.info(f"Built-in whitelist {item.key} matched")
            if email_code and email_code in email["subject"]:
                is_whitelisted = True
                logging.info(f"'{email_code}' email code matched {email['subject']}")
            receiver_name = f"{account.user.first_name} {account.user.last_name}"
            receiver_name = (
                receiver_name
                if account.user.first_name
                else account.email.split("@")[0]
            )
            email_dict = {
                "to_name": receiver_name,
                "to": account.email,
                "from_name": email["sender_name"],
                "from_address": email["sender"],
                "subject": email["subject"][:255],
                "message_id": email["id"],
                "r_message_id": email["message_id"],
                "thread_id": email["thread_id"],
                "email_account_id": account.id,
            }
            if not is_whitelisted:
                sender_account = EmailAccount.get_by_email(email["sender"], session)
                receiver_thr = account.user.price_configs.price_for_receiving
                move_email_to_blocked(
                    service, email["thread_id"], mailwall_label, False
                )
                if sender_account:
                    sender_thr = sender_account.user.price_configs.autopay_threshold
                    if sender_thr >= receiver_thr:
                        email_obj = Email(
                            **email_dict, status=EmailStatus.PROCESSING.value
                        ).insert(session)
                        if is_balance_enough(
                            sender_account.user.id, receiver_thr, session
                        ):
                            queue_status = QueueStatus.AUTHORIZED.value
                        else:
                            queue_status = QueueStatus.INSUFFICIENT_BALANCE.value
                        logging.info("Mailwall, asked to payment queue")
                    else:
                        email_obj = Email(
                            **email_dict, status=EmailStatus.BLOCKED.value
                        ).insert(session)
                        queue_status = QueueStatus.UNAUTHORIZED.value
                        logging.info("Mailwall, unable to match amount, authorize")
                else:
                    email_obj = Email(
                        **email_dict, status=EmailStatus.BLOCKED.value
                    ).insert(session)
                    logging.info("Mailwall, prevented email, no account")
                    queue_status = QueueStatus.SIGNUP_REQUIRED.value
                from_user_id = sender_account.user.id if sender_account else None
                Queue(
                    email_id=email_obj.id,
                    status=queue_status,
                    to_user_id=account.user.id,
                    from_user_id=from_user_id,
                    amount=receiver_thr,
                ).insert(session)
            else:
                Email(**email_dict, status=EmailStatus.WHITELISTED.value).insert(
                    session
                )

    set_last_email_sync(updated_sync)
    logging.info(f"Mailwall, last email synced on {updated_sync}")


@celery_app.task(bind=True, base=DbTask)
def sync_whitelist(self, *args, **kwargs):
    session = self.session
    email_accounts = (
        session.query(EmailAccount)
        .filter(EmailAccount.status == EmailAccountStatus.CONFIRMED)
        .all()
    )
    updated_sync = int(datetime.now(pytz.UTC).timestamp())
    last_sync = int(get_last_whitelist_sync()) - settings.SYNC_TIME_SUBTRACT
    for account in email_accounts:
        credentials = account.gmail_cred(session)
        if not credentials:
            logging.info(f"Skipping {account.email} due to credentials")
            continue
        generate_whitelist_from_sent_mails(
            session,
            credentials,
            account.id,
            last_sync,
            settings.WHITELIST_SCAN_COUNT_BACKGROUND,
        )
        generate_whitelist_from_received_mails(
            session,
            credentials,
            account.id,
            last_sync,
            settings.WHITELIST_SCAN_COUNT_BACKGROUND,
        )
        generate_whitelist_from_contacts(session, credentials, account.id)
    set_last_whitelist_sync(updated_sync)
    logging.info(f"Mailwall, last whitelist synced on {updated_sync}")
