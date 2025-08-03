# API Документация Banister

## 📋 Обзор

API Banister предоставляет полный набор эндпоинтов для управления пользователями, аутентификации и администрирования системы. Все эндпоинты используют RESTful архитектуру и возвращают JSON ответы.

## 🔐 Аутентификация

### JWT Токены

Система использует JWT (JSON Web Tokens) для аутентификации:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin"
}
```

### Использование токенов

Добавьте токен в заголовок Authorization:
```
Authorization: Bearer <access_token>
```

## 👥 Регистрация пользователей

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
    }
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

### Вход для менеджеров поддержки
```http
POST /api/v1/auth/login/management/
```

### Вход для администраторов
```http
POST /api/v1/auth/login/admin/
```

### Вход для супер-администраторов
```http
POST /api/v1/auth/login/superadmin/
```

### Вход для бухгалтеров
```http
POST /api/v1/auth/login/accountant/
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
    "role": "customer",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "bio": "Software developer"
    },
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

### Удаление аккаунта
```http
DELETE /api/v1/auth/profile/
Authorization: Bearer <access_token>
```

## 🔄 Обновление токенов

### Обновление access токена
```http
POST /api/v1/auth/token/refresh/
```

**Тело запроса:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ответ:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

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

## 👨‍💼 Административная система

### Создание администраторов

#### Создание Admin
```http
POST /api/v1/auth/admin/create/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "email": "admin@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "first_name": "Admin",
  "last_name": "User",
  "phone": "(555) 123-4567",
  "permissions": ["user_management", "service_management"]
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Admin user created successfully",
  "data": {
    "id": 119,
    "email": "admin@example.com",
    "role": "admin",
    "profile": {
      "first_name": "Admin",
      "last_name": "User"
    },
    "permissions": ["user_management", "service_management"]
  }
}
```

#### Создание Accountant
```http
POST /api/v1/auth/admin/create-accountant/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "email": "accountant@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "first_name": "Accountant",
  "last_name": "User",
  "phone": "(555) 123-4567"
}
```

#### Создание Support Manager
```http
POST /api/v1/auth/admin/create-support/
Authorization: Bearer <super_admin_token>
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

### Управление администраторами

#### Список Admin (только role='admin')
```http
GET /api/v1/auth/admin/list/
Authorization: Bearer <super_admin_token>
```

**Ответ:**
```json
{
  "success": true,
  "message": "Admin users list retrieved successfully",
  "data": {
    "admin_users": [
      {
        "id": 119,
        "email": "admin@example.com",
        "role": "admin",
        "profile": {
          "first_name": "Admin",
          "last_name": "User"
        }
      }
    ]
  }
}
```

#### Удаление Admin
```http
DELETE /api/v1/auth/admin/list/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "user_id": 119
}
```

### CRUD для Accountant

#### Список бухгалтеров
```http
GET /api/v1/auth/accountant/
Authorization: Bearer <super_admin_token>
```

#### Обновление бухгалтера
```http
PUT /api/v1/auth/accountant/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "user_id": 120,
  "is_active": true
}
```

#### Удаление бухгалтера
```http
DELETE /api/v1/auth/accountant/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "user_id": 120
}
```

### CRUD для Support Manager

#### Список менеджеров поддержки
```http
GET /api/v1/auth/support-manager/
Authorization: Bearer <super_admin_token>
```

#### Обновление менеджера поддержки
```http
PUT /api/v1/auth/support-manager/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "user_id": 121,
  "is_active": true
}
```

#### Удаление менеджера поддержки
```http
DELETE /api/v1/auth/support-manager/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "user_id": 121
}
```

## 🔐 Управление разрешениями

### Детальная информация о разрешениях

#### Получение списка админов с разрешениями
```http
GET /api/v1/auth/admin/permissions/detail/
Authorization: Bearer <super_admin_token>
```

**Ответ:**
```json
{
  "success": true,
  "message": "Admin users with permissions retrieved successfully",
  "data": {
    "admin_users": [
      {
        "id": 119,
        "email": "admin@example.com",
        "role": "admin",
        "profile": {
          "first_name": "Admin",
          "last_name": "User"
        },
        "permissions": [
          "user_management",
          "service_management"
        ]
      }
    ]
  }
}
```

#### Массовое обновление разрешений
```http
POST /api/v1/auth/admin/permissions/detail/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "updates": [
    {
      "admin_user_id": 119,
      "permissions": ["user_management"],
      "action": "grant"
    },
    {
      "admin_user_id": 119,
      "permissions": ["service_management"],
      "action": "revoke"
    }
  ]
}
```

#### Проверка разрешений
```http
PUT /api/v1/auth/admin/permissions/detail/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "admin_user_id": 119,
  "permissions": ["user_management", "service_management"]
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Permission check completed successfully",
  "data": {
    "admin_user": {
      "id": 119,
      "email": "admin@example.com",
      "role": "admin"
    },
    "permission_status": {
      "user_management": true,
      "service_management": false
    },
    "all_permissions": ["user_management"]
  }
}
```

#### Сброс всех разрешений
```http
DELETE /api/v1/auth/admin/permissions/detail/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "admin_user_id": 119
}
```

### Гранулярное управление разрешениями

#### Предоставление разрешений
```http
POST /api/v1/auth/admin/permissions/grant/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "admin_user_id": 119,
  "permissions": ["user_management", "service_management"]
}
```

#### Отзыв разрешений
```http
POST /api/v1/auth/admin/permissions/revoke/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "admin_user_id": 119,
  "permissions": ["service_management"]
}
```

#### Список разрешений пользователя
```http
GET /api/v1/auth/admin/permissions/list/?admin_user_id=119
Authorization: Bearer <super_admin_token>
```

**Ответ:**
```json
{
  "success": true,
  "message": "Admin permissions retrieved successfully",
  "data": {
    "admin_user": {
      "id": 119,
      "email": "admin@example.com",
      "role": "admin"
    },
    "permissions": [
      {
        "id": 1,
        "permission": "user_management",
        "is_active": true,
        "granted_by": "superadmin@example.com",
        "granted_at": "2025-08-03T18:40:50.547748+00:00"
      }
    ]
  }
}
```

#### Удаление конкретного разрешения
```http
DELETE /api/v1/auth/admin/permissions/delete/
Authorization: Bearer <super_admin_token>
```

**Тело запроса:**
```json
{
  "admin_user_id": 119,
  "permission": "service_management"
}
```

## 🚨 Обработка ошибок

Все ошибки возвращаются в стандартизированном формате:

```json
{
  "success": false,
  "error_number": "ERROR_CODE",
  "error_message": "Описание ошибки",
  "timestamp": "2025-08-03T18:40:50.547748+00:00"
}
```

### Коды ошибок

| Код | HTTP Статус | Описание |
|-----|-------------|----------|
| `ACCESS_DENIED` | 403 | Отказано в доступе |
| `MISSING_FIELD` | 400 | Отсутствует обязательное поле |
| `USER_NOT_FOUND` | 404 | Пользователь не найден |
| `USER_EXISTS` | 400 | Пользователь уже существует |
| `PASSWORD_MISMATCH` | 400 | Пароли не совпадают |
| `WEAK_PASSWORD` | 400 | Слабый пароль |
| `INVALID_PERMISSION` | 400 | Неверное разрешение |
| `INVALID_ACTION` | 400 | Неверное действие |
| `CANNOT_DELETE_SELF` | 400 | Нельзя удалить свой аккаунт |
| `SERVER_ERROR` | 500 | Ошибка сервера |

## 📊 Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс создан |
| 204 | Успешное удаление |
| 400 | Ошибка валидации |
| 401 | Не авторизован |
| 403 | Доступ запрещен |
| 404 | Ресурс не найден |
| 500 | Ошибка сервера |

## 🔧 Swagger документация

Интерактивная документация доступна по адресу:
```
http://localhost:8000/swagger/
```

Документация организована по разделам:
- **Login** - Вход в систему
- **Registration** - Регистрация
- **Profile** - Управление профилем
- **Password Reset** - Сброс пароля
- **Email confirmation** - Подтверждение email
- **Admin** - Управление администраторами
- **Accountant** - Управление бухгалтерами
- **Support Manager** - Управление менеджерами поддержки
- **Admin Permissions** - Управление разрешениями

## 📝 Примеры использования

### Полный цикл создания администратора

1. **Вход как Super Admin**
```bash
curl -X POST /api/v1/auth/login/superadmin/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@example.com",
    "password": "securepass123"
  }'
```

2. **Создание Admin**
```bash
curl -X POST /api/v1/auth/admin/create/ \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "first_name": "Admin",
    "last_name": "User",
    "phone": "(555) 123-4567",
    "permissions": ["user_management", "service_management"]
  }'
```

3. **Предоставление дополнительных разрешений**
```bash
curl -X POST /api/v1/auth/admin/permissions/grant/ \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_user_id": 119,
    "permissions": ["financial_management"]
  }'
```

4. **Проверка разрешений**
```bash
curl -X PUT /api/v1/auth/admin/permissions/detail/ \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_user_id": 119,
    "permissions": ["user_management", "service_management", "financial_management"]
  }'
```

## 🔒 Безопасность

### Рекомендации

1. **Используйте HTTPS** в продакшене
2. **Храните токены безопасно** - не в localStorage
3. **Обновляйте токены** перед истечением срока
4. **Валидируйте данные** на клиенте и сервере
5. **Логируйте важные операции** для аудита

### Rate Limiting

Система включает защиту от брутфорс атак:
- Ограничение попыток входа
- Блокировка IP после множественных неудачных попыток
- Автоматическое разблокирование через время

### Валидация данных

Все входные данные валидируются:
- Email формат
- Сила пароля (минимум 8 символов)
- Обязательные поля
- Уникальность email 