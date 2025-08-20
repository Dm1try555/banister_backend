from celery import shared_task
from .local_service import local_backup_service

@shared_task
def database_backup_task():
    try:
        backup_file = local_backup_service.backup_database()
        return f"Database backup completed: {backup_file}"
    except Exception as e:
        return f"Database backup failed: {str(e)}"

@shared_task
def minio_backup_task():
    try:
        backup_file = local_backup_service.backup_minio()
        return f"MinIO backup completed: {backup_file}"
    except Exception as e:
        return f"MinIO backup failed: {str(e)}"

@shared_task
def cleanup_notifications_task():
    try:
        deleted_count = local_backup_service.cleanup_old_notifications()
        return f"Cleaned up {deleted_count} old notifications"
    except Exception as e:
        return f"Notifications cleanup failed: {str(e)}"