# Административная система Banister

## 📋 Обзор

Система администрирования Banister предоставляет полный контроль над пользователями, разрешениями и системными настройками через API и консольные команды.

## 👥 Роли пользователей

### 1. Super Admin
- **Описание**: Полный доступ ко всем функциям системы
- **Права**: Создание, редактирование, удаление всех типов пользователей
- **Разрешения**: Все доступные разрешения автоматически
- **Вход**: `/api/v1/auth/login/superadmin/`

### 2. Admin
- **Описание**: Администраторы системы с ограниченными правами
- **Права**: Управление пользователями и услугами (в зависимости от разрешений)
- **Разрешения**: Назначаются Super Admin
- **Вход**: `/api/v1/auth/login/admin/`

### 3. Accountant
- **Описание**: Бухгалтеры с финансовыми правами
- **Права**: Управление финансовыми операциями, биллингом
- **Разрешения**: Финансовые разрешения по умолчанию
- **Вход**: `/api/v1/auth/login/accountant/`

### 4. Support Manager
- **Описание**: Сотрудники поддержки (бывший "Management")
- **Права**: Обработка запросов клиентов, управление поддержкой
- **Разрешения**: Разрешения поддержки по умолчанию
- **Вход**: `/api/v1/auth/login/management/`

## 🛠️ Создание административных ролей

### Консольные команды

#### Создание Super Admin
```bash
python manage.py create_superadmin --email superadmin@example.com --password securepass123
```
**Особенности:**
- Автоматически получает все доступные разрешения
- Создается с ролью `super_admin`
- Полный доступ к системе

#### Создание Admin
```bash
python manage.py create_admin --email admin@example.com --password securepass123 --permissions user_management service_management
```
**Особенности:**
- Создается с ролью `admin`
- Разрешения указываются через `--permissions`
- Доступ к управлению пользователями и услугами

#### Создание Accountant
```bash
python manage.py create_accountant --email accountant@example.com --password securepass123
```
**Особенности:**
- Создается с ролью `accountant`
- Автоматически получает финансовые разрешения
- Доступ к финансовым операциям

#### Создание Support Manager
```bash
python manage.py create_management --email support@example.com --password securepass123
```
**Особенности:**
- Создается с ролью `management`
- Автоматически получает разрешения поддержки
- Доступ к управлению поддержкой клиентов

### API эндпоинты (только для Super Admin)

#### Создание Admin
```bash
POST /api/v1/auth/admin/create/
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

#### Создание Accountant
```bash
POST /api/v1/auth/admin/create-accountant/
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
```bash
POST /api/v1/auth/admin/create-support/
{
  "email": "support@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "first_name": "Support",
  "last_name": "Manager",
  "phone": "(555) 123-4567"
}
```

## 📊 Управление администраторами

### Список администраторов

#### Получение списка Admin (только role='admin')
```bash
GET /api/v1/auth/admin/list/
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
        "phone": "(555) 123-4567",
        "role": "admin",
            "profile": {
          "first_name": "Admin",
          "last_name": "User",
          "bio": ""
        },
        "profile_photo_url": null,
        "has_required_profile_photo": false,
        "role_display": "Admin"
      }
    ]
  }
}
```

#### Удаление Admin
```bash
DELETE /api/v1/auth/admin/list/
{
  "user_id": 119
}
```

### CRUD для Accountant

#### Список бухгалтеров
```bash
GET /api/v1/auth/accountant/
```

#### Обновление бухгалтера
```bash
PUT /api/v1/auth/accountant/
{
  "user_id": 120,
  "is_active": true
}
```

#### Удаление бухгалтера
```bash
DELETE /api/v1/auth/accountant/
{
  "user_id": 120
}
```

### CRUD для Support Manager

#### Список менеджеров поддержки
```bash
GET /api/v1/auth/support-manager/
```

#### Обновление менеджера поддержки
```bash
PUT /api/v1/auth/support-manager/
{
  "user_id": 121,
  "is_active": true
}
```

#### Удаление менеджера поддержки
```bash
DELETE /api/v1/auth/support-manager/
{
  "user_id": 121
}
```

## 🔐 Управление разрешениями

### Доступные разрешения

| Разрешение | Описание |
|------------|----------|
| `user_management` | Управление пользователями |
| `service_management` | Управление услугами |
| `financial_management` | Финансовое управление |
| `support_management` | Управление поддержкой |
| `system_configuration` | Конфигурация системы |
| `data_analytics` | Аналитика данных |
| `content_moderation` | Модерация контента |
| `billing_management` | Управление биллингом |

### Детальная информация о разрешениях

#### Получение списка админов с разрешениями
```bash
GET /api/v1/auth/admin/permissions/detail/
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
        "phone": "(555) 123-4567",
        "role": "admin",
        "profile": {
          "first_name": "Admin",
          "last_name": "User",
          "bio": ""
        },
        "profile_photo_url": null,
        "has_required_profile_photo": false,
        "role_display": "Admin",
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
```bash
POST /api/v1/auth/admin/permissions/detail/
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
```bash
PUT /api/v1/auth/admin/permissions/detail/
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
```bash
DELETE /api/v1/auth/admin/permissions/detail/
{
  "admin_user_id": 119
}
```

### Гранулярное управление разрешениями

#### Предоставление разрешений
```bash
POST /api/v1/auth/admin/permissions/grant/
{
  "admin_user_id": 119,
  "permissions": ["user_management", "service_management"]
}
```

#### Отзыв разрешений
```bash
POST /api/v1/auth/admin/permissions/revoke/
{
  "admin_user_id": 119,
  "permissions": ["service_management"]
}
```

#### Список разрешений пользователя
```bash
GET /api/v1/auth/admin/permissions/list/?admin_user_id=119
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
```bash
DELETE /api/v1/auth/admin/permissions/delete/
{
  "admin_user_id": 119,
  "permission": "service_management"
}
```

## 🔧 Middleware

### RoleBasedAccessMiddleware
- Контролирует доступ к эндпоинтам на основе ролей
- Автоматически перенаправляет неавторизованных пользователей
- Логирует попытки несанкционированного доступа

### AdminPermissionMiddleware
- Проверяет разрешения администраторов для защищенных эндпоинтов
- Автоматически блокирует доступ без необходимых разрешений
- Логирует попытки доступа без разрешений

### AdminActivityLoggingMiddleware
- Логирует все административные действия
- Записывает время, пользователя, действие и детали
- Обеспечивает аудит безопасности

## 📝 Логирование

Все административные действия автоматически логируются:

```json
{
  "timestamp": "2025-08-03T18:40:50.547748+00:00",
  "user": "superadmin@example.com",
  "action": "admin_user_created",
  "details": {
    "created_user": "admin@example.com",
    "role": "admin",
    "permissions": ["user_management", "service_management"]
  }
}
```

## 🚨 Обработка ошибок

Система использует стандартизированный формат ошибок:

```json
{
  "success": false,
  "error_number": "ACCESS_DENIED",
  "error_message": "Access denied. Only super admin can create admin users.",
  "timestamp": "2025-08-03T18:40:50.547748+00:00"
}
```

### Коды ошибок

| Код | Описание |
|-----|----------|
| `ACCESS_DENIED` | Отказано в доступе |
| `MISSING_FIELD` | Отсутствует обязательное поле |
| `USER_NOT_FOUND` | Пользователь не найден |
| `USER_EXISTS` | Пользователь уже существует |
| `PASSWORD_MISMATCH` | Пароли не совпадают |
| `WEAK_PASSWORD` | Слабый пароль |
| `INVALID_PERMISSION` | Неверное разрешение |
| `INVALID_ACTION` | Неверное действие |
| `CANNOT_DELETE_SELF` | Нельзя удалить свой аккаунт |
| `SERVER_ERROR` | Ошибка сервера |

## 🔒 Безопасность

### Аутентификация
- JWT токены для безопасной аутентификации
- Автоматическое обновление токенов
- Защита от CSRF атак

### Авторизация
- Ролевая система доступа
- Гранулярные разрешения
- Проверка разрешений на уровне middleware

### Аудит
- Логирование всех административных действий
- Отслеживание изменений разрешений
- Мониторинг попыток несанкционированного доступа

## 📞 Поддержка

Для получения технической поддержки:
1. Обратитесь к менеджерам поддержки через соответствующие эндпоинты
2. Используйте административную панель для управления пользователями
3. Проверьте логи системы для диагностики проблем 