from datetime import timedelta

from config import settings

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

broker_url = settings.CELERY_BROKER_REDIS
broker_transport_options = {"visibility_timeout": 3600 * 6}
result_backend = settings.CELERY_BROKER_REDIS
result_persistent = False

imports = ("tasks.email","tasks.account")


beat_schedule = {
    "account_processed": {
        "task": "tasks.email.process_new",
        "schedule": timedelta(minutes=1)
    },
    "unauthorized_account_processed": {
        "task": "tasks.account.process_unauthorized_accounts",
        "schedule": timedelta(minutes=5)
    },
    "delete_old_emails": {
        "task": "tasks.account.process_old_emails",
        "schedule": timedelta(hours=10)
    }
}




