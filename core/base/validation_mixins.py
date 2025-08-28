import re
from django.core.exceptions import ValidationError
from core.error_handling.enums import ErrorCode
from core.error_handling.exceptions import CustomValidationError


class EmailValidationMixin:
    """Mixin for email validation functionality"""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @classmethod
    def validate_email_format(cls, email):
        """Validate email format using regex"""
        if not email:
            return False
        
        return bool(re.match(cls.EMAIL_PATTERN, email))
    
    @classmethod
    def validate_email_or_raise(cls, email):
        """Validate email format and raise error if invalid"""
        if not cls.validate_email_format(email):
            raise CustomValidationError(ErrorCode.INVALID_EMAIL_FORMAT)
        return email


class PhoneValidationMixin:
    """Mixin for phone number validation functionality"""
    
    # US phone number pattern: (xxx) xxx-xxxx or xxx-xxx-xxxx or xxxxxxxxxx
    PHONE_PATTERN = r'^(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    
    @classmethod
    def validate_phone_format(cls, phone):
        """Validate US phone number format"""
        if not phone:
            return False
        
        return bool(re.match(cls.PHONE_PATTERN, phone))
    
    @classmethod
    def validate_phone_or_raise(cls, phone):
        """Validate phone format and raise error if invalid"""
        if not cls.validate_phone_format(phone):
            raise CustomValidationError(ErrorCode.INVALID_PHONE_FORMAT)
        return phone


class PasswordValidationMixin:
    """Mixin for password validation functionality"""
    
    @classmethod
    def validate_password_strength(cls, password):
        """Validate password strength"""
        if not password:
            return False
        
        # At least 8 characters
        if len(password) < 8:
            return False
        
        # At least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # At least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # At least one digit
        if not re.search(r'\d', password):
            return False
        
        return True
    
    @classmethod
    def validate_password_or_raise(cls, password):
        """Validate password strength and raise error if weak"""
        if not cls.validate_password_strength(password):
            raise CustomValidationError(ErrorCode.PASSWORD_TOO_WEAK)
        return password


class CommonValidationMixin(EmailValidationMixin, PhoneValidationMixin, PasswordValidationMixin):
    """Combined mixin with all common validation methods"""
    pass