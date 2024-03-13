import os

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Users_DRF.settings')

app = Celery('Users_DRF')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')