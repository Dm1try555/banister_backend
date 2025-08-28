import os
import io
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings

class GoogleDriveService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        try:
            service_account_file = os.path.join(settings.BASE_DIR, 'google-credentials.json')
            
            if not os.path.exists(service_account_file):
                print("Google credentials file not found at google-credentials.json")
                return
            
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            self.service = build('drive', 'v3', credentials=self.credentials)
            print("Google Drive initialized successfully")
            
        except Exception as e:
            print(f"Google Drive API initialization error: {str(e)}")
    
    def upload_file(self, file_path, folder_name="Banister Backups"):
        """Upload file to Google Drive"""
        if not self.service:
            print("Google Drive service not initialized")
            return None
        
        try:
            # Create folder if it doesn't exist
            folder_id = self._get_or_create_folder(folder_name)
            
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Read file
            with open(file_path, 'rb') as file:
                file_content = file.read()
            
            # Create file metadata
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size'
            ).execute()
            
            print(f"File uploaded successfully: {file.get('name')} (ID: {file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            error_msg = str(e)
            if "storageQuotaExceeded" in error_msg:
                print(f"Google Drive quota exceeded. File saved locally: {file_path}")
                print("To enable Google Drive uploads, configure shared drives or OAuth delegation.")
            else:
                print(f"Error uploading file to Google Drive: {error_msg}")
            return None
    
    def _get_or_create_folder(self, folder_name):
        """Get existing folder or create new one"""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            print(f"Created folder: {folder_name} (ID: {folder.get('id')})")
            return folder.get('id')
            
        except Exception as e:
            print(f"Error creating folder: {str(e)}")
            return None
    
    def list_files(self, folder_name="Banister Backups"):
        """List files in folder"""
        if not self.service:
            return []
        
        try:
            folder_id = self._get_or_create_folder(folder_name)
            
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, size, createdTime, modifiedTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def delete_old_files(self, folder_name="Banister Backups", days_to_keep=30):
        """Delete files older than specified days"""
        if not self.service:
            return 0
        
        try:
            files = self.list_files(folder_name)
            deleted_count = 0
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for file in files:
                file_date = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
                
                if file_date < cutoff_date:
                    self.service.files().delete(fileId=file['id']).execute()
                    deleted_count += 1
                    print(f"Deleted old file: {file['name']}")
            
            return deleted_count
            
        except Exception as e:
            print(f"Error deleting old files: {str(e)}")
            return 0

google_drive_service = GoogleDriveService()