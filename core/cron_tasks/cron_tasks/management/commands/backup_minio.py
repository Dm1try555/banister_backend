import os
import tempfile
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account
from minio import Minio


class Command(BaseCommand):
    help = 'Backup MinIO files to Google Drive'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting MinIO backup...')
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'minio_backup_{timestamp}.zip'
            
            # Create temporary file for backup
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                temp_backup_path = temp_file.name
            
            # Create MinIO client
            minio_client = Minio(
                        endpoint=os.getenv('MINIO_ENDPOINT').replace('http://', '').replace('https://', ''),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY'),
                secure=False
            )
            
            # Create zip file with MinIO data
            self.create_minio_backup(minio_client, temp_backup_path)
            
            # Upload to Google Drive
            self.upload_to_google_drive(temp_backup_path, backup_filename)
            
            # Clean up temporary file
            os.unlink(temp_backup_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'MinIO backup completed: {backup_filename}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during MinIO backup: {str(e)}')
            )
    
    def create_minio_backup(self, minio_client, backup_path):
        """Create backup of MinIO files"""
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # List all buckets
                buckets = minio_client.list_buckets()
                
                for bucket in buckets:
                    bucket_name = bucket.name
                    
                    # List all objects in bucket
                    objects = minio_client.list_objects(bucket_name, recursive=True)
                    
                    for obj in objects:
                        try:
                            # Get object data
                            data = minio_client.get_object(bucket_name, obj.object_name)
                            
                            # Add to zip file
                            zip_path = f'{bucket_name}/{obj.object_name}'
                            zip_file.writestr(zip_path, data.read())
                            
                            self.stdout.write(f'Added {zip_path} to backup')
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'Failed to backup {obj.object_name}: {str(e)}')
                            )
            
            self.stdout.write('MinIO backup file created successfully')
            
        except Exception as e:
            raise Exception(f'Failed to create MinIO backup: {str(e)}')
    
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
            blob = bucket.blob(f'minio_backups/{filename}')
            blob.upload_from_filename(file_path)
            
            self.stdout.write(f'Uploaded {filename} to Google Drive')
            
        except Exception as e:
            raise Exception(f'Failed to upload to Google Drive: {str(e)}') 