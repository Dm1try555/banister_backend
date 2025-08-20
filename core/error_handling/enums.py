from enum import Enum


class ErrorCode(Enum):
    INVALID_CREDENTIALS = (1001, "Invalid credentials", "Username or password is incorrect")
    USER_NOT_FOUND = (1002, "User not found", "User with specified ID does not exist")
    TOKEN_EXPIRED = (1003, "Token expired", "Authentication token has expired")
    INVALID_TOKEN = (1004, "Invalid token", "Authentication token is invalid")
    PERMISSION_DENIED = (1005, "Permission denied", "You don't have permission to perform this action")
    
    BOOKING_NOT_FOUND = (2001, "Booking not found", "Booking with specified ID does not exist")
    BOOKING_CONFLICT = (2002, "Booking conflict", "Time slot is already booked")
    INVALID_BOOKING_TIME = (2003, "Invalid booking time", "Booking time is in the past or invalid")
    BOOKING_CANCELLED = (2004, "Booking cancelled", "This booking has been cancelled")
    
    SERVICE_NOT_FOUND = (3001, "Service not found", "Service with specified ID does not exist")
    SERVICE_UNAVAILABLE = (3002, "Service unavailable", "Service is currently unavailable")
    INVALID_SERVICE_PRICE = (3003, "Invalid price", "Service price must be positive")
    
    PAYMENT_FAILED = (4001, "Payment failed", "Payment processing failed")
    INSUFFICIENT_FUNDS = (4002, "Insufficient funds", "Not enough funds to complete payment")
    PAYMENT_NOT_FOUND = (4003, "Payment not found", "Payment with specified ID does not exist")
    INVALID_PAYMENT_METHOD = (4004, "Invalid payment method", "Payment method is not supported")
    
    DOCUMENT_NOT_FOUND = (4501, "Document not found", "Document with specified ID does not exist")
    DOCUMENT_ACCESS_DENIED = (4502, "Document access denied", "You don't have access to this document")
    INVALID_FILE_FORMAT = (4503, "Invalid file format", "File format is not supported")
    FILE_TOO_LARGE = (4504, "File too large", "File size exceeds maximum limit")
    
    WITHDRAWAL_NOT_FOUND = (5001, "Withdrawal not found", "Withdrawal with specified ID does not exist")
    INSUFFICIENT_BALANCE = (5002, "Insufficient balance", "Not enough balance for withdrawal")
    WITHDRAWAL_LIMIT_EXCEEDED = (5003, "Withdrawal limit exceeded", "Daily/monthly withdrawal limit exceeded")
    
    NOTIFICATION_NOT_FOUND = (6001, "Notification not found", "Notification with specified ID does not exist")
    NOTIFICATION_SEND_FAILED = (6002, "Notification send failed", "Failed to send notification")
    
    CHAT_NOT_FOUND = (7001, "Chat not found", "Chat with specified ID does not exist")
    MESSAGE_NOT_FOUND = (7002, "Message not found", "Message with specified ID does not exist")
    CHAT_ACCESS_DENIED = (7003, "Chat access denied", "You don't have access to this chat")
    
    SCHEDULE_NOT_FOUND = (8001, "Schedule not found", "Schedule with specified ID does not exist")
    SCHEDULE_CONFLICT = (8002, "Schedule conflict", "Schedule overlaps with existing schedule")
    INVALID_SCHEDULE_TIME = (8003, "Invalid schedule time", "Schedule time is invalid")
    
    INVALID_DATA = (9001, "Invalid data", "Provided data is invalid")
    MISSING_REQUIRED_FIELD = (9002, "Missing required field", "Required field is missing")
    INVALID_EMAIL_FORMAT = (9003, "Invalid email", "Email format is invalid")
    INVALID_PHONE_FORMAT = (9004, "Invalid phone", "Phone number format is invalid")
    
    DATABASE_ERROR = (9901, "Database error", "Database operation failed")
    EXTERNAL_SERVICE_ERROR = (9902, "External service error", "External service is unavailable")
    FILE_UPLOAD_ERROR = (9903, "File upload error", "File upload failed")
    RATE_LIMIT_EXCEEDED = (9904, "Rate limit exceeded", "Too many requests, please try again later")
    
    def __init__(self, code, title, description):
        self.code = code
        self.title = title
        self.description = description