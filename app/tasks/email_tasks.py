from app.core.celery import celery_app
from app.core.utility import send_email

@celery_app.task(
    name="app.tasks.email_tasks.send_email_task",
    bind=True,
    max_retries=3
)
def send_email_task(self, to_email: str, subject: str, body: str):
    try:
        send_email(to_email, subject, body)
    except Exception as e:
        raise self.retry(exc=e, countdown=10)