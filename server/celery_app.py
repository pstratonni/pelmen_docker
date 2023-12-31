import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_server.settings')

app = Celery('shop_server')
app.config_from_object('django.conf:settings')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
app.conf.timezone = settings.TIME_ZONE
app.autodiscover_tasks()


