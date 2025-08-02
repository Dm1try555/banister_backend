# Banister API Endpoints Overview

## 🔐 Authentication & Registration

### Registration
- `POST /api/v1/auth/register/customer/` - Customer registration
- `POST /api/v1/auth/register/provider/` - Provider registration  
- `POST /api/v1/auth/register/management/` - Management registration

### Login
- `POST /api/v1/auth/login/customer/` - Customer login
- `POST /api/v1/auth/login/provider/` - Provider login
- `POST /api/v1/auth/login/management/` - Management login

### Profile Management
- `GET /api/v1/auth/profile/` - Get profile
- `PUT /api/v1/auth/profile/` - Update profile (full)
- `PATCH /api/v1/auth/profile/` - Update profile (partial)
- `DELETE /api/v1/auth/profile/` - Delete account

### Password Reset
- `POST /api/v1/auth/password-reset/request/` - Request reset code
- `POST /api/v1/auth/password-reset/confirm/` - Confirm reset with code

### Email Confirmation
- `POST /api/v1/auth/email-confirm/request/` - Request confirmation
- `GET /api/v1/auth/email-confirm/verify/` - Verify confirmation

### Token Management
- `POST /api/v1/auth/token/refresh/` - Refresh token
- `POST /api/v1/auth/logout/` - Logout

---

## 📸 File Storage

### Profile Photos
- `POST /api/v1/files/profile-photo/upload/` - Upload photo
- `GET /api/v1/files/profile-photo/` - Get photo
- `DELETE /api/v1/files/profile-photo/delete/` - Delete photo

---

## 🛠️ Services

### Service Management
- `GET /api/v1/services/` - List all services
- `POST /api/v1/services/` - Create service (providers only)
- `GET /api/v1/services/{id}/` - Get service details
- `PUT /api/v1/services/{id}/` - Update service (owner only)
- `DELETE /api/v1/services/{id}/` - Delete service (owner only)

**Query Parameters:**
- `search` - Search by title/description
- `ordering` - Sort by price, created_at
- `page` - Pagination

---

## 📅 Bookings

### Booking Management
- `GET /api/v1/bookings/` - List user bookings
- `POST /api/v1/bookings/` - Create booking (customers only)
- `GET /api/v1/bookings/{id}/` - Get booking details
- `PUT /api/v1/bookings/{id}/` - Update booking (owner only)
- `DELETE /api/v1/bookings/{id}/` - Delete booking (owner only)
- `POST /api/v1/bookings/status/{booking_id}/` - Update status (providers only)

**Booking Statuses:** `pending`, `confirmed`, `cancelled`, `completed`

---

## 💰 Payments (Ready for Implementation)

- `GET /api/v1/payments/` - Payment history
- `POST /api/v1/payments/` - Create payment
- `GET /api/v1/payments/{id}/` - Payment details
- `PUT /api/v1/payments/{id}/` - Update payment
- `DELETE /api/v1/payments/{id}/` - Delete payment

---

## 💸 Withdrawals (Ready for Implementation)

- `GET /api/v1/withdrawals/` - Withdrawal history
- `POST /api/v1/withdrawals/` - Request withdrawal
- `GET /api/v1/withdrawals/{id}/` - Withdrawal details
- `PUT /api/v1/withdrawals/{id}/` - Update withdrawal
- `DELETE /api/v1/withdrawals/{id}/` - Delete withdrawal

---

## 💬 Messages (Ready for Implementation)

- `GET /api/v1/message/` - Get messages
- `POST /api/v1/message/` - Send message
- `GET /api/v1/message/{id}/` - Message details
- `PUT /api/v1/message/{id}/` - Update message
- `DELETE /api/v1/message/{id}/` - Delete message

---

## 📅 Schedules (Ready for Implementation)

- `GET /api/v1/schedules/` - Get schedules
- `POST /api/v1/schedules/` - Create schedule
- `GET /api/v1/schedules/{id}/` - Schedule details
- `PUT /api/v1/schedules/{id}/` - Update schedule
- `DELETE /api/v1/schedules/{id}/` - Delete schedule

---

## 📄 Documents (Ready for Implementation)

- `GET /api/v1/documents/` - Get documents
- `POST /api/v1/documents/` - Upload document
- `GET /api/v1/documents/{id}/` - Document details
- `PUT /api/v1/documents/{id}/` - Update document
- `DELETE /api/v1/documents/{id}/` - Delete document

---

## 👥 Admin Panel (Ready for Implementation)

- `GET /api/v1/users/` - Get all users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - User details
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

---

## 📊 Dashboard (Ready for Implementation)

- `GET /api/v1/dashboard/` - Dashboard data
- `GET /api/v1/dashboard/stats/` - Statistics
- `GET /api/v1/dashboard/analytics/` - Analytics

---

## 🌐 Public Core

### Public Services
- `GET /api/v1/public/services/` - Public list of all services (no auth required)

### Public Providers
- `GET /api/v1/public/providers/` - Public list of all providers (no auth required)
- `GET /api/v1/public/providers/{id}/` - Public provider information by ID (no auth required)

---

## 📚 Documentation

- `GET /swagger/` - Swagger UI documentation

---

## 🔐 Authentication Required

Most endpoints require JWT authentication. Add token to Authorization header:
```
Authorization: <your-jwt-token>
```

The system automatically adds "Bearer " prefix to your token.

---

## 📝 Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "error_number": "ERROR_CODE",
    "error_message": "Error description",
    "timestamp": "2024-01-01T12:00:00.000000+00:00"
  }
}
```

---

*Last updated: August 2, 2024* 