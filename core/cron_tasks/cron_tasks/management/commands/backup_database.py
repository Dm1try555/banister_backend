import os
import tempfile
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account


class Command(BaseCommand):
    help = 'Backup database to Google Drive'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting database backup...')
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'database_backup_{timestamp}.sql'
            
            # Get database settings
            db_settings = settings.DATABASES['default']
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_password = db_settings['PASSWORD']
            db_host = db_settings['HOST']
            db_port = db_settings['PORT']
            
            # Create temporary file for backup
            with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as temp_file:
                temp_backup_path = temp_file.name
            
            # Create pg_dump command
            if db_password:
                os.environ['PGPASSWORD'] = db_password
            
            pg_dump_cmd = [
                'pg_dump',
                '-h', db_host or 'localhost',
                '-p', str(db_port or 5432),
                '-U', db_user,
                '-d', db_name,
                '-f', temp_backup_path
            ]
            
            # Execute pg_dump
            result = subprocess.run(pg_dump_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.stdout.write(
                    self.style.ERROR(f'Database backup failed: {result.stderr}')
                )
                return
            
            # Upload to Google Drive
            self.upload_to_google_drive(temp_backup_path, backup_filename)
            
            # Clean up temporary file
            os.unlink(temp_backup_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'Database backup completed: {backup_filename}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during database backup: {str(e)}')
            )
    
    def upload_to_google_drive(self, file_path, filename):
        """Upload file to Google Drive using Google Cloud Storage"""
        try:
            # Get Google Cloud credentials from environment or use local file
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_path:
                # Try to use local key file
                local_key_path = os.path.join(
                    settings.BASE_DIR,
                    'google-credentials.json'
                )
                if os.path.exists(local_key_path):
                    credentials_path = local_key_path
                else:
                    raise Exception('GOOGLE_APPLICATION_CREDENTIALS environment variable not set and local key file not found')
            
            # Initialize Google Cloud Storage client
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            storage_client = storage.Client(credentials=credentials)
            
            # Get bucket
            bucket_name = os.getenv('GOOGLE_CLOUD_BUCKET_NAME')
            bucket = storage_client.bucket(bucket_name)
            
            # Create blob and upload
            blob = bucket.blob(f'database_backups/{filename}')
            blob.upload_from_filename(file_path)
            
            self.stdout.write(f'Uploaded {filename} to Google Drive')
            
        except Exception as e:
            raise Exception(f'Failed to upload to Google Drive: {str(e)}') 