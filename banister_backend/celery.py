import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banister_backend.settings')

# Create Celery instance
app = Celery('banister_backend')

# Use Django settings for Celery configuration
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in Django applications
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Redis configuration
app.conf.update(
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('REDIS_URL'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Task routes (simplified)
app.conf.task_routes = {
    'core.mail.*': {'queue': 'email'},
    'core.notifications.*': {'queue': 'notifications'},
}

# Periodic task settings
app.conf.beat_schedule = {
    'database-backup': {
        'task': 'core.backup.tasks.database_backup_task',
        'schedule': crontab(hour=0, minute=0),  # daily at midnight
    },
    'minio-backup': {
        'task': 'core.backup.tasks.minio_backup_task',
        'schedule': crontab(hour=0, minute=0),  # daily at midnight
    },
    'cleanup-old-notifications': {
        'task': 'core.backup.tasks.cleanup_notifications_task',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # weekly on Sunday at midnight
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 