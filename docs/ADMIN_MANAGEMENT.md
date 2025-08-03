# 🎛️ Управление администраторами

Документация по системе управления администраторами в Banister Backend.

## 📋 Обзор

Система управления администраторами включает:
- **3 роли администраторов:** Admin, Super Admin, Accountant
- **Консольная команда** для создания суперадмина
- **API эндпоинты** для управления профилями и правами
- **Система прав доступа** с детальными разрешениями

## 👥 Роли администраторов

### Super Admin (Суперадмин)
- Полный доступ ко всем функциям системы
- Может создавать и управлять другими администраторами
- Может назначать и отзывать права доступа
- Доступ к финансовым отчетам и системным настройкам

### Admin (Администратор)
- Ограниченный доступ на основе назначенных прав
- Может управлять пользователями, услугами, бронированиями
- Права назначаются суперадмином

### Accountant (Бухгалтер)
- Специализированный доступ к финансовым функциям
- Управление платежами, выводами средств
- Доступ к финансовым отчетам

## 🔧 Консольная команда

### Создание суперадмина

```bash
python manage.py create_superadmin \
    --email admin@banister.com \
    --password secure_password123 \
    --first-name "John" \
    --last-name "Admin" \
    --phone "(555) 123-4567"
```

**Параметры:**
- `--email` (обязательный): Email адрес суперадмина
- `--password` (обязательный): Пароль
- `--first-name` (обязательный): Имя
- `--last-name` (обязательный): Фамилия
- `--phone` (опциональный): Номер телефона

**Пример использования:**
```bash
# Создание суперадмина
python manage.py create_superadmin \
    --email superadmin@banister.com \
    --password AdminPass123! \
    --first-name "Super" \
    --last-name "Administrator" \
    --phone "(555) 999-8888"
```

## 🌐 API Эндпоинты

### 1. Обновление профиля администратора

**PUT/PATCH** `/api/auth/admin/profile/update/`

Обновление имени и фамилии администратора.

**Заголовки:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
    "first_name": "Новое имя",
    "last_name": "Новая фамилия"
}
```

**Ответ (200):**
```json
{
    "success": true,
    "message": "Admin profile updated successfully",
    "data": {
        "first_name": "Новое имя",
        "last_name": "Новая фамилия"
    }
}
```

### 2. Управление правами доступа

**POST** `/api/auth/admin/permissions/manage/`

Назначение или отзыв прав доступа (только для суперадмина).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
    "admin_user_id": 123,
    "permissions": ["user_management", "service_management"],
    "action": "grant"
}
```

**Параметры:**
- `admin_user_id`: ID администратора
- `permissions`: Список прав доступа
- `action`: "grant" (назначить) или "revoke" (отозвать)

**Доступные права:**
- `user_management` - Управление пользователями
- `service_management` - Управление услугами
- `booking_management` - Управление бронированиями
- `payment_management` - Управление платежами
- `withdrawal_management` - Управление выводами средств
- `document_management` - Управление документами
- `financial_reports` - Финансовые отчеты
- `system_settings` - Системные настройки
- `admin_management` - Управление администраторами

**Ответ (200):**
```json
{
    "success": true,
    "message": "Permissions granted successfully for admin@example.com",
    "data": {
        "admin_user_id": 123,
        "admin_user_email": "admin@example.com",
        "action": "grant",
        "updated_permissions": ["user_management", "service_management"]
    }
}
```

### 3. Список администраторов

**GET** `/api/auth/admin/list/`

Получение списка всех администраторов с их правами (только для суперадмина).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ (200):**
```json
{
    "success": true,
    "message": "Admin users retrieved successfully",
    "data": [
        {
            "id": 1,
            "email": "superadmin@banister.com",
            "role": "super_admin",
            "role_display": "Super Admin",
            "phone": "(555) 999-8888",
            "is_active": true,
            "profile": {
                "first_name": "Super",
                "last_name": "Administrator"
            },
            "permissions": []
        },
        {
            "id": 2,
            "email": "admin@banister.com",
            "role": "admin",
            "role_display": "Admin",
            "phone": "(555) 123-4567",
            "is_active": true,
            "profile": {
                "first_name": "John",
                "last_name": "Admin"
            },
            "permissions": [
                {
                    "id": 1,
                    "permission": "user_management",
                    "permission_display": "User Management",
                    "is_active": true,
                    "granted_by_email": "superadmin@banister.com"
                }
            ]
        }
    ]
}
```

## 🔐 Система прав доступа

### Модель AdminPermission

```python
class AdminPermission(models.Model):
    PERMISSION_CHOICES = (
        ('user_management', 'User Management'),
        ('service_management', 'Service Management'),
        ('booking_management', 'Booking Management'),
        ('payment_management', 'Payment Management'),
        ('withdrawal_management', 'Withdrawal Management'),
        ('document_management', 'Document Management'),
        ('financial_reports', 'Financial Reports'),
        ('system_settings', 'System Settings'),
        ('admin_management', 'Admin Management'),
    )
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=50, choices=PERMISSION_CHOICES)
    is_active = models.BooleanField(default=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

### Проверка прав доступа

```python
# Проверка роли администратора
if request.user.is_admin_role():
    # Пользователь является администратором

# Проверка суперадмина
if request.user.is_super_admin():
    # Пользователь является суперадмином

# Проверка конкретного права
if AdminPermission.objects.filter(
    admin_user=user,
    permission='user_management',
    is_active=True
).exists():
    # У пользователя есть право на управление пользователями
```

## 🚀 Примеры использования

### 1. Создание суперадмина

```bash
# Создание первого суперадмина
python manage.py create_superadmin \
    --email admin@banister.com \
    --password SecurePass123! \
    --first-name "Main" \
    --last-name "Administrator" \
    --phone "(555) 111-2222"
```

### 2. Назначение прав администратору

```bash
# Создание администратора через API
curl -X POST "http://localhost:8000/api/auth/register/management/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "first_name": "John",
    "last_name": "Admin",
    "phone": "(555) 123-4567"
  }'
```

```bash
# Назначение прав (требует токен суперадмина)
curl -X POST "http://localhost:8000/api/auth/admin/permissions/manage/" \
  -H "Authorization: Bearer <superadmin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_user_id": 2,
    "permissions": ["user_management", "service_management"],
    "action": "grant"
  }'
```

### 3. Обновление профиля администратора

```bash
curl -X PUT "http://localhost:8000/api/auth/admin/profile/update/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated Name",
    "last_name": "Updated Surname"
  }'
```

## ⚠️ Безопасность

### Ограничения доступа

1. **Обновление профиля:** Только администраторы могут обновлять свои профили
2. **Управление правами:** Только суперадмины могут назначать/отзывать права
3. **Просмотр списка:** Только суперадмины могут видеть список всех администраторов

### Валидация данных

- Проверка корректности email адресов
- Валидация US форматов телефонных номеров
- Проверка существования пользователей
- Валидация прав доступа

## 🔧 Разработка

### Добавление новых прав

1. Добавить новое право в `AdminPermission.PERMISSION_CHOICES`
2. Создать миграцию: `python manage.py makemigrations`
3. Применить миграцию: `python manage.py migrate`

### Расширение функциональности

```python
# Пример добавления нового права
PERMISSION_CHOICES = (
    # ... существующие права ...
    ('new_permission', 'New Permission'),
)
```

## 📝 Логирование

Все операции с администраторами логируются:
- Создание суперадминов
- Назначение/отзыв прав
- Обновление профилей
- Попытки несанкционированного доступа

---

**Версия:** 1.0.0  
**Последнее обновление:** Август 2025 