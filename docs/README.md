# Banister Backend API

## 🚀 Обзор проекта

**Banister Backend** - это полнофункциональная Django REST API система для управления сервисами, платежами, бронированиями и пользователями. Система поддерживает различные роли пользователей и интегрируется с внешними сервисами.

## 📋 Что реализовано

### ✅ Аутентификация и пользователи
- **JWT аутентификация** с поддержкой различных ролей
- **Роли пользователей:** customer, provider, management, admin, super_admin, accountant
- **Email подтверждение** с SMTP интеграцией
- **Профили пользователей** с фото
- **Управление админами** через консольные команды

### ✅ Платежи и финансы
- **Stripe интеграция** для обработки платежей
- **Создание Payment Intent** и подтверждение платежей
- **Возврат средств** через Stripe
- **История платежей** с детализацией
- **Управление клиентами** и методами оплаты

### ✅ Бронирования и сервисы
- **Система бронирований** с различными статусами
- **Управление сервисами** для провайдеров
- **Расписание провайдеров** с проверкой конфликтов
- **Поиск провайдеров** по различным критериям

### ✅ Google Calendar интеграция
- **Создание событий** в Google Calendar
- **Google Meet конференции** с автоматическими приглашениями
- **Email уведомления** с ссылками на встречи
- **Тестовый эндпоинт** для отправки приглашений

### ✅ Уведомления и чат
- **Firebase Cloud Messaging** для push уведомлений
- **WebSocket чат** с реальным временем
- **Приватные каналы** и авторизация
- **Управление сообщениями** (отправка, получение, удаление)

### ✅ Файловое хранилище
- **MinIO интеграция** для хранения файлов
- **Автоматическое создание бакетов**
- **Загрузка профильных фото** для всех типов пользователей
- **Безопасное хранение** документов

### ✅ Административная панель
- **Управление пользователями** (просмотр, удаление)
- **Фильтрация по ролям** (клиенты, провайдеры)
- **Статистика и дашборд** для всех ролей
- **Система разрешений** для админов

### ✅ Автоматизация и резервное копирование
- **Cron задачи** для автоматических операций
- **Резервное копирование** базы данных в Google Drive
- **Резервное копирование** MinIO файлов
- **Очистка уведомлений** старше 2 месяцев

### ✅ Документация и API
- **Swagger документация** с полным описанием
- **JWT аутентификация** в Swagger UI
- **Примеры использования** для всех эндпоинтов
- **Структурированная документация** по всем сервисам

## 🛠 Технологии

### Backend
- **Django 4.2** - основной фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - база данных
- **Redis** - кэширование и сессии
- **Celery** - фоновые задачи

### Интеграции
- **Stripe** - платежи
- **Google Calendar API** - календарь и встречи
- **Firebase Cloud Messaging** - push уведомления
- **MinIO** - файловое хранилище
- **SMTP** - email уведомления

### Документация
- **Swagger/OpenAPI** - API документация
- **DRF-YASG** - генерация документации

## 📁 Структура проекта

```
banister_backend/
├── authentication/          # Аутентификация и пользователи
├── bookings/               # Бронирования и встречи
├── payments/               # Платежи и Stripe
├── services/               # Управление сервисами
├── schedules/              # Расписание провайдеров
├── notifications/          # Уведомления и Firebase
├── message/                # WebSocket чат
├── file_storage/           # MinIO файловое хранилище
├── admin_panel/            # Административная панель
├── dashboard/              # Статистика и дашборд
├── public_core/            # Публичные API
├── documents/              # Управление документами
├── withdrawals/            # Выводы средств
├── workers/                # Фоновые задачи
├── cron_tasks/             # Автоматические задачи
├── error_handling/         # Обработка ошибок
└── docs/                   # Документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных
```bash
python manage.py migrate
```

### 3. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 4. Создание админов
```bash
python manage.py create-superadmin
python manage.py create-admin
python manage.py create-accountant
```

### 5. Запуск сервера
```bash
python manage.py runserver
```

### 6. Доступ к документации
- **Swagger UI:** http://localhost:8000/swagger/
- **API Base URL:** http://localhost:8000/api/v1/

## 🔧 Настройка сервисов

### Stripe (Платежи)
1. Получите API ключи в [Stripe Dashboard](https://dashboard.stripe.com/)
2. Добавьте в `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

### Google Calendar
1. Создайте сервисный аккаунт в [Google Cloud Console](https://console.cloud.google.com/)
2. Скачайте JSON файл с ключами и поместите в корень проекта как `google-credentials.json`
3. Включите Google Calendar API в проекте
4. Проверьте права доступа для сервисного аккаунта

### Firebase (Уведомления)
1. Создайте проект в [Firebase Console](https://console.firebase.google.com/)
2. Добавьте в `.env`:
   ```
   FIREBASE_API_KEY=your-firebase-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   FIREBASE_APP_ID=your-app-id
   ```

### MinIO (Файловое хранилище)
1. Настройте MinIO в `docker-compose.yml`
2. Добавьте в `.env`:
   ```
   MINIO_ACCESS_KEY=your-access-key
   MINIO_SECRET_KEY=your-secret-key
   MINIO_ENDPOINT=minio:9000
   ```

### SMTP (Email)
1. Настройте SMTP сервер
2. Добавьте в `.env`:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

## 📚 Документация

### Основные документы
- **[CLIENT_REQUIREMENTS_RESPONSE.md](CLIENT_REQUIREMENTS_RESPONSE.md)** - Ответы на требования заказчика
- **[STRIPE_SETUP.md](STRIPE_SETUP.md)** - Настройка платежей
- **[AUTHENTICATION_API.md](AUTHENTICATION_API.md)** - API аутентификации
- **[ADMIN_MANAGEMENT.md](ADMIN_MANAGEMENT.md)** - Управление админами
- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Настройка уведомлений
- **[CHAT_API.md](CHAT_API.md)** - WebSocket чат
- **[MINIO_IMPLEMENTATION.md](MINIO_IMPLEMENTATION.md)** - Файловое хранилище
- **[GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)** - Google Calendar
- **[worker_documentation.md](worker_documentation.md)** - Фоновые задачи

### API Endpoints

#### Аутентификация
- `POST /api/v1/auth/login/customer/` - Вход для клиентов
- `POST /api/v1/auth/login/provider/` - Вход для провайдеров
- `POST /api/v1/auth/register/` - Регистрация
- `POST /api/v1/auth/email-confirm/request/` - Запрос подтверждения email
- `POST /api/v1/auth/email-confirm/verify/` - Подтверждение email

#### Платежи
- `GET /api/v1/payments/` - История платежей
- `POST /api/v1/payments/stripe/create-intent/` - Создание Payment Intent
- `POST /api/v1/payments/stripe/confirm-payment/` - Подтверждение платежа
- `POST /api/v1/payments/stripe/refund/` - Возврат средств

#### Бронирования
- `GET /api/v1/bookings/` - Список бронирований
- `POST /api/v1/bookings/create/` - Создание бронирования
- `POST /api/v1/bookings/google-meet-invitation/` - Google Meet приглашения

#### Сервисы
- `GET /api/v1/services/` - Список сервисов
- `POST /api/v1/services/create/` - Создание сервиса
- `PUT /api/v1/services/{id}/update/` - Обновление сервиса

#### Уведомления
- `GET /api/v1/notifications/` - Список уведомлений
- `POST /api/v1/notifications/mark-read/{id}/` - Отметить как прочитанное
- `DELETE /api/v1/notifications/{id}/` - Удалить уведомление

#### Чат
- `GET /api/v1/message/chats/` - Список чатов
- `GET /api/v1/message/chats/{chat_id}/messages/` - Сообщения чата
- `POST /api/v1/message/messages/` - Отправить сообщение

## 🔒 Безопасность

### Аутентификация
- JWT токены с автоматическим обновлением
- Ролевая система доступа
- Email подтверждение для критических операций

### Транзакции
- Все операции создания/обновления обернуты в транзакции
- Автоматический откат при ошибках
- Проверка прав доступа на уровне объектов

### Валидация
- Строгая валидация входных данных
- Проверка типов файлов и размеров
- Защита от SQL инъекций

## 📊 Мониторинг

### Логирование
- Структурированные логи для всех операций
- Отслеживание ошибок и исключений
- Мониторинг производительности

### Резервное копирование
- Ежедневное резервное копирование БД
- Ежедневное резервное копирование файлов
- Автоматическая очистка старых данных

## 🚀 Развертывание

### Docker
```bash
docker-compose up -d
```

### Продакшн
1. Настройте переменные окружения
2. Запустите миграции
3. Создайте суперпользователя
4. Настройте SSL сертификаты
5. Запустите с Gunicorn

## 📞 Поддержка

- **Email:** developer@banister.com
- **Документация:** http://localhost:8000/swagger/
- **Лицензия:** MIT License

---

**Banister Backend** - Полнофункциональная система управления сервисами и платежами 