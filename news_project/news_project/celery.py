import os
from celery import Celery
from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')

app = Celery('news_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-weekly-newsletter': {
        'task': 'news.tasks.schedule_weekly_newsletter',
        'schedule': timedelta(days=7),
    },
}