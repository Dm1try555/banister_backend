import os
import subprocess
from datetime import datetime, timedelta
import shutil
import glob

class LocalBackupService:
    def __init__(self):
        self.backup_dir = '/app/backups'
        self._create_backup_dir()
    
    def _create_backup_dir(self):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_database(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.backup_dir}/db_backup_{timestamp}.sql"
        
        subprocess.run([
            'pg_dump',
            '-h', os.getenv('DB_HOST'),
            '-U', os.getenv('POSTGRES_USER'),
            '-d', os.getenv('POSTGRES_DB'),
            '-f', backup_file
        ], env={**os.environ, 'PGPASSWORD': os.getenv('POSTGRES_PASSWORD')})
        
        self._cleanup_old_backups('db_backup_*.sql')
        return backup_file
    
    def backup_minio(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.backup_dir}/minio_backup_{timestamp}.tar.gz"
        
        # Create info file first
        info_file = f"{self.backup_dir}/minio_info_{timestamp}.txt"
        with open(info_file, 'w') as f:
            f.write(f"MinIO backup created at {datetime.now()}\n")
            f.write("MinIO endpoint: minio:9000\n")
            f.write("Bucket: profile-photos\n")
            f.write("Note: This is a placeholder backup file\n")
        
        # Create tar.gz with the info file
        subprocess.run([
            'tar', '-czf', backup_file, '-C', self.backup_dir, f"minio_info_{timestamp}.txt"
        ])
        
        # Remove the info file
        os.remove(info_file)
        
        self._cleanup_old_backups('minio_backup_*.tar.gz')
        return backup_file
    
    def cleanup_old_notifications(self):
        from apps.notifications.models import Notification
        from datetime import timedelta
        from django.utils import timezone
        
        two_months_ago = timezone.now() - timedelta(days=60)
        deleted_count = Notification.objects.filter(
            created_at__lt=two_months_ago
        ).delete()[0]
        
        return deleted_count
    
    def _cleanup_old_backups(self, pattern, keep_count=7):
        backup_files = glob.glob(f"{self.backup_dir}/{pattern}")
        backup_files.sort(key=os.path.getctime, reverse=True)
        
        for old_file in backup_files[keep_count:]:
            os.remove(old_file)
    
    def list_backups(self):
        db_backups = glob.glob(f"{self.backup_dir}/db_backup_*.sql")
        minio_backups = glob.glob(f"{self.backup_dir}/minio_backup_*.tar.gz")
        
        db_list = []
        for file in sorted(db_backups, key=os.path.getctime, reverse=True):
            stat = os.stat(file)
            db_list.append({
                'name': os.path.basename(file),
                'path': file,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        
        minio_list = []
        for file in sorted(minio_backups, key=os.path.getctime, reverse=True):
            stat = os.stat(file)
            minio_list.append({
                'name': os.path.basename(file),
                'path': file,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        
        return {
            'database_backups': db_list,
            'minio_backups': minio_list
        }

local_backup_service = LocalBackupService()