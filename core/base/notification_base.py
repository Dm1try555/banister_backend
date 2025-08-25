from core.base.common_imports import *

class NotificationBase:
    def _create_notification(self, user, notification_type, data, push_title=None, push_body=None):
        try:
            from apps.notifications.models import Notification
            from core.firebase.service import firebase_service
            
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                data=data
            )
            
            if user.firebase_token and push_title and push_body:
                firebase_service.send_notification(
                    user_token=user.firebase_token,
                    title=push_title,
                    body=push_body,
                    data=data
                )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
