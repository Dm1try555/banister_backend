# Banister Backend API Documentation

## 📋 Overview

Banister - это платформа для связи клиентов с поставщиками услуг. API поддерживает три роли пользователей:
- **customer** - клиенты
- **provider** - поставщики услуг  
- **management** - менеджеры

## 🔐 Authentication

### JWT Token Authentication
- Используйте JWT токены для аутентификации
- В поле Authorization вставляйте только токен (без "Bearer")
- Система автоматически добавит "Bearer " к вашему токену

### Примеры логинов для тестирования:

#### Customer (Клиент):
```
Email: shilovscky@i.ua
Password: shilovscky
```

#### Provider (Поставщик услуг):
```
Email: shilovscky2020@gmail.com
Password: shilovscky2020
```

### Пример использования:
1. Получите токен через `/api/v1/auth/login/customer/` или `/api/v1/auth/login/provider/`
2. Скопируйте значение `access` из ответа
3. Вставьте токен в поле Authorization в Swagger UI
4. Теперь вы можете использовать защищенные эндпоинты

---

## 👤 Authentication & Registration

### Registration Endpoints

#### Customer Registration
```
POST /api/v1/auth/register/customer/
```
**Body:**
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

#### Provider Registration
```
POST /api/v1/auth/register/provider/
```
**Body:**
```json
{
  "email": "provider@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "(555) 123-4567"
}
```

#### Management Registration
```
POST /api/v1/auth/register/management/
```
**Body:**
```json
{
  "email": "manager@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "Admin",
  "last_name": "Manager",
  "phone": "(555) 123-4567"
}
```

### Login Endpoints

#### Customer Login
```
POST /api/v1/auth/login/customer/
```
**Body:**
```json
{
  "email": "customer@example.com",
  "password": "password123"
}
```

#### Provider Login
```
POST /api/v1/auth/login/provider/
```
**Body:**
```json
{
  "email": "provider@example.com",
  "password": "password123"
}
```

#### Management Login
```
POST /api/v1/auth/login/management/
```
**Body:**
```json
{
  "email": "manager@example.com",
  "password": "password123"
}
```

### Profile Management

#### Get Profile
```
GET /api/v1/auth/profile/
```
**Headers:** `Authorization: <token>`

#### Update Profile (Full Update)
```
PUT /api/v1/auth/profile/
```
**Headers:** `Authorization: <token>`
**Body:**
```json
{
  "email": "newemail@example.com",
  "phone": "(555) 987-6543",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "About me"
  },
  "provider_profile": {
    "experience_years": 5,
    "hourly_rate": 50.00
  }
}
```

#### Update Profile (Partial Update)
```
PATCH /api/v1/auth/profile/
```
**Headers:** `Authorization: <token>`
**Body:** (только изменяемые поля)

#### Delete Account
```
DELETE /api/v1/auth/profile/
```
**Headers:** `Authorization: <token>`

### Password Reset

#### Request Password Reset
```
POST /api/v1/auth/password-reset/request/
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

#### Confirm Password Reset
```
POST /api/v1/auth/password-reset/confirm/
```
**Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewSecurePassword123!"
}
```

### Email Confirmation

#### Request Email Confirmation
```
POST /api/v1/auth/email-confirm/request/
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

#### Verify Email Confirmation
```
GET /api/v1/auth/email-confirm/verify/?token=<token>
```

### Token Management

#### Refresh Token
```
POST /api/v1/auth/token/refresh/
```
**Body:**
```json
{
  "refresh": "your-refresh-token-here"
}
```

#### Logout
```
POST /api/v1/auth/logout/
```
**Headers:** `Authorization: <token>`

---

## 📸 File Storage & Profile Photos

### Upload Profile Photo
```
POST /api/v1/files/profile-photo/upload/
```
**Headers:** `Authorization: <token>`
**Body:** `multipart/form-data`
- `photo`: Image file (JPEG, PNG, GIF, max 5MB)

### Get Profile Photo
```
GET /api/v1/files/profile-photo/
```
**Headers:** `Authorization: <token>`

### Delete Profile Photo
```
DELETE /api/v1/files/profile-photo/delete/
```
**Headers:** `Authorization: <token>`

---

## 🛠️ Services Management

### Create Service (Providers Only)
```
POST /api/v1/services/
```
**Headers:** `Authorization: <token>`
**Body:**
```json
{
  "title": "Web Development",
  "description": "Professional web development services",
  "price": 100.00,
}
```

### Get All Services
```
GET /api/v1/services/
```
**Query Parameters:**
- `search`: Search by title or description
- `ordering`: Sort by price, created_at
- `page`: Page number for pagination

### Get Service by ID
```
GET /api/v1/services/{id}/
```

### Update Service (Owner Only)
```
PUT /api/v1/services/{id}/
```
**Headers:** `Authorization: <token>`
**Body:** (updated fields)

### Delete Service (Owner Only)
```
DELETE /api/v1/services/{id}/
```
**Headers:** `Authorization: <token>`

---

## 📅 Bookings Management

### Create Booking (Customers Only)
```
POST /api/v1/bookings/
```
**Headers:** `Authorization: <token>`
**Body:**
```json
{
  "service": 1,
  "date": "2024-01-15T14:00:00Z",
  "status": "pending"
}
```

### Get User Bookings
```
GET /api/v1/bookings/
```
**Headers:** `Authorization: <token>`
- Customers see their own bookings
- Providers see bookings for their services

### Get Booking by ID
```
GET /api/v1/bookings/{id}/
```
**Headers:** `Authorization: <token>`

### Update Booking (Owner Only)
```
PUT /api/v1/bookings/{id}/
```
**Headers:** `Authorization: <token>`
**Body:** (updated fields)

### Delete Booking (Owner Only)
```
DELETE /api/v1/bookings/{id}/
```
**Headers:** `Authorization: <token>`

### Update Booking Status (Providers Only)
```
POST /api/v1/bookings/status/{booking_id}/
```
**Headers:** `Authorization: <token>`
**Body:**
```json
{
  "status": "confirmed"
}
```
**Available statuses:** `pending`, `confirmed`, `cancelled`, `completed`

---

## 💰 Payments (Ready for Implementation)

### Payment Endpoints
- `GET /api/v1/payments/` - Get payment history
- `POST /api/v1/payments/` - Create payment
- `GET /api/v1/payments/{id}/` - Get payment details
- `PUT /api/v1/payments/{id}/` - Update payment
- `DELETE /api/v1/payments/{id}/` - Delete payment

---

## 💸 Withdrawals (Ready for Implementation)

### Withdrawal Endpoints
- `GET /api/v1/withdrawals/` - Get withdrawal history
- `POST /api/v1/withdrawals/` - Request withdrawal
- `GET /api/v1/withdrawals/{id}/` - Get withdrawal details
- `PUT /api/v1/withdrawals/{id}/` - Update withdrawal
- `DELETE /api/v1/withdrawals/{id}/` - Delete withdrawal

---

## 💬 Messages & Chat (Ready for Implementation)

### Message Endpoints
- `GET /api/v1/message/` - Get messages
- `POST /api/v1/message/` - Send message
- `GET /api/v1/message/{id}/` - Get message details
- `PUT /api/v1/message/{id}/` - Update message
- `DELETE /api/v1/message/{id}/` - Delete message

---

## 📅 Schedules (Ready for Implementation)

### Schedule Endpoints
- `GET /api/v1/schedules/` - Get schedules
- `POST /api/v1/schedules/` - Create schedule
- `GET /api/v1/schedules/{id}/` - Get schedule details
- `PUT /api/v1/schedules/{id}/` - Update schedule
- `DELETE /api/v1/schedules/{id}/` - Delete schedule

---

## 📄 Documents (Ready for Implementation)

### Document Endpoints
- `GET /api/v1/documents/` - Get documents
- `POST /api/v1/documents/` - Upload document
- `GET /api/v1/documents/{id}/` - Get document details
- `PUT /api/v1/documents/{id}/` - Update document
- `DELETE /api/v1/documents/{id}/` - Delete document

---

## 👥 Admin Panel (Ready for Implementation)

### Admin Endpoints
- `GET /api/v1/users/` - Get all users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Get user details
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

---

## 📊 Dashboard (Ready for Implementation)

### Dashboard Endpoints
- `GET /api/v1/dashboard/` - Get dashboard data
- `GET /api/v1/dashboard/stats/` - Get statistics
- `GET /api/v1/dashboard/analytics/` - Get analytics

---

## 🌐 Public Core

### Public Services
- `GET /api/v1/public/services/` - Get public list of all services (no authentication required)

### Public Providers  
- `GET /api/v1/public/providers/` - Get public list of all providers (no authentication required)
- `GET /api/v1/public/providers/{id}/` - Get public provider information by ID (no authentication required)

---

## 🔧 Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "error_number": "ERROR_CODE",
    "error_message": "Human readable error message",
    "timestamp": "2024-01-01T12:00:00.000000+00:00"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_FAILED` - Authentication error
- `TOKEN_MISSING` - Missing authentication token
- `PERMISSION_DENIED` - Insufficient permissions
- `VALIDATION_ERROR` - Data validation error
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict
- `UNKNOWN_ERROR` - Unexpected server error

---

## 📝 Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Success message"
}
```

### Pagination Response
```json
{
  "success": true,
  "data": {
    "results": [
      // Items
    ],
    "count": 100,
    "next": "http://api.example.com/endpoint/?page=2",
    "previous": null
  },
  "message": "Success message"
}
```

---

## 🚀 Getting Started

### 1. Start the Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 2. Access Swagger UI
Open your browser and go to: `http://localhost:8000/swagger/`

### 3. Register a User
Use one of the registration endpoints to create an account

### 4. Login
Use the login endpoint to get your JWT token

### 5. Use Protected Endpoints
Insert your token in the Authorization field in Swagger UI

---

## 📋 Features Status

### ✅ Completed Features
- [x] User registration (customer, provider, management)
- [x] User authentication (login/logout)
- [x] JWT token management
- [x] Profile management (CRUD)
- [x] Password reset (6-digit code system)
- [x] Email confirmation
- [x] Profile photo upload/management
- [x] Services CRUD (providers only)
- [x] Bookings CRUD (customers create, providers manage)
- [x] Booking status management
- [x] Error handling system
- [x] Swagger UI documentation
- [x] File storage with MinIO
- [x] Image processing and validation

### 🔄 In Progress
- [ ] Payment processing
- [ ] Withdrawal system
- [ ] Messaging system
- [ ] Schedule management
- [ ] Document management
- [ ] Admin panel
- [ ] Dashboard analytics
- [ ] Public API endpoints

### 📋 Planned Features
- [ ] Real-time notifications
- [ ] Advanced search and filtering
- [ ] Rating and review system
- [ ] Multi-language support
- [ ] Mobile app API endpoints
- [ ] Webhook system
- [ ] Advanced analytics
- [ ] Bulk operations
- [ ] Export functionality
- [ ] API rate limiting
- [ ] Caching system
- [ ] Background tasks
- [ ] Email templates
- [ ] SMS integration
- [ ] Social media login
- [ ] Two-factor authentication
- [ ] Audit logging
- [ ] Data backup system
- [ ] Performance monitoring
- [ ] Security enhancements

---

## 🔒 Security Features

- JWT token authentication
- Password hashing with Django's built-in system
- Input validation and sanitization
- File upload security (type and size validation)
- CORS configuration
- Rate limiting
- Error handling without exposing sensitive information
- Transaction-based database operations

---

## 🛠️ Technical Stack

- **Backend:** Django 5.2
- **API Framework:** Django REST Framework
- **Authentication:** JWT (Simple JWT)
- **Documentation:** Swagger/OpenAPI (drf-yasg)
- **File Storage:** MinIO
- **Database:** PostgreSQL
- **Image Processing:** Pillow
- **Error Handling:** Custom error handling system
- **Validation:** Django REST Framework serializers
- **Testing:** Django test framework (ready for implementation)

---

## 📞 Support

For technical support or questions about the API, please contact:
- Email: contact@example.com
- Documentation: http://localhost:8000/swagger/
- GitHub: [Repository URL]

---

*Last updated: August 2, 2024* 