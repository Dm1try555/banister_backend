import os
import tempfile
import tarfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account
from minio import Minio


class Command(BaseCommand):
    help = 'Backup MinIO storage to Google Drive'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting MinIO backup...')
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'minio_backup_{timestamp}.tar.gz'
            
            # Get MinIO settings from environment
            minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
            minio_access_key = os.getenv('MINIO_ACCESS_KEY')
            minio_secret_key = os.getenv('MINIO_SECRET_KEY')
            minio_secure = os.getenv('MINIO_SECURE', 'False').lower() == 'true'
            
            if not minio_access_key or not minio_secret_key:
                raise Exception('MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set')
            
            # Initialize MinIO client
            minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=minio_secure
            )
            
            # Create temporary directory for backup
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_path = os.path.join(temp_dir, backup_filename)
                
                # Create tar.gz archive
                with tarfile.open(backup_path, 'w:gz') as tar:
                    # List all buckets
                    buckets = minio_client.list_buckets()
                    
                    for bucket in buckets:
                        bucket_name = bucket.name
                        self.stdout.write(f'Backing up bucket: {bucket_name}')
                        
                        # Create bucket directory in archive
                        bucket_dir = f'minio_backup/{bucket_name}/'
                        
                        # List all objects in bucket
                        objects = minio_client.list_objects(bucket_name, recursive=True)
                        
                        for obj in objects:
                            try:
                                # Download object to temporary file
                                temp_file_path = os.path.join(temp_dir, f'{bucket_name}_{obj.object_name}')
                                
                                # Create directory structure
                                os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                                
                                # Download object
                                minio_client.fget_object(bucket_name, obj.object_name, temp_file_path)
                                
                                # Add to archive
                                archive_path = f'minio_backup/{bucket_name}/{obj.object_name}'
                                tar.add(temp_file_path, arcname=archive_path)
                                
                                # Clean up temporary file
                                os.unlink(temp_file_path)
                                
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(f'Failed to backup object {obj.object_name}: {str(e)}')
                                )
                
                # Upload to Google Drive
                self.upload_to_google_drive(backup_path, backup_filename)
            
            self.stdout.write(
                self.style.SUCCESS(f'MinIO backup completed: {backup_filename}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during MinIO backup: {str(e)}')
            )
    
    def upload_to_google_drive(self, file_path, filename):
        """Upload file to Google Drive using Google Cloud Storage"""
        try:
            # Get Google Cloud credentials from environment or use local file
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_path:
                # Try to use local key file
                local_key_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'banister-backup-1700feef3b7a.json'
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
            bucket_name = os.getenv('GOOGLE_CLOUD_BUCKET_NAME', 'banister-backups')
            bucket = storage_client.bucket(bucket_name)
            
            # Create blob and upload
            blob = bucket.blob(f'minio_backups/{filename}')
            blob.upload_from_filename(file_path)
            
            self.stdout.write(f'Uploaded {filename} to Google Drive')
            
        except Exception as e:
            raise Exception(f'Failed to upload to Google Drive: {str(e)}') 