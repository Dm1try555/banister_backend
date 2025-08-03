# API Аутентификации Banister

## 📋 Обзор

Система аутентификации Banister предоставляет полный набор эндпоинтов для регистрации, входа, управления профилем и восстановления пароля. Система поддерживает 6 различных ролей пользователей с соответствующими эндпоинтами входа.

## 👥 Роли пользователей

### 1. Customer (Клиент)
- **Описание**: Обычные пользователи платформы
- **Вход**: `/api/v1/auth/login/customer/`
- **Регистрация**: `/api/v1/auth/register/customer/`

### 2. Provider (Поставщик услуг)
- **Описание**: Поставщики услуг на платформе
- **Вход**: `/api/v1/auth/login/provider/`
- **Регистрация**: `/api/v1/auth/register/provider/`

### 3. Support Manager (Менеджер поддержки)
- **Описание**: Сотрудники поддержки клиентов
- **Вход**: `/api/v1/auth/login/management/`
- **Регистрация**: `/api/v1/auth/register/management/`

### 4. Admin (Администратор)
- **Описание**: Администраторы системы
- **Вход**: `/api/v1/auth/login/admin/`
- **Создание**: Только через API или консольные команды

### 5. Super Admin (Супер-администратор)
- **Описание**: Супер-администраторы с полными правами
- **Вход**: `/api/v1/auth/login/superadmin/`
- **Создание**: Только через консольные команды

### 6. Accountant (Бухгалтер)
- **Описание**: Бухгалтеры с финансовыми правами
- **Вход**: `/api/v1/auth/login/accountant/`
- **Создание**: Только через API или консольные команды

## 🔐 JWT Аутентификация

### Структура токенов

При успешном входе система возвращает:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin"
}
```

### Использование токенов

Добавьте access токен в заголовок Authorization:

```
Authorization: Bearer <access_token>
```

### Обновление токенов

Используйте refresh токен для получения нового access токена:

```http
POST /api/v1/auth/token/refresh/
```

**Тело запроса:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 📝 Регистрация

### Регистрация клиента

```http
POST /api/v1/auth/register/customer/
```

**Тело запроса:**
```json
{
  "email": "customer@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "(555) 123-4567"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "id": 1,
    "email": "customer@example.com",
    "role": "customer",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "bio": ""
    },
    "profile_photo_url": null,
    "has_required_profile_photo": false
  }
}
```

### Регистрация поставщика

```http
POST /api/v1/auth/register/provider/
```

**Тело запроса:**
```json
{
  "email": "provider@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "(555) 123-4567"
}
```

### Регистрация менеджера поддержки

```http
POST /api/v1/auth/register/management/
```

**Тело запроса:**
```json
{
  "email": "support@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "first_name": "Support",
  "last_name": "Manager",
  "phone": "(555) 123-4567"
}
```

## 🔑 Вход в систему

### Вход для клиентов

```http
POST /api/v1/auth/login/customer/
```

**Тело запроса:**
```json
{
  "email": "customer@example.com",
  "password": "securepass123"
}
```

**Ответ:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "customer"
}
```

### Вход для поставщиков

```http
POST /api/v1/auth/login/provider/
```

**Тело запроса:**
```json
{
  "email": "provider@example.com",
  "password": "securepass123"
}
```

### Вход для менеджеров поддержки

```http
POST /api/v1/auth/login/management/
```

**Тело запроса:**
```json
{
  "email": "support@example.com",
  "password": "securepass123"
}
```

### Вход для администраторов

```http
POST /api/v1/auth/login/admin/
```

**Тело запроса:**
```json
{
  "email": "admin@example.com",
  "password": "securepass123"
}
```

### Вход для супер-администраторов

```http
POST /api/v1/auth/login/superadmin/
```

**Тело запроса:**
```json
{
  "email": "superadmin@example.com",
  "password": "securepass123"
}
```

### Вход для бухгалтеров

```http
POST /api/v1/auth/login/accountant/
```

**Тело запроса:**
```json
{
  "email": "accountant@example.com",
  "password": "securepass123"
}
```

## 👤 Управление профилем

### Получение профиля

```http
GET /api/v1/auth/profile/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "phone": "(555) 123-4567",
    "role": "customer",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "bio": "Software developer"
    },
    "provider_profile": null,
    "profile_photo_url": "https://example.com/photos/user.jpg",
    "has_required_profile_photo": true
  }
}
```

### Обновление профиля

```http
PUT /api/v1/auth/profile/
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "email": "newemail@example.com",
  "phone": "(555) 999-8888",
  "profile": {
    "first_name": "John",
    "last_name": "Smith",
    "bio": "Updated bio"
  }
}
```

**Особенности:**
- Роль пользователя не может быть изменена
- Для поставщиков доступно поле `provider_profile`
- Email должен быть уникальным

### Удаление аккаунта

```http
DELETE /api/v1/auth/profile/
Authorization: Bearer <access_token>
```

**Особенности:**
- Полностью удаляет пользователя и все связанные данные
- Для поставщиков и менеджеров требуется фото профиля
- Операция необратима

## 🔒 Сброс пароля

### Запрос кода сброса

```http
POST /api/v1/auth/password-reset/request/
```

**Тело запроса:**
```json
{
  "email": "user@example.com"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Reset code sent to your email",
  "data": {
    "email": "user@example.com"
  }
}
```

**Особенности:**
- Отправляет 6-значный код на email
- Код действителен 10 минут
- Можно запросить новый код через 1 минуту

### Подтверждение сброса пароля

```http
POST /api/v1/auth/password-reset/confirm/
```

**Тело запроса:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewSecurePassword123!"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Password reset successful",
  "data": {
    "email": "user@example.com"
  }
}
```

**Требования к паролю:**
- Минимум 8 символов
- Содержит буквы и цифры
- Не должен совпадать с предыдущим паролем

## 📧 Подтверждение email

### Запрос кода подтверждения

```http
POST /api/v1/auth/email-confirm/request/
```

**Тело запроса:**
```json
{
  "email": "user@example.com"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Confirmation code sent to your email",
  "data": {
    "email": "user@example.com"
  }
}
```

### Подтверждение email

```http
POST /api/v1/auth/email-confirm/verify/
```

**Тело запроса:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Email confirmed successfully",
  "data": {
    "email": "user@example.com"
  }
}
```

## 🚨 Обработка ошибок

### Стандартный формат ошибок

```json
{
  "success": false,
  "error_number": "ERROR_CODE",
  "error_message": "Описание ошибки",
  "timestamp": "2025-08-03T18:40:50.547748+00:00"
}
```

### Коды ошибок аутентификации

| Код | HTTP Статус | Описание |
|-----|-------------|----------|
| `AUTHENTICATION_FAILED` | 401 | Неверный email или пароль |
| `ROLE_MISMATCH` | 401 | Неверная роль для данного эндпоинта |
| `TOKEN_MISSING` | 401 | Отсутствует токен аутентификации |
| `TOKEN_INVALID` | 401 | Неверный или истекший токен |
| `USER_NOT_FOUND` | 404 | Пользователь не найден |
| `USER_EXISTS` | 400 | Пользователь с таким email уже существует |
| `PASSWORD_MISMATCH` | 400 | Пароли не совпадают |
| `WEAK_PASSWORD` | 400 | Слабый пароль |
| `INVALID_EMAIL` | 400 | Неверный формат email |
| `MISSING_FIELD` | 400 | Отсутствует обязательное поле |
| `INVALID_CODE` | 400 | Неверный код подтверждения |
| `CODE_EXPIRED` | 400 | Код истек |
| `EMAIL_NOT_VERIFIED` | 400 | Email не подтвержден |
| `PROFILE_PHOTO_REQUIRED` | 400 | Требуется фото профиля |

## 🔒 Безопасность

### Валидация данных

#### Email
- Должен быть в формате email
- Должен быть уникальным в системе
- Регистр не учитывается

#### Пароль
- Минимум 8 символов
- Рекомендуется: буквы, цифры, специальные символы
- Не должен совпадать с предыдущим паролем

#### Телефон
- Поддерживает различные форматы:
  - `(555) 123-4567`
  - `+1 (555) 123-4567`
  - `555-123-4567`
  - `555.123.4567`
  - `555 123 4567`
  - `123-4567`
  - `5551234567`

### Rate Limiting

Система включает защиту от брутфорс атак:

- **Регистрация**: 5 попыток в час
- **Вход**: 10 попыток в час
- **Сброс пароля**: 3 попытки в час
- **Подтверждение email**: 5 попыток в час

### Токены

#### Access Token
- Срок действия: 5 минут
- Содержит информацию о пользователе и роли
- Используется для доступа к защищенным эндпоинтам

#### Refresh Token
- Срок действия: 7 дней
- Используется для получения нового access токена
- Может быть отозван при выходе

## 📝 Примеры использования

### Полный цикл регистрации и входа

1. **Регистрация клиента**
```bash
curl -X POST /api/v1/auth/register/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "(555) 123-4567"
  }'
```

2. **Вход в систему**
```bash
curl -X POST /api/v1/auth/login/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "securepass123"
  }'
```

3. **Получение профиля**
```bash
curl -X GET /api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

4. **Обновление профиля**
```bash
curl -X PUT /api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "first_name": "John",
      "last_name": "Smith",
      "bio": "Updated bio"
    }
  }'
```

### Сброс пароля

1. **Запрос кода сброса**
```bash
curl -X POST /api/v1/auth/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

2. **Подтверждение сброса**
```bash
curl -X POST /api/v1/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456",
    "new_password": "NewSecurePassword123!"
  }'
```

### Обновление токенов

```bash
curl -X POST /api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

## 🔧 Технические детали

### Middleware

Система использует следующие middleware:

- **RoleBasedAccessMiddleware**: Контроль доступа на основе ролей
- **AdminPermissionMiddleware**: Проверка разрешений администраторов
- **AdminActivityLoggingMiddleware**: Логирование действий администраторов

### Логирование

Все важные операции логируются:

```json
{
  "timestamp": "2025-08-03T18:40:50.547748+00:00",
  "user": "user@example.com",
  "action": "user_login",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

### Транзакции

Все операции с пользователями выполняются в транзакциях для обеспечения целостности данных.

## 📞 Поддержка

Для получения поддержки по вопросам аутентификации:

1. Проверьте логи системы
2. Убедитесь в правильности формата данных
3. Проверьте срок действия токенов
4. Обратитесь к менеджерам поддержки через соответствующие эндпоинты 