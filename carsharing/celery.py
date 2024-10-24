import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carsharing.settings')

app = Celery('carsharing')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
