import logging

from common.enums import EmailStatus, Platforms
from helpers.common import get_emails
from helpers.platform import taichi, kirin, vblink
from model import Email
from model.user import User
from model.user_emails import UserEmail
from tasks.celery import DbTask, celery_app

logger = logging.getLogger(__file__)


@celery_app.task(bind=True, base=DbTask)
def process_new(self, *args, **kwargs):
    res = vblink("test000111", 1, "justest", "justest1")
    logging.error(res)

    # session = self.session
    # email_accounts = session.query(User).filter_by(status=True).all()
    # for each in email_accounts:
    #     emails = get_emails(each.user_auth, 15)
    #     for email in emails:
    #         subject = email["subject"]
    #         logging.info(subject)
    #         sender_email = email["sender"]
    #         existing_email = session.query(Email).filter_by(email_id=email["email_id"]).first()
    #         reason = ""
    #         try:
    #             if not existing_email and sender_email != each.email:
    #                 status = EmailStatus.Skipped.value
    #                 # If it doesn't exist, create a new record
    #                 logging.info(sender_email)
    #                 if "cash@square.com" == sender_email:
    #                     platform = ""
    #                     subject_ele = subject.split(" ")
    #                     subject_platform = subject_ele[len(subject_ele) - 1]
    #                     second_last = subject_ele[len(subject_ele) - 2]
    #
    #                     amount = None
    #                     for each_subject_ele in subject_ele:
    #                         if "$" in each_subject_ele:
    #                             amount = each_subject_ele.replace("$", "")
    #                     logging.info(f'{subject_platform}-{second_last}-{amount}')
    #                     if subject_platform.lower() == "t" or subject_platform.lower() == "taichi":
    #
    #                         platform = Platforms.Taichi.value
    #                         user_platforms = each.platforms
    #                         game_status = EmailStatus.Failed.value
    #                         creds = None
    #                         for each_user_platforms in user_platforms:
    #                             if each_user_platforms.platform.name == Platforms.Taichi.value:
    #                                 creds = (
    #                                     each_user_platforms.platform.username, each_user_platforms.platform.password)
    #                         if amount and not creds:
    #                             reason = "Creds not Set for Platform. "
    #                         elif not amount:
    #                             reason = "Amount not Found."
    #                         else:
    #                             logging.info(f"{second_last} ---- ${amount}")
    #                             platform_response, msg = taichi(second_last, int(amount), creds[0], creds[1])
    #                             #platform_response, msg = taichi("test123", 1, creds[0], creds[1])
    #                             if platform_response == True:
    #                                 game_status = EmailStatus.Successful.value
    #                             else:
    #                                 reason = msg
    #                         new_email = Email(
    #                             email_id=email["email_id"],
    #                             subject=email["subject"],
    #                             sender_email=email["sender"],
    #                             sender_name=email["sender_name"],
    #                             status=game_status,
    #                             reason=reason,
    #                             platform=platform
    #                         )
    #                     elif subject_platform.lower() == "f" or subject_platform.lower() == "kirin" or subject_platform.lower() == "firekirin":
    #
    #                         platform = Platforms.Firekirin.value
    #                         user_platforms = each.platforms
    #                         game_status = EmailStatus.Failed.value
    #                         creds = None
    #                         for each_user_platforms in user_platforms:
    #                             if each_user_platforms.platform.name == Platforms.Firekirin.value:
    #                                 creds = (
    #                                     each_user_platforms.platform.username, each_user_platforms.platform.password)
    #                         if amount and not creds:
    #                             reason = "Creds not Set for Platform. "
    #                         elif not amount:
    #                             reason = "Amount not Found."
    #                         else:
    #                             logging.info(f"{second_last} ---- ${amount}")
    #                             #platform_response, msg = kirin("Test000_", int(amount), creds[0], creds[1])
    #                             platform_response, msg = kirin(second_last, int(amount), creds[0], creds[1])
    #                             # platform_response, msg = taichi("test123", 1, creds[0], creds[1])
    #                             if platform_response == True:
    #                                 game_status = EmailStatus.Successful.value
    #                             else:
    #                                 reason = msg
    #                         new_email = Email(
    #                             email_id=email["email_id"],
    #                             subject=email["subject"],
    #                             sender_email=email["sender"],
    #                             sender_name=email["sender_name"],
    #                             status=game_status,
    #                             reason=reason,
    #                             platform=platform
    #                         )
    #                     elif subject_platform.lower() == "v" or subject_platform.lower() == "vb" or subject_platform.lower() == "vblink":
    #
    #                         platform = Platforms.VBLink.value
    #                         user_platforms = each.platforms
    #                         game_status = EmailStatus.Failed.value
    #                         creds = None
    #                         for each_user_platforms in user_platforms:
    #                             if each_user_platforms.platform.name == Platforms.VBLink.value:
    #                                 creds = (
    #                                     each_user_platforms.platform.username, each_user_platforms.platform.password)
    #                         if amount and not creds:
    #                             reason = "Creds not Set for Platform. "
    #                         elif not amount:
    #                             reason = "Amount not Found."
    #                         else:
    #                             logging.info(f"{second_last} ---- ${amount}")
    #                             #platform_response, msg = vblink("test000111", int(amount), creds[0], creds[1])
    #                             platform_response, msg = vblink(second_last, int(amount), creds[0], creds[1])
    #                             # platform_response, msg = taichi("test123", 1, creds[0], creds[1])
    #                             if platform_response == True:
    #                                 game_status = EmailStatus.Successful.value
    #                             else:
    #                                 reason = msg
    #                         new_email = Email(
    #                             email_id=email["email_id"],
    #                             subject=email["subject"],
    #                             sender_email=email["sender"],
    #                             sender_name=email["sender_name"],
    #                             status=game_status,
    #                             reason=reason,
    #                             platform=platform
    #                         )
    #
    #                     else:
    #                         new_email = Email(
    #                             email_id=email["email_id"],
    #                             subject=email["subject"],
    #                             sender_email=email["sender"],
    #                             sender_name=email["sender_name"],
    #                             status=EmailStatus.Failed.value,
    #                             reason="Platfrom Not Identified",
    #                             platform="")
    #                 else:
    #                     new_email = Email(
    #                         email_id=email["email_id"],
    #                         subject=email["subject"],
    #                         sender_email=email["sender"],
    #                         sender_name=email["sender_name"],
    #                         status=EmailStatus.Skipped.value,
    #                         reason="Not Related to CashApp",
    #                         platform=""
    #                     )
    #
    #                 session.add(new_email)
    #                 session.commit()
    #                 user_email = UserEmail(user_id=each.id, email_id=new_email.id)
    #                 session.add(user_email)
    #                 session.commit()
    #
    #         except Exception as e:
    #             logging.exception(e)
    #             new_email = Email(
    #                 email_id=email["email_id"],
    #                 subject=email["subject"],
    #                 sender_email=email["sender"],
    #                 sender_name=email["sender_name"],
    #                 status=EmailStatus.Failed.value,
    #                 reason="Internal Server Error.",
    #                 platform=""
    #             )
    #             session.add(new_email)
    #             session.commit()
