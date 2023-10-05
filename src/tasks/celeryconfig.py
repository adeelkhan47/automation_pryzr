from datetime import timedelta

from celery.schedules import crontab

from config import settings

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

broker_url = settings.CELERY_BROKER_REDIS
broker_transport_options = {"visibility_timeout": 3600 * 6}
result_backend = settings.CELERY_BROKER_REDIS
result_persistent = False

imports = ("tasks.email_process", "tasks.queue")

beat_schedule = {
    "emails_get-every_minute": {
        "task": "tasks.email.fetch_new",
        "schedule": timedelta(seconds=30),
    },
    "sync_whitelist-every_minute": {
        "task": "tasks.email.sync_whitelist",
        "schedule": crontab(minute="*", hour="*"),
    },
    "process_queue-every_thirtyseconds": {
        "task": "tasks.queue.process_queue",
        "schedule": timedelta(seconds=30),
    },
}
