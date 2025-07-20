import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed



def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CONFIG)
        firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token):
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise AuthenticationFailed(str(e))