import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from apps.authentication.models import User, UserFCMToken
from apps.notifications.models import Notification
from core.firebase.service import firebase_service
from core.error_handling import ErrorCode
from core.error_handling.exceptions import CustomValidationError

logger = logging.getLogger(__name__)


class NotificationService:
    """Centralized notification service with Firebase integration"""
    
    # Notification types
    NOTIFICATION_TYPES = {
        'CLIENT_SEND_BOOKING_TO_ADMIN': 'ClientSendBookingNotificationToAdmin',
        'BOOKING_CONFIRMED': 'BookingConfirmed',
        'BOOKING_CANCELLED': 'BookingCancelled',
        'PAYMENT_RECEIVED': 'PaymentReceived',
        'PAYMENT_FAILED': 'PaymentFailed',
        'REMINDER': 'Reminder',
        'WELCOME': 'Welcome',
        'EMAIL_VERIFIED': 'EmailVerified',
        'PASSWORD_RESET': 'PasswordReset',
    }
    
    @staticmethod
    def send_notification(
        user: User,
        notification_type: str,
        data: Dict[str, Any] = None,
        title: str = None,
        body: str = None,
        send_push: bool = True,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Send notification to user via Firebase and save to database
        
        Args:
            user: Target user
            notification_type: Type of notification
            data: Additional data for the notification
            title: Push notification title
            body: Push notification body
            send_push: Whether to send push notification
            save_to_db: Whether to save to database
            
        Returns:
            Dict with success status and details
        """
        try:
            result = {
                'success': True,
                'notification_id': None,
                'push_sent': False,
                'push_error': None,
                'db_saved': False,
                'db_error': None
            }
            
            # Save to database
            if save_to_db:
                try:
                    with transaction.atomic():
                        notification = Notification.objects.create(
                            user=user,
                            notification_type=notification_type,
                            data=data or {}
                        )
                        result['notification_id'] = notification.id
                        result['db_saved'] = True
                        logger.info(f"Notification saved to DB: {notification.id}")
                except Exception as e:
                    result['db_error'] = str(e)
                    logger.error(f"Failed to save notification to DB: {e}")
            
            # Send push notification
            if send_push:
                try:
                    # Get user's FCM tokens
                    fcm_tokens = UserFCMToken.objects.filter(
                        user=user,
                        is_active=True
                    ).values_list('token', flat=True)
                    
                    if fcm_tokens:
                        # Prepare push notification data
                        push_data = {
                            'notification_type': notification_type,
                            'notification_id': str(result['notification_id']) if result['notification_id'] else None,
                            **(data or {})
                        }
                        
                        # Send to all user's devices
                        success, response = firebase_service.send_to_multiple(
                            tokens=list(fcm_tokens),
                            title=title or NotificationService._get_default_title(notification_type),
                            body=body or NotificationService._get_default_body(notification_type),
                            data=push_data
                        )
                        
                        if success:
                            result['push_sent'] = True
                            logger.info(f"Push notification sent to {len(fcm_tokens)} devices for user {user.username}")
                        else:
                            result['push_error'] = response
                            logger.error(f"Failed to send push notification: {response}")
                    else:
                        result['push_error'] = "No active FCM tokens found for user"
                        logger.warning(f"No FCM tokens found for user {user.username}")
                        
                except Exception as e:
                    result['push_error'] = str(e)
                    logger.error(f"Failed to send push notification: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Notification service error: {e}")
            raise CustomValidationError(ErrorCode.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def send_to_multiple_users(
        users: List[User],
        notification_type: str,
        data: Dict[str, Any] = None,
        title: str = None,
        body: str = None,
        send_push: bool = True,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Send notification to multiple users
        
        Args:
            users: List of target users
            notification_type: Type of notification
            data: Additional data for the notification
            title: Push notification title
            body: Push notification body
            send_push: Whether to send push notifications
            save_to_db: Whether to save to database
            
        Returns:
            Dict with results for each user
        """
        results = {
            'total_users': len(users),
            'successful': 0,
            'failed': 0,
            'user_results': []
        }
        
        for user in users:
            try:
                result = NotificationService.send_notification(
                    user=user,
                    notification_type=notification_type,
                    data=data,
                    title=title,
                    body=body,
                    send_push=send_push,
                    save_to_db=save_to_db
                )
                
                results['user_results'].append({
                    'user_id': user.id,
                    'username': user.username,
                    'result': result
                })
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['user_results'].append({
                    'user_id': user.id,
                    'username': user.username,
                    'error': str(e)
                })
                logger.error(f"Failed to send notification to user {user.username}: {e}")
        
        return results
    
    @staticmethod
    def send_to_admins(
        notification_type: str,
        data: Dict[str, Any] = None,
        title: str = None,
        body: str = None,
        send_push: bool = True,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Send notification to all admin users
        
        Args:
            notification_type: Type of notification
            data: Additional data for the notification
            title: Push notification title
            body: Push notification body
            send_push: Whether to send push notifications
            save_to_db: Whether to save to database
            
        Returns:
            Dict with results
        """
        admin_users = User.objects.filter(role='admin')
        return NotificationService.send_to_multiple_users(
            users=list(admin_users),
            notification_type=notification_type,
            data=data,
            title=title,
            body=body,
            send_push=send_push,
            save_to_db=save_to_db
        )
    
    @staticmethod
    def register_fcm_token(user: User, token: str, device_type: str = 'web') -> bool:
        """
        Register or update user's FCM token
        
        Args:
            user: User to register token for
            token: FCM token
            device_type: Type of device (web, android, ios)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                # Deactivate old tokens for this user and device type
                UserFCMToken.objects.filter(
                    user=user,
                    device_type=device_type
                ).update(is_active=False)
                
                # Create or update token
                fcm_token, created = UserFCMToken.objects.update_or_create(
                    token=token,
                    defaults={
                        'user': user,
                        'device_type': device_type,
                        'is_active': True
                    }
                )
                
                logger.info(f"FCM token {'created' if created else 'updated'} for user {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register FCM token: {e}")
            return False
    
    @staticmethod
    def unregister_fcm_token(token: str) -> bool:
        """
        Unregister FCM token
        
        Args:
            token: FCM token to unregister
            
        Returns:
            True if successful, False otherwise
        """
        try:
            UserFCMToken.objects.filter(token=token).update(is_active=False)
            logger.info(f"FCM token unregistered: {token}")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister FCM token: {e}")
            return False
    
    @staticmethod
    def _get_default_title(notification_type: str) -> str:
        """Get default title for notification type"""
        titles = {
            'ClientSendBookingNotificationToAdmin': 'New Booking Request',
            'BookingConfirmed': 'Booking Confirmed',
            'BookingCancelled': 'Booking Cancelled',
            'PaymentReceived': 'Payment Received',
            'PaymentFailed': 'Payment Failed',
            'Reminder': 'Reminder',
            'Welcome': 'Welcome!',
            'EmailVerified': 'Email Verified',
            'PasswordReset': 'Password Reset',
        }
        return titles.get(notification_type, 'Notification')
    
    @staticmethod
    def _get_default_body(notification_type: str) -> str:
        """Get default body for notification type"""
        bodies = {
            'ClientSendBookingNotificationToAdmin': 'A new booking request has been submitted',
            'BookingConfirmed': 'Your booking has been confirmed',
            'BookingCancelled': 'Your booking has been cancelled',
            'PaymentReceived': 'Payment has been received successfully',
            'PaymentFailed': 'Payment processing failed',
            'Reminder': 'You have a reminder',
            'Welcome': 'Welcome to our platform!',
            'EmailVerified': 'Your email has been verified successfully',
            'PasswordReset': 'Password reset instructions sent',
        }
        return bodies.get(notification_type, 'You have a new notification')


# Create service instance
notification_service = NotificationService()