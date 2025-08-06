import os
from minio import Minio
from django.conf import settings
from PIL import Image
import io
import uuid
from datetime import datetime

def get_minio_client():
    """Get MinIO client"""
    return Minio(
        endpoint=os.getenv('MINIO_ENDPOINT').replace('http://', '').replace('https://', ''),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        secure=False  # For local development
    )

def create_bucket_if_not_exists(bucket_name):
    try:
        client = get_minio_client()
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            set_bucket_public_policy(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully and set public")
        return True
    except Exception as e:
        print(f"Error creating bucket '{bucket_name}': {e}")
        return False

def upload_file_to_minio(file_obj, bucket_name, object_key, content_type=None):
    """Upload file to MinIO"""
    try:
        client = get_minio_client()
        
        # Create bucket if it doesn't exist
        create_bucket_if_not_exists(bucket_name)
        
        # Upload file
        file_data = file_obj.read()
        file_obj.seek(0)  # Reset file position
        
        client.put_object(
            bucket_name,
            object_key,
            io.BytesIO(file_data),
            length=len(file_data),
            content_type=content_type or file_obj.content_type
        )
        
        return True
    except Exception as e:
        print(f"Error uploading file to MinIO: {e}")
        return False

def delete_file_from_minio(bucket_name, object_key):
    """Delete file from MinIO"""
    try:
        client = get_minio_client()
        client.remove_object(bucket_name, object_key)
        return True
    except Exception as e:
        print(f"Error deleting file from MinIO: {e}")
        return False

def resize_image(image_file, max_size=(800, 800)):
    """Resize image"""
    try:
        image = Image.open(image_file)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize maintaining aspect ratio
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def generate_object_key(user_id, file_type, original_name):
    """Generate unique key for file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(original_name)[1]
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{user_id}/{file_type}/{timestamp}_{unique_id}{file_extension}"

def get_bucket_name_for_file_type(file_type):
    """Get bucket name for file type"""
    bucket_mapping = {
        'profile_photo': 'profile-photos',
        'document': 'documents',
        'image': 'images',
        'other': 'misc'
    }
    return bucket_mapping.get(file_type, 'misc')

def validate_image_file(file_obj):
    """Validate image"""
    try:
        image = Image.open(file_obj)
        image.verify()
        file_obj.seek(0)
        return True
    except Exception:
        return False

def get_file_size_mb(file_obj):
    """Get file size in MB"""
    file_obj.seek(0, 2)  # Move to end of file
    size = file_obj.tell()
    file_obj.seek(0)  # Return to beginning
    return size / (1024 * 1024)  # Convert to MB 

def set_bucket_public_policy(bucket_name):
    client = get_minio_client()
    policy_json = """
    {
        "Version":"2012-10-17",
        "Statement":[
            {
                "Effect":"Allow",
                "Principal":{"AWS":["*"]},
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::%s/*"]
            }
        ]
    }
    """ % bucket_name

    client.set_bucket_policy(bucket_name, policy_json)

