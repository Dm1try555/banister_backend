import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from error_handling.exceptions import AuthenticationError
import os


def initialize_firebase():
    if not firebase_admin._apps:
        # Путь к файлу сервисного аккаунта Firebase
        service_account_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
        
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            raise AuthenticationError("Firebase service account file not found")

def verify_firebase_token(id_token):
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise AuthenticationError(str(e))