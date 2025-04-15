# config/celery.py
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'daily-update-phone-data': {
        'task': 'apps.operator_by_phone.tasks.update_phone_ranges',
        'schedule': 24 * 60 * 60,  # раз в сутки
        'options': {
            'expires': 60 * 60
        }
    },
}
