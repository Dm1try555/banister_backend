import os
import json
from firebase_admin import credentials, messaging, initialize_app
from django.conf import settings

class FirebaseService:
    """Centralized Firebase service for push notifications"""
    
    def __init__(self):
        self.app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase app using firebase-service-account.json"""
        try:
            firebase_config_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
            
            if not os.path.exists(firebase_config_path):
                print("Firebase service account file not found at firebase-service-account.json")
                return
            
            cred = credentials.Certificate(firebase_config_path)
            self.app = initialize_app(cred)
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Firebase initialization error: {str(e)}")
    
    def send_notification(self, user_token, title, body, data=None):
        """Send push notification via Firebase"""
        if not self.app or not user_token:
            return False, "Firebase not initialized or no user token"
        
        try:
            message_data = {
                'notification': messaging.Notification(
                    title=title,
                    body=body
                ),
                'token': user_token
            }
            
            if data:
                message_data['data'] = data
            
            message = messaging.Message(**message_data)
            response = messaging.send(message)
            return True, response
            
        except Exception as e:
            return False, f"Firebase send error: {str(e)}"
    
    def send_to_multiple(self, tokens, title, body, data=None):
        """Send notification to multiple devices"""
        if not self.app or not tokens:
            return False, "Firebase not initialized or no tokens"
        
        try:
            message_data = {
                'notification': messaging.Notification(
                    title=title,
                    body=body
                ),
                'tokens': tokens
            }
            
            if data:
                message_data['data'] = data
            
            response = messaging.send_multicast(messaging.MulticastMessage(**message_data))
            return True, response
            
        except Exception as e:
            return False, f"Firebase multicast error: {str(e)}"
    
    def send_to_topic(self, topic, title, body, data=None):
        """Send notification to topic subscribers"""
        if not self.app:
            return False, "Firebase not initialized"
        
        try:
            message_data = {
                'notification': messaging.Notification(
                    title=title,
                    body=body
                ),
                'topic': topic
            }
            
            if data:
                message_data['data'] = data
            
            message = messaging.Message(**message_data)
            response = messaging.send(message)
            return True, response
            
        except Exception as e:
            return False, f"Firebase topic error: {str(e)}"

firebase_service = FirebaseService()