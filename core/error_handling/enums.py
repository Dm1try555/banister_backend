from enum import Enum


class ErrorCode(Enum):
    # Authentication errors (1000-1999)
    INVALID_CREDENTIALS = (1001, "Invalid credentials", "Username or password is incorrect")
    USER_NOT_FOUND = (1002, "User not found", "User with specified ID does not exist")
    TOKEN_EXPIRED = (1003, "Token expired", "Authentication token has expired")
    INVALID_TOKEN = (1004, "Invalid token", "Authentication token is invalid")
    AUTHENTICATION_REQUIRED = (1005, "Authentication required", "Authentication credentials were not provided")
    PERMISSION_DENIED = (1006, "Permission denied", "You don't have permission to perform this action")
    USER_ALREADY_EXISTS = (1007, "User already exists", "User with this email or username already exists")
    EMAIL_NOT_VERIFIED = (1008, "Email not verified", "Please verify your email address first")
    INVALID_VERIFICATION_CODE = (1009, "Invalid verification code", "Verification code is incorrect or expired")
    EMAIL_ALREADY_VERIFIED = (1010, "Email already verified", "Email address is already verified")
    VERIFICATION_CODE_EXPIRED = (1011, "Verification code expired", "Verification code has expired")
    EMAIL_SEND_FAILED = (1012, "Email send failed", "Failed to send email")
    EMAIL_VERIFICATION_FAILED = (1013, "Email verification failed", "Failed to verify email address")
    PASSWORD_RESET_FAILED = (1014, "Password reset failed", "Failed to reset password")
    PASSWORD_TOO_WEAK = (1015, "Password too weak", "Password must be at least 8 characters long")
    INVALID_EMAIL_FORMAT = (1016, "Invalid email format", "Email format is invalid")
    EMAIL_NOT_FOUND = (1017, "Email not found", "No account found with this email address")
    INVALID_PHONE_FORMAT = (1018, "Invalid phone format", "Phone number format is invalid")
    PASSWORDS_DO_NOT_MATCH = (1019, "Passwords do not match", "Password and password confirmation do not match")
    FILE_TOO_LARGE = (1020, "File too large", "File size exceeds maximum allowed limit")
    INVALID_FILE_TYPE = (1021, "Invalid file type", "File type is not supported")
    EMPTY_FILE = (1022, "Empty file", "File cannot be empty")

    # Booking errors (2000-2099)
    BOOKING_NOT_FOUND = (2001, "Booking not found", "Booking with specified ID does not exist")
    BOOKING_CONFLICT = (2002, "Booking conflict", "Time slot is already booked")
    INVALID_BOOKING_TIME = (2003, "Invalid booking time", "Booking time is in the past or invalid")
    BOOKING_CANCELLED = (2004, "Booking cancelled", "This booking has been cancelled")
    BOOKING_EXPIRED = (2005, "Booking expired", "Booking request has expired")
    BOOKING_LIMIT_EXCEEDED = (2006, "Booking limit exceeded", "Maximum number of bookings reached")
    INVALID_BOOKING_STATUS = (2007, "Invalid booking status", "Cannot perform action with current booking status")

    # Interview errors (2100-2199)
    INTERVIEW_NOT_FOUND = (2101, "Interview not found", "Interview with specified ID does not exist")
    INTERVIEW_ALREADY_SCHEDULED = (2102, "Interview already scheduled", "Interview is already scheduled for this time")
    INTERVIEW_TIME_CONFLICT = (2103, "Interview time conflict", "Interview time conflicts with existing schedule")
    INTERVIEW_CANNOT_BE_CANCELLED = (2104, "Interview cannot be cancelled", "Interview cannot be cancelled at this stage")
    INTERVIEW_STATUS_INVALID = (2105, "Invalid interview status", "Cannot change interview to this status")

    # Service errors (3000-3099)
    SERVICE_NOT_FOUND = (3001, "Service not found", "Service with specified ID does not exist")
    SERVICE_UNAVAILABLE = (3002, "Service unavailable", "Service is currently unavailable")
    INVALID_SERVICE_PRICE = (3003, "Invalid price", "Service price must be positive")
    SERVICE_ALREADY_EXISTS = (3004, "Service already exists", "Service with this name already exists")
    SERVICE_CATEGORY_NOT_FOUND = (3005, "Service category not found", "Service category does not exist")
    SERVICE_DELETION_FAILED = (3006, "Service deletion failed", "Cannot delete service with active bookings")

    # Schedule errors (3100-3199)
    SCHEDULE_NOT_FOUND = (3101, "Schedule not found", "Schedule with specified ID does not exist")
    SCHEDULE_CONFLICT = (3102, "Schedule conflict", "Schedule overlaps with existing schedule")
    INVALID_SCHEDULE_TIME = (3103, "Invalid schedule time", "Schedule time is invalid")
    SCHEDULE_OUTSIDE_WORKING_HOURS = (3104, "Schedule outside working hours", "Schedule time is outside working hours")
    SCHEDULE_DAY_NOT_AVAILABLE = (3105, "Schedule day not available", "This day is not available for scheduling")

    # Payment errors (4000-4099)
    PAYMENT_FAILED = (4001, "Payment failed", "Payment processing failed")
    INSUFFICIENT_FUNDS = (4002, "Insufficient funds", "Not enough funds to complete payment")
    PAYMENT_NOT_FOUND = (4003, "Payment not found", "Payment with specified ID does not exist")
    INVALID_PAYMENT_METHOD = (4004, "Invalid payment method", "Payment method is not supported")
    PAYMENT_ALREADY_PROCESSED = (4005, "Payment already processed", "Payment has already been processed")
    PAYMENT_AMOUNT_INVALID = (4006, "Invalid payment amount", "Payment amount must be positive")
    PAYMENT_INTENT_EXPIRED = (4007, "Payment intent expired", "Payment intent has expired")

    # Document errors (4500-4599)
    DOCUMENT_NOT_FOUND = (4501, "Document not found", "Document with specified ID does not exist")
    DOCUMENT_ACCESS_DENIED = (4502, "Document access denied", "User does not have permission to access this document")
    INVALID_FILE_FORMAT = (4503, "Invalid file format", "File format is not supported")
    DOCUMENT_ALREADY_EXISTS = (4505, "Document already exists", "Document with this name already exists")
    DOCUMENT_PROCESSING_ERROR = (4506, "Document processing error", "Error occurred while processing document")

    # Withdrawal errors (5000-5099)
    WITHDRAWAL_NOT_FOUND = (5001, "Withdrawal not found", "Withdrawal with specified ID does not exist")
    WITHDRAWAL_ALREADY_PROCESSED = (5002, "Withdrawal already processed", "Withdrawal has already been processed")
    INSUFFICIENT_BALANCE = (5003, "Insufficient balance", "User does not have sufficient balance for withdrawal")
    WITHDRAWAL_AMOUNT_TOO_SMALL = (5004, "Withdrawal amount too small", "Withdrawal amount is below minimum threshold")
    WITHDRAWAL_LIMIT_EXCEEDED = (5005, "Withdrawal limit exceeded", "Withdrawal amount exceeds daily/monthly limit")
    STRIPE_ACCOUNT_NOT_FOUND = (5006, "Stripe account not found", "User does not have a connected Stripe account")

    # Notification errors (6000-6099)
    NOTIFICATION_NOT_FOUND = (6001, "Notification not found", "Notification with specified ID does not exist")
    NOTIFICATION_ACCESS_DENIED = (6002, "Notification access denied", "User does not have permission to access this notification")
    FIREBASE_TOKEN_INVALID = (6003, "Firebase token invalid", "Firebase push notification token is invalid or expired")
    NOTIFICATION_SEND_FAILED = (6004, "Notification send failed", "Failed to send push notification")

    # Chat errors (7000-7099)
    CHAT_ROOM_NOT_FOUND = (7001, "Chat room not found", "Chat room with specified ID does not exist")
    MESSAGE_NOT_FOUND = (7002, "Message not found", "Message with specified ID does not exist")
    CHAT_ACCESS_DENIED = (7003, "Chat access denied", "User does not have permission to access this chat")
    MESSAGE_EDIT_DENIED = (7004, "Message edit denied", "User cannot edit this message")
    MESSAGE_DELETE_DENIED = (7005, "Message delete denied", "User cannot delete this message")
    CHAT_CREATION_FAILED = (7006, "Chat creation failed", "Failed to create new chat room")

    # Dashboard errors (8000-8099)
    DASHBOARD_NOT_FOUND = (8001, "Dashboard not found", "Dashboard with specified ID does not exist")
    DASHBOARD_ACCESS_DENIED = (8002, "Dashboard access denied", "User does not have permission to access this dashboard")
    DASHBOARD_CREATION_FAILED = (8003, "Dashboard creation failed", "Failed to create dashboard for user")

    # Validation errors (9000-9199)
    INVALID_DATA = (9001, "Invalid data", "Provided data is invalid or malformed")
    MISSING_REQUIRED_FIELD = (9002, "Missing required field", "Required field is missing from request")
    INVALID_DATE_FORMAT = (9003, "Invalid date format", "Date format is invalid")
    INVALID_TIME_FORMAT = (9004, "Invalid time format", "Time format is invalid")
    FIELD_TOO_LONG = (9005, "Field too long", "Field value exceeds maximum length")
    VALIDATION_ERROR = (9006, "Validation error", "Data validation failed")
    BAD_REQUEST = (9100, "Bad request", "Request format is invalid (e.g. JSON parsing error)")
    METHOD_NOT_ALLOWED = (9101, "Method not allowed", "HTTP method not allowed for this endpoint")
    CONFLICT_ERROR = (9102, "Conflict error", "Request could not be completed due to a data conflict")

    # System errors (9900-9999)
    INTERNAL_SERVER_ERROR = (9901, "Internal server error", "An unexpected error occurred on the server")
    DATABASE_CONNECTION_ERROR = (9902, "Database connection error", "Failed to connect to database")
    EXTERNAL_SERVICE_ERROR = (9903, "External service error", "External service is unavailable or returned an error")
    RATE_LIMIT_EXCEEDED = (9904, "Rate limit exceeded", "Too many requests, please try again later")
    MAINTENANCE_MODE = (9905, "Maintenance mode", "Service is temporarily unavailable for maintenance")
    STRIPE_SERVICE_ERROR = (9906, "Stripe service error", "Stripe API call failed")
    TIMEOUT_ERROR = (9907, "Timeout error", "External service did not respond in time")
    SYSTEM_SERVICE_UNAVAILABLE = (9908, "System service unavailable", "The requested system service is currently unavailable")
    GENERAL_SERVICE_UNAVAILABLE = (9909, "General service unavailable", "The requested service is currently unavailable")

    def __init__(self, code, title, description):
        self.code = code
        self.title = title
        self.description = description

    def raise_error(self, detail=None):
        """
        Creates and raises a ValidationError with an error code
        Usage: ErrorCode.PASSWORDS_DO_NOT_MATCH.raise_error()
        """
        from rest_framework import serializers
        error_message = detail or self.description
        raise serializers.ValidationError(f"{self.code}: {self.title}: {error_message}")

