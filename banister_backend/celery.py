import os
from celery import Celery
from django.conf import settings

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banister_backend.settings')

# Создание экземпляра Celery
app = Celery('banister_backend')

# Использование настроек Django для конфигурации Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Конфигурация Redis
app.conf.update(
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('REDIS_URL'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Настройки для email очередей
app.conf.task_routes = {
    'mail.tasks.*': {'queue': 'email'},
    'notifications.tasks.*': {'queue': 'notifications'},
    'workers.tasks.*': {'queue': 'workers'},
}

# Настройки для периодических задач
app.conf.beat_schedule = {
    'cleanup-expired-verification-codes': {
        'task': 'authentication.tasks.cleanup_expired_verification_codes',
        'schedule': 3600.0,  # каждый час
    },
    'send-scheduled-emails': {
        'task': 'mail.tasks.process_email_queue',
        'schedule': 60.0,  # каждую минуту
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 