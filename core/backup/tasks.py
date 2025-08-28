from celery import shared_task
from .local_service import local_backup_service
from core.google_drive.service import google_drive_service

@shared_task(bind=True, max_retries=3)
def database_backup_task(self):
    try:
        # Create local backup
        backup_file = local_backup_service.backup_database()
        
        # Upload to Google Drive
        drive_file_id = google_drive_service.upload_file(backup_file, "Banister Database Backups")
        
        result = f"Database backup completed: {backup_file}"
        if drive_file_id:
            result += f" (Uploaded to Google Drive: {drive_file_id})"
        else:
            result += " (Google Drive upload failed)"
        
        return result
    except Exception as e:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        return f"Database backup failed: {str(e)}"

@shared_task(bind=True, max_retries=3)
def minio_backup_task(self):
    try:
        # Create local backup
        backup_file = local_backup_service.backup_minio()
        
        # Upload to Google Drive
        drive_file_id = google_drive_service.upload_file(backup_file, "Banister MinIO Backups")
        
        result = f"MinIO backup completed: {backup_file}"
        if drive_file_id:
            result += f" (Uploaded to Google Drive: {drive_file_id})"
        else:
            result += " (Google Drive upload failed)"
        
        return result
    except Exception as e:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        return f"MinIO backup failed: {str(e)}"

@shared_task(bind=True, max_retries=3)
def cleanup_notifications_task(self):
    try:
        deleted_count = local_backup_service.cleanup_old_notifications()
        return f"Cleaned up {deleted_count} old notifications"
    except Exception as e:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        return f"Notifications cleanup failed: {str(e)}"