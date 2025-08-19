# Banister Backend API

Django REST Framework бэкенд для платформы бронирования услуг.

## 🚀 Быстрый запуск

### 1. Подготовка окружения

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать окружение (Windows)
venv\Scripts\activate

# Установить зависимости
pip install setuptools
pip install -r requirements.txt
```

### 2. Настройка базы данных

Создайте файл `.env` в корне проекта:

```env
# Django Settings
DJANGO_SECRET_KEY=your_secret_key_here_replace_in_production
DJANGO_DEBUG=True

# PostgreSQL Database
POSTGRES_DB=banister_db
POSTGRES_USER=banister_user
POSTGRES_PASSWORD=banister_password
DB_HOST=localhost

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com

# External Services (optional)
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 3. Установка PostgreSQL

**Для Windows:**
1. Скачайте PostgreSQL с https://www.postgresql.org/download/
2. Установите с настройками по умолчанию
3. Создайте базу данных и пользователя:

```sql
-- Войти в psql как postgres
psql -U postgres

-- Создать пользователя
CREATE USER banister_user WITH PASSWORD 'banister_password';

-- Создать базу данных
CREATE DATABASE banister_db OWNER banister_user;

-- Дать права
GRANT ALL PRIVILEGES ON DATABASE banister_db TO banister_user;
```

### 4. Запуск проекта

```bash
# Применить миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя (опционально)
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

## 📚 API Documentation

После запуска сервера доступна документация:
- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/
- Django Admin: http://127.0.0.1:8000/admin/

## 🔗 API Endpoints

### Основные endpoints:
- `/api/v1/users/` - Управление пользователями
- `/api/v1/bookings/` - Бронирования
- `/api/v1/services/` - Услуги
- `/api/v1/schedules/` - Расписания
- `/api/v1/payments/` - Платежи
- `/api/v1/withdrawals/` - Выводы средств
- `/api/v1/documents/` - Документы
- `/api/v1/notifications/` - Уведомления
- `/api/v1/chats/` - Чаты
- `/api/v1/messages/` - Сообщения
- `/api/v1/customer-dashboard/` - Dashboard клиента
- `/api/v1/provider-dashboard/` - Dashboard провайдера
- `/api/v1/management-dashboard/` - Dashboard менеджмента

## 🛠️ Структура проекта

```
banister_backend/
├── apps/                    # Django приложения
│   ├── authentication/     # Аутентификация и пользователи
│   ├── bookings/           # Бронирования
│   ├── services/           # Услуги и расписания
│   ├── payments/           # Платежи
│   ├── withdrawals/        # Выводы
│   ├── documents/          # Документы
│   ├── dashboard/          # Dashboard
│   ├── notifications/      # Уведомления
│   └── message/            # Чаты и сообщения
├── core/                   # Базовые сервисы
│   ├── mail/               # Email сервис
│   ├── firebase/           # Firebase сервис
│   ├── google_calendar/    # Google Calendar API
│   └── stripe/             # Stripe API
├── banister_backend/       # Настройки Django
└── requirements.txt        # Зависимости
```

## 🔧 Дополнительные настройки

### WebSocket (для чатов)
WebSocket подключения доступны по адресу:
```
ws://127.0.0.1:8000/ws/chat/<chat_id>/
```

### Внешние сервисы (опционально)

**Firebase (для push-уведомлений):**
1. Создайте проект в Firebase Console
2. Скачайте `firebase-service-account.json` в корень проекта

**Google Calendar API:**
1. Создайте проект в Google Cloud Console
2. Включите Calendar API
3. Скачайте `google-credentials.json` в корень проекта

**Stripe (для платежей):**
1. Создайте аккаунт на stripe.com
2. Получите API ключи в Dashboard
3. Добавьте их в .env файл

## 🚦 Статусы

- ✅ **Готово к запуску** - базовая функциональность работает
- ✅ **Django REST Framework** - стандартные ViewSets и Serializers
- ✅ **SQLite/PostgreSQL** - поддержка обеих БД
- ✅ **JWT Authentication** - аутентификация по токенам
- ✅ **WebSocket чаты** - реальное время
- ✅ **Swagger документация** - автогенерация API docs
- ✅ **Роли пользователей** - customer, provider, management, admin
- ⚠️ **Внешние сервисы** - опциональны, работают без настройки

## 📝 Лицензия

MIT License