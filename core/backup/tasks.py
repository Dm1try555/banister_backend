from celery import shared_task
from .service import backup_service

@shared_task
def database_backup_task():
    try:
        backup_service.backup_database()
        return "Database backup completed successfully"
    except Exception as e:
        return f"Database backup failed: {str(e)}"

@shared_task
def minio_backup_task():
    try:
        backup_service.backup_minio()
        return "MinIO backup completed successfully"
    except Exception as e:
        return f"MinIO backup failed: {str(e)}"

@shared_task
def cleanup_notifications_task():
    try:
        deleted_count = backup_service.cleanup_old_notifications()
        return f"Cleaned up {deleted_count} old notifications"
    except Exception as e:
        return f"Notifications cleanup failed: {str(e)}"