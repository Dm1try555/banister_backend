# Banister Backend API

Полная документация по API для системы управления услугами Banister.

## 📋 Содержание

1. [Аутентификация и авторизация](#аутентификация-и-авторизация)
2. [Управление пользователями](#управление-пользователями)
3. [Транзакции базы данных](#транзакции-базы-данных)
4. [Подтверждение email](#подтверждение-email)
5. [Управление админами](#управление-админами)
6. [Файловое хранилище (MinIO)](#файловое-хранилище-minio)
7. [Резервное копирование](#резервное-копирование)
8. [Уведомления (Firebase)](#уведомления-firebase)
9. [Чат (WebSocket)](#чат-websocket)
10. [Google Calendar](#google-calendar)
11. [Платежи (Stripe)](#платежи-stripe)
12. [SMTP настройки](#smtp-настройки)

## 🔐 Аутентификация и авторизация

### Роли пользователей
- `customer` - Клиент
- `provider` - Провайдер услуг
- `admin` - Администратор
- `super_admin` - Супер администратор
- `accountant` - Бухгалтер
- `management` - Менеджер поддержки

### Firebase интеграция
- Аутентификация через Firebase
- Отправка push-уведомлений
- Поддержка токенов

## 👥 Управление пользователями

### Консольные команды для создания пользователей

```bash
# Создание суперадмина
python manage.py create_superadmin --email admin@example.com --password password123

# Создание админа
python manage.py create_admin --email admin@example.com --password password123

# Создание бухгалтера
python manage.py create_accountant --email accountant@example.com --password password123

# Создание менеджера
python manage.py create_management --email manager@example.com --password password123
```

### Обновление данных админа
- `PUT /api/auth/profile/` - Обновление имени, фамилии и других данных профиля

## 💾 Транзакции базы данных

**Все эндпоинты, выполняющие создание и обновление данных, обернуты в транзакции:**

```python
from django.db import transaction

@transaction.atomic
def perform_create(self, serializer):
    # Логика создания
    serializer.save()
```

**Примеры эндпоинтов с транзакциями:**
- Создание бронирования
- Создание платежей
- Создание запросов на вывод средств
- Обновление профилей
- Создание услуг

## 📧 Подтверждение email

### Эндпоинты для подтверждения email:

1. **Отправка запроса подтверждения**
   ```
   POST /api/auth/send-email-confirmation/
   ```

2. **Подтверждение email**
   ```
   POST /api/auth/confirm-email/
   ```

## 🔧 Управление админами

### Система разрешений для админов

Модель `AdminPermission` позволяет настраивать права доступа:

```python
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
```

### Эндпоинты управления админами:

- `GET /api/admin/permissions/` - Получить разрешения админа
- `POST /api/admin/permissions/` - Добавить разрешение (только суперадмин)
- `DELETE /api/admin/permissions/{id}/` - Удалить разрешение (только суперадмин)

## 📁 Файловое хранилище (MinIO)

### Docker Compose конфигурация

MinIO уже подключен в `docker-compose.yml`:

```yaml
minio:
  image: minio/minio:latest
  container_name: minio_banister
  command: server /data --console-address ":9001"
  environment:
    - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
    - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
  volumes:
    - minio_data:/data
  ports:
    - "9000:9000"
    - "9001:9001"
```

### Автоматическое создание бакетов

Команда для создания бакетов:
```bash
python manage.py create_minio_buckets
```

### Эндпоинты для профильных фотографий

- `POST /api/file-storage/profile-photo/` - Загрузка профильной фотографии
- `DELETE /api/file-storage/profile-photo/{id}/` - Удаление профильной фотографии
- `GET /api/file-storage/profile-photo/` - Получение профильной фотографии

## 💾 Резервное копирование

### Cron задачи (настроены на 12:00 ночи)

1. **Бэкап базы данных в Google Drive** (ежедневно)
   ```python
   ('0 0 * * *', 'cron_tasks.cron.database_backup_cron_job')
   ```

2. **Бэкап MinIO в Google Drive** (ежедневно)
   ```python
   ('0 0 * * *', 'cron_tasks.cron.minio_backup_cron_job')
   ```

3. **Очистка старых уведомлений** (еженедельно)
   ```python
   ('0 0 * * 0', 'cron_tasks.cron.notification_cleanup_cron_job')
   ```

### Команды для ручного бэкапа:

```bash
# Бэкап базы данных
python manage.py backup_database

# Бэкап MinIO
python manage.py backup_minio

# Очистка уведомлений
python manage.py cleanup_notifications
```

## 🔔 Уведомления (Firebase)

### Модель уведомлений

```python
{
    "id": "uuid",
    "user_id": "user_id",
    "notification_type": "ClientSendBookingNotificationToAdmin",
    "data": {},
    "is_read": false,
    "created_at": "timestamp"
}
```

### Эндпоинты уведомлений

- `GET /api/notifications/` - Получить уведомления с пагинацией
- `POST /api/notifications/mark-read/{id}/` - Отметить как прочитанное
- `DELETE /api/notifications/{id}/` - Удалить уведомление
- `DELETE /api/notifications/clear-all/` - Удалить все уведомления
- `GET /api/notifications/mark-all-read/` - Отметить все как прочитанные

## 💬 Чат (WebSocket)

### WebSocket соединение

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/chat/');
```

### Эндпоинты чата

- `GET /api/message/conversations/` - Получить список чатов
- `GET /api/message/messages/{conversation_id}/` - Получить сообщения с пагинацией
- `POST /api/message/send/` - Отправить сообщение
- `PUT /api/message/messages/{id}/` - Обновить сообщение
- `DELETE /api/message/messages/{id}/` - Удалить сообщение

## 📅 Google Calendar

### Эндпоинты для интервью

- `POST /api/bookings/interview-request/` - Запрос на интервью
- `GET /api/bookings/my-interview-requests/` - Мои запросы на интервью (провайдер)
- `GET /api/bookings/interview-requests/` - Запросы на интервью (админ)
- `PUT /api/bookings/interview-request/{id}/status/` - Изменить статус интервью

### Статусы интервью:
- `pending` - Ожидает рассмотрения
- `scheduled` - Назначено время
- `rejected` - Отклонено
- `completed` - Завершено

## 💳 Платежи (Stripe)

### Эндпоинты платежей

- `POST /api/payments/create-payment-intent/` - Создать платежное намерение
- `POST /api/payments/confirm-payment/` - Подтвердить платеж
- `GET /api/payments/payment-history/` - История платежей
- `POST /api/payments/refund/` - Возврат средств

### Финансовые операции

- Получение финансов на карту системы
- Отправка средств провайдерам
- Автоматические выплаты

## 📧 SMTP настройки

### Конфигурация в settings.py

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@banister.com')
```

### Переменные окружения

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@banister.com
```

## 🚀 Запуск проекта

1. **Клонирование и установка зависимостей:**
   ```bash
   git clone <repository>
   cd banister_backend
   pip install -r requirements.txt
   ```

2. **Настройка переменных окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл
   ```

3. **Запуск с Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Миграции и создание суперадмина:**
   ```bash
   python manage.py migrate
   python manage.py create_superadmin --email admin@example.com --password password123
   ```

## 📚 Дополнительная документация

- [Ответы на требования заказчика](CLIENT_REQUIREMENTS_RESPONSE.md) - **ГЛАВНЫЙ ДОКУМЕНТ**
- [API Аутентификации](AUTHENTICATION_API.md)
- [API Услуг](SERVICES_API.md)
- [API Уведомлений](notifications_api.md)
- [API Чата](CHAT_API.md)
- [WebSocket API](WEBSOCKET_API.md)
- [Настройка Firebase](FIREBASE_SETUP.md)
- [Настройка MinIO](MINIO_IMPLEMENTATION.md)
- [Настройка Google Calendar](GOOGLE_CALENDAR_SETUP.md)
- [Настройка Stripe](STRIPE_SETUP.md)
- [Управление админами](ADMIN_MANAGEMENT.md)
- [Документация воркеров](worker_documentation.md) 