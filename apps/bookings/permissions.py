from core.base.permissions import BasePermissionsMixin


class BookingPermissions(BasePermissionsMixin):
    """Permissions for bookings"""
    
    def can_view_bookings(self, role):
        """Who can view bookings"""
        # Only registered users
        return role != 'anonymous'
    
    def can_create_booking(self, role):
        """Who can create bookings"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']
    
    def can_edit_booking(self, role):
        """Who can edit bookings"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']
    
    def can_delete_booking(self, role):
        """Who can delete bookings"""
        # All except Service Provider
        return role != 'service_provider'
    
    def can_view_booking_details(self, role):
        """Who can view booking details"""
        # Only registered users
        return role != 'anonymous'
    
    def can_cancel_booking(self, role):
        """Who can cancel bookings"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']


class InterviewPermissions(BasePermissionsMixin):
    """Permissions for interviews"""
    
    def can_view_interviews(self, role):
        """Who can view interviews"""
        # Только зарегистрированные пользователи
        return role != 'anonymous'
    
    def can_create_interview(self, role):
        """Who can create interviews"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']
    
    def can_edit_interview(self, role):
        """Who can edit interviews"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']
    
    def can_delete_interview(self, role):
        """Who can delete interviews"""
        # All except Service Provider
        return role != 'service_provider'
    
    def can_view_interview_details(self, role):
        """Who can view interview details"""
        # Only registered users
        return role != 'anonymous'
    
    def can_schedule_interview(self, role):
        """Who can schedule interviews"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer'] 