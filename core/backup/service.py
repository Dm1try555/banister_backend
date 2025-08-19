import os
import subprocess
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload

class BackupService:
    def __init__(self):
        self.credentials = Credentials.from_service_account_file(
            'google-credentials.json',
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive = build('drive', 'v3', credentials=self.credentials)
    
    def backup_database(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"db_backup_{timestamp}.sql"
        
        subprocess.run([
            'pg_dump',
            '-h', os.getenv('DB_HOST'),
            '-U', os.getenv('POSTGRES_USER'),
            '-d', os.getenv('POSTGRES_DB'),
            '-f', backup_file
        ], env={**os.environ, 'PGPASSWORD': os.getenv('POSTGRES_PASSWORD')})
        
        self._upload_to_drive(backup_file, 'database_backups')
        os.remove(backup_file)
    
    def backup_minio(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"minio_backup_{timestamp}.tar.gz"
        
        subprocess.run([
            'tar', '-czf', backup_file, '/data'
        ])
        
        self._upload_to_drive(backup_file, 'minio_backups')
        os.remove(backup_file)
    
    def cleanup_old_notifications(self):
        from apps.notifications.models import Notification
        from datetime import timedelta
        
        two_months_ago = datetime.now() - timedelta(days=60)
        deleted_count = Notification.objects.filter(
            created_at__lt=two_months_ago
        ).delete()[0]
        
        return deleted_count
    
    def _upload_to_drive(self, file_path, folder_name):
        media = MediaFileUpload(file_path)
        
        self.drive.files().create(
            body={'name': os.path.basename(file_path)},
            media_body=media
        ).execute()

backup_service = BackupService()