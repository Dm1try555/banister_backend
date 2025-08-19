import os
from minio import Minio
from minio.error import S3Error
from django.conf import settings

class MinioClient:
    def __init__(self):
        self.client = Minio(
            os.getenv('MINIO_ENDPOINT'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=False
        )
        self.bucket_name = 'profile-photos'
        self._create_bucket()
    
    def _create_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error:
            pass
    
    def upload_file(self, file_obj, file_name):
        try:
            self.client.put_object(
                self.bucket_name,
                file_name,
                file_obj,
                length=file_obj.size,
                content_type=file_obj.content_type
            )
            return f"http://{os.getenv('MINIO_ENDPOINT')}/{self.bucket_name}/{file_name}"
        except S3Error:
            return None
    
    def delete_file(self, file_name):
        try:
            self.client.remove_object(self.bucket_name, file_name)
            return True
        except S3Error:
            return False

minio_client = MinioClient()