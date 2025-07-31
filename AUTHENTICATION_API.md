# API Документация - Система Авторизации

## Обзор

Полная система авторизации с поддержкой регистрации, входа, восстановления пароля и управления профилем для трех ролей: customer, provider, management.

## Базовый URL
```
http://localhost:8000/api/v1/auth/
```

## Endpoints

### 1. Регистрация

#### Customer Registration
```http
POST /auth/register/customer/
```

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
      "bio": ""
    }
  },
  "message": "Customer registered successfully"
}
```

#### Provider Registration
```http
POST /auth/register/provider/
```

**Request Body:** (аналогично customer, но создается provider_profile)

#### Management Registration
```http
POST /auth/register/management/
```

**Request Body:** (аналогично customer)

### 2. Авторизация

#### Customer Login
```http
POST /auth/login/customer/
```

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
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "role": "customer"
}
```

#### Provider Login
```http
POST /auth/login/provider/
```

#### Management Login
```http
POST /auth/login/management/
```

### 3. Обновление токенов

#### Refresh Token
```http
POST /auth/token/refresh/
```

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

### 4. Восстановление пароля

#### Запрос сброса пароля
```http
POST /auth/password-reset/
```

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

#### Подтверждение сброса пароля
```http
POST /auth/password-reset/confirm/
```

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

### 5. Профиль пользователя

#### Получить профиль
```http
GET /auth/profile/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone": "(555) 123-4567",
  "role": "customer",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "My bio"
  },
  "profile_photo_url": "https://example.com/photo.jpg",
  "has_required_profile_photo": true
}
```

#### Обновить профиль (PUT - полное обновление)
```http
PUT /auth/profile/
Authorization: Bearer <access_token>
```

**Request Body (Customer):**
```json
{
  "email": "newemail@example.com",
  "phone": "(555) 123-4567",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Updated bio"
  }
}
```

**Request Body (Provider):**
```json
{
  "email": "provider@example.com",
  "phone": "(555) 123-4567",
  "profile": {
    "first_name": "Jane",
    "last_name": "Smith",
    "bio": "Provider bio"
  },
  "provider_profile": {
    "experience_years": 5,
    "hourly_rate": 50.00
  }
}
```

#### Обновить профиль (PATCH - частичное обновление)
```http
PATCH /auth/profile/
Authorization: Bearer <access_token>
```

#### Удалить аккаунт
```http
DELETE /auth/profile/
Authorization: Bearer <access_token>
```

**Response (204):** No Content

### 6. Логаут

#### Logout
```http
POST /auth/logout/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### 7. Email подтверждение

#### Запрос подтверждения email
```http
POST /auth/email-confirm/request/
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### Подтверждение email
```http
GET /auth/email-confirm/verify/?token=email-confirmation-token
```

## Валидация данных

### Пароли
- Минимум 8 символов
- Должен содержать хотя бы одну букву
- Должен содержать хотя бы одну цифру

### Имена и фамилии (US)
- Только буквы, пробелы, дефисы и апострофы
- Минимум 1 символ, максимум 50 символов
- Поддерживает составные имена: "Mary-Jane", "O'Connor"

### Email
- Должен быть уникальным
- Валидный формат email

### Телефон (US)
- Стандартный формат: (XXX) XXX-XXXX
- С кодом страны: +1 (XXX) XXX-XXXX
- Только цифры: 10 или 11 цифр (с кодом страны)
- Поддерживает форматирование: скобки, дефисы, пробелы

## Безопасность

### Rate Limiting
- Анонимные пользователи: 100 запросов/час
- Авторизованные пользователи: 1000 запросов/час

### JWT Токены
- Access Token: 60 минут (настраивается)
- Refresh Token: 1 день (настраивается)

### Восстановление пароля
- Токен действителен 1 час
- Одноразовое использование
- Автоматическое удаление старых токенов

## Коды ошибок

### Общие ошибки
- `EMAIL_REQUIRED` - Email обязателен
- `USER_NOT_FOUND` - Пользователь не найден
- `INVALID_TOKEN` - Недействительный токен
- `EXPIRED_TOKEN` - Токен истек
- `PASSWORDS_DONT_MATCH` - Пароли не совпадают
- `WEAK_PASSWORD` - Слабый пароль
- `EMAIL_ALREADY_EXISTS` - Email уже существует

### Ошибки авторизации
- `AUTHENTICATION_ERROR` - Ошибка аутентификации
- `AUTH_ERROR` - Общая ошибка авторизации

### Ошибки профиля
- `PROFILE_PHOTO_REQUIRED` - Требуется фото профиля
- `SERVER_ERROR` - Ошибка сервера

## Примеры использования

### Полный цикл регистрации и авторизации

1. **Регистрация customer:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "(555) 123-4567"
  }'
```

2. **Авторизация:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'
```

3. **Получение профиля:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

4. **Обновление токена:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

5. **Восстановление пароля:**
```bash
# Запрос сброса
curl -X POST http://localhost:8000/api/v1/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'

# Подтверждение сброса
curl -X POST http://localhost:8000/api/v1/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset-token-from-email",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
  }'
```

## Настройки

### Переменные окружения
```env
# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@banister.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

Система авторизации полностью готова к использованию! 