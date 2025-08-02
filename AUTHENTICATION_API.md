# Authentication API Documentation

## Overview
This document describes the authentication and user management API endpoints for the Banister backend system, specifically designed for American users with US-specific validations.

## Base URL
```
http://localhost:8000/api/v1/auth/
```

## Authentication
All endpoints except registration and login require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Registration Endpoints

### Customer Registration
**POST** `/register/customer/`

Register a new customer account.

**Request Body:**
```json
{
  "email": "customer@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "(555) 123-4567"
}
```

**Supported Phone Formats:**
- `(555) 123-4567` - Standard US format
- `+1 (555) 123-4567` - With country code
- `555-123-4567` - With hyphens
- `555.123.4567` - With dots
- `555 123 4567` - With spaces
- `123-4567` - Local number (7 digits)
- `5551234567` - No formatting (10 digits)
- `+1-555-123-4567` - International format
- `1-555-123-4567` - With country code prefix

**Validation Rules:**
- Email: Must be valid US email format (gmail.com, yahoo.com, hotmail.com, outlook.com, aol.com, or custom domain)
- Password: Minimum 8 characters, must contain at least one letter and one number
- First/Last Name: Only letters, spaces, hyphens, and apostrophes allowed
- Phone: Must be valid US phone number format (7, 10, 11, 12, or 13 digits)

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "customer@example.com",
    "phone": "(555) 123-4567",
    "role": "customer",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "bio": null
    },
    "profile_photo_url": null,
    "has_required_profile_photo": false,
    "timestamp": "2025-01-31T19:36:59.900765+00:00"
  },
  "message": "Customer registered successfully"
}
```

### Provider Registration
**POST** `/register/provider/`

Register a new provider account.

**Request Body:**
```json
{
  "email": "provider@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1 (555) 123-4567"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "provider@example.com",
    "phone": "+1 (555) 123-4567",
    "role": "provider",
    "profile": {
      "first_name": "Jane",
      "last_name": "Smith",
      "bio": null
    },
    "provider_profile": {
      "experience_years": 0,
      "hourly_rate": 0.0
    },
    "profile_photo_url": null,
    "has_required_profile_photo": false,
    "timestamp": "2025-01-31T19:36:59.900765+00:00"
  },
  "message": "Provider registered successfully"
}
```

### Management Registration
**POST** `/register/management/`

Register a new management account.

**Request Body:**
```json
{
  "email": "manager@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "Admin",
  "last_name": "Manager",
  "phone": "555-123-4567"
}
```

## Login Endpoints

### Customer Login
**POST** `/login/customer/`

Authenticate a customer user.

**Request Body:**
```json
{
  "email": "customer@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "customer"
}
```

### Provider Login
**POST** `/login/provider/`

Authenticate a provider user.

**Request Body:**
```json
{
  "email": "provider@example.com",
  "password": "password123"
}
```

### Management Login
**POST** `/login/management/`

Authenticate a management user.

**Request Body:**
```json
{
  "email": "manager@example.com",
  "password": "password123"
}
```

## Profile Management

### Get Profile
**GET** `/profile/`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "customer@example.com",
  "phone": "(555) 123-4567",
  "role": "customer",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Professional customer"
  },
  "profile_photo_url": "https://example.com/photos/profile.jpg",
  "has_required_profile_photo": true,
  "timestamp": "2025-01-31T19:36:59.900765+00:00"
}
```

### Update Profile (Full Update)
**PUT** `/profile/`

Update user profile with full data replacement.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "phone": "555.123.4567",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Updated bio"
  }
}
```

**Validation Rules:**
- Email: Must be valid US email format and unique (except for current user)
- Phone: Must be valid US phone number format
- First/Last Name: Only letters, spaces, hyphens, and apostrophes allowed
- Bio: Maximum 500 characters
- **Role: Cannot be changed via this endpoint (security restriction)**

**Response (200):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "phone": "555.123.4567",
  "role": "customer",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Updated bio"
  },
  "profile_photo_url": "https://example.com/photos/profile.jpg",
  "has_required_profile_photo": true,
  "timestamp": "2025-01-31T19:36:59.900765+00:00"
}
```

**Error Response (400) - Role Change Attempt:**
```json
{
  "success": false,
  "error": {
    "error_number": "ROLE_CHANGE_NOT_ALLOWED",
    "error_message": "Role cannot be changed via profile update"
  }
}
```

### Update Profile (Partial Update)
**PATCH** `/profile/`

Update user profile with partial data.

**Request Body:**
```json
{
  "phone": "555 123 4567",
  "profile": {
    "bio": "New bio text"
  }
}
```

**Validation Rules:**
- Same validation as PUT method
- **Role: Cannot be changed via this endpoint (security restriction)**

**Error Response (400) - Role Change Attempt:**
```json
{
  "success": false,
  "error": {
    "error_number": "ROLE_CHANGE_NOT_ALLOWED",
    "error_message": "Role cannot be changed via profile update"
  }
}
```

### Delete Profile
**DELETE** `/profile/`

Delete user account and all associated data.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
```
No Content
```

## Profile Photo Management

### Upload/Change Profile Photo
**POST** `/api/v1/files/profile-photo/upload/`

Upload or change user's profile photo. This endpoint automatically handles both first-time uploads and photo replacements.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
photo: [file] - Profile photo file (JPEG, PNG, GIF, max 5MB)
```

**Supported File Types:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)

**File Size Limit:** 5 MB

**Response (200) - First Upload:**
```json
{
  "success": true,
  "message": "Profile photo uploaded successfully",
  "timestamp": "2025-01-31T19:36:59.900765+00:00",
  "data": {
    "id": "1df4cf9b-ef49-42b5-8bb9-5bc03052600c",
    "user": {
      "id": 112,
      "email": "provider@example.com",
      "phone": "1234567890",
      "role": "provider",
      "profile": {
        "first_name": "John",
        "last_name": "Doe",
        "bio": ""
      },
      "provider_profile": {
        "experience_years": 0,
        "hourly_rate": "0.00"
      },
      "profile_photo_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg",
      "has_required_profile_photo": true
    },
    "file_storage": {
      "id": "300917b4-91dd-4abc-bb9e-504fadd38461",
      "file_name": "profile_photo_112",
      "original_name": "profile.jpg",
      "file_type": "profile_photo",
      "bucket_name": "profile-photos",
      "object_key": "112/profile_photo/20250131_193659_e1f2b717.jpg",
      "file_size": 107236,
      "content_type": "image/jpeg",
      "is_public": true,
      "created_at": "2025-01-31T19:36:59.444490Z",
      "updated_at": "2025-01-31T19:36:59.444508Z",
      "file_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg",
      "public_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg"
    },
    "is_active": true,
    "created_at": "2025-01-31T19:36:59.453362Z",
    "updated_at": "2025-01-31T19:36:59.453418Z",
    "photo_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg"
  }
}
```

**Response (200) - Photo Change:**
```json
{
  "success": true,
  "message": "Profile photo changed successfully",
  "timestamp": "2025-01-31T19:36:59.900765+00:00",
  "data": {
    // Same structure as above
  }
}
```

**Error Responses:**

**Invalid File Format (400):**
```json
{
  "success": false,
  "error": {
    "error_number": "INVALID_IMAGE",
    "error_message": "Invalid image format"
  }
}
```

**File Too Large (400):**
```json
{
  "success": false,
  "error": {
    "error_number": "FILE_TOO_LARGE",
    "error_message": "File size must not exceed 5 MB"
  }
}
```

**Upload Error (500):**
```json
{
  "success": false,
  "error": {
    "error_number": "PROFILE_PHOTO_UPLOAD_ERROR",
    "error_message": "Error uploading profile photo: [details]"
  }
}
```

**Features:**
- ✅ **Automatic Image Processing:** Images are automatically resized for optimal storage
- ✅ **Duplicate Handling:** Automatically deletes old photos when uploading new ones
- ✅ **File Validation:** Validates file type, size, and format
- ✅ **MinIO Storage:** Files are stored in MinIO object storage
- ✅ **Public URLs:** Generated URLs are publicly accessible
- ✅ **Database Consistency:** Maintains referential integrity between User, ProfilePhoto, and FileStorage models

## Password Management

### Request Password Reset
**POST** `/password-reset/`

Request a password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "email": "user@example.com"
  },
  "message": "Password reset link sent to your email"
}
```

### Confirm Password Reset
**POST** `/password-reset/confirm/`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "email": "user@example.com"
  },
  "message": "Password reset successful"
}
```

## Token Management

### Refresh Token
**POST** `/token/refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh": "your-refresh-token-here"
}
```

**Response (200):**
```json
{
  "access": "new-access-token-here"
}
```

### Logout
**POST** `/logout/`

Logout user (client-side token invalidation).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logout successful. Please clear your token in Swagger UI or client application."
}
```

### Clear Token (Swagger UI)
**GET** `/clear-token/`

Get JavaScript code to automatically clear token in Swagger UI.

**Response (200):**
```javascript
// JavaScript code to clear token in Swagger UI
if (typeof window !== 'undefined' && window.ui) {
    window.ui.preauthorizeApiKey('Bearer', '');
    alert('Token cleared successfully!');
} else {
    console.log('Please manually clear the token in Swagger UI');
}
```

**Usage in Swagger UI:**
1. Execute this endpoint in Swagger UI
2. The JavaScript will automatically clear the Bearer token
3. You can then log in with a different account

## Email Confirmation

### Request Email Confirmation
**POST** `/email-confirm/request/`

Request email confirmation link.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Email confirmation link sent"
}
```

### Verify Email Confirmation
**GET** `/email-confirm/verify/?token=confirmation-token`

Verify email using token from link.

**Response (200):**
```json
{
  "success": true,
  "message": "Email confirmed successfully"
}
```

## Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "error": {
    "error_number": "VALIDATION_ERROR",
    "error_message": {
      "email": ["Please enter a valid email address."],
      "phone": ["Please enter a valid US phone number. Supported formats: (555) 123-4567, +1 (555) 123-4567, 555-123-4567, 555.123.4567, 555 123 4567, 123-4567, 5551234567"],
      "profile": {
        "first_name": ["First name can only contain letters, spaces, hyphens, and apostrophes."],
        "last_name": ["Last name can only contain letters, spaces, hyphens, and apostrophes."],
        "bio": ["Bio cannot exceed 500 characters."]
      }
    }
  }
}
```

### Authentication Error (401)
```json
{
  "success": false,
  "error": {
    "error_number": "AUTHENTICATION_ERROR",
    "error_message": "Invalid email or password"
  }
}
```

### User Not Found (404)
```json
{
  "success": false,
  "error": {
    "error_number": "USER_NOT_FOUND",
    "error_message": "User with this email not found"
  }
}
```

### Server Error (500)
```json
{
  "success": false,
  "error": {
    "error_number": "SERVER_ERROR",
    "error_message": "Internal server error"
  }
}
```

### Profile Photo Required Error (400)
```json
{
  "success": false,
  "error": {
    "error_number": "PROFILE_PHOTO_REQUIRED",
    "error_message": "Profile photo is required for this user role"
  }
}
```

### Role Change Not Allowed Error (400)
```json
{
  "success": false,
  "error": {
    "error_number": "ROLE_CHANGE_NOT_ALLOWED",
    "error_message": "Role cannot be changed via profile update"
  }
}
```

## Rate Limiting

All registration and login endpoints are rate-limited:
- Anonymous users: 5 requests per minute
- Authenticated users: 10 requests per minute

## Security Considerations

1. **Password Requirements:**
   - Minimum 8 characters
   - Must contain at least one letter and one number
   - Passwords are hashed using Django's built-in hashing

2. **Token Security:**
   - Access tokens expire after 5 minutes
   - Refresh tokens expire after 24 hours
   - Tokens are JWT-based for stateless authentication

3. **Email Validation:**
   - Supports common US email providers
   - Validates email format and uniqueness
   - Email confirmation required for full account access

4. **Phone Validation:**
   - Supports all common US phone number formats
   - Validates number length and country code
   - Flexible formatting for user convenience

5. **Name Validation:**
   - US-specific character validation
   - Supports common name formats with hyphens and apostrophes
   - Prevents injection of special characters

6. **Role Security:**
   - Role changes are blocked via profile update endpoints
   - Prevents unauthorized role escalation
   - Maintains user role integrity

7. **Profile Photo Security:**
   - Required for provider and management roles
   - Automatic validation of file types and sizes
   - Secure storage in MinIO with public access URLs
   - Automatic cleanup of old files when replacing photos

## Testing Examples

### Valid Phone Numbers:
- `(555) 123-4567`
- `+1 (555) 123-4567`
- `555-123-4567`
- `555.123.4567`
- `555 123 4567`
- `123-4567`
- `5551234567`
- `+1-555-123-4567`
- `1-555-123-4567`

### Invalid Phone Numbers:
- `123456` (too short)
- `123456789012345` (too long)
- `abc-def-ghij` (contains letters)
- `555-123-456` (wrong format)

### Valid Emails:
- `user@gmail.com`
- `user@yahoo.com`
- `user@hotmail.com`
- `user@outlook.com`
- `user@aol.com`
- `user@company.com`

### Valid Names:
- `John`
- `Mary-Jane`
- `O'Connor`
- `Jean-Pierre`
- `Van der Berg`

This API is specifically designed for American users with comprehensive validation for US phone numbers, email addresses, and name formats. 