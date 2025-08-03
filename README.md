# 🏠 Banister Backend API

Django REST API для платформы Banister - сервиса для поиска и бронирования услуг в Америке.

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Запуск сервера
```bash
python manage.py runserver 0.0.0.0:8000
```

### 4. Доступ к документации API
Откройте браузер и перейдите: `http://localhost:8000/swagger/`

### 5. Тестовые аккаунты

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

### 6. Аутентификация
1. Используйте эндпоинты входа для получения JWT токена
2. Вставьте токен в поле Authorization в Swagger UI
3. Система автоматически добавляет префикс "Bearer " к вашему токену

---

## ✅ Готовые функции

### 🔐 Аутентификация и пользователи
- [x] Регистрация пользователей (клиент, поставщик, администрация)
- [x] JWT аутентификация (вход/выход)
- [x] Управление профилями (CRUD)
- [x] Сброс пароля (6-значный код)
- [x] Подтверждение email
- [x] Загрузка/управление фото профиля
- [x] Firebase Authentication интеграция

### 🛠️ Услуги и бронирования
- [x] CRUD услуг (только для поставщиков)
- [x] CRUD бронирований (клиенты создают, поставщики управляют)
- [x] Управление статусом бронирования
- [x] Поиск и фильтрация
- [x] Система расписаний

### 💳 Платежи и финансы
- [x] Система платежей
- [x] Выводы средств
- [x] Управление балансом
- [x] История транзакций

### 📁 Хранилище файлов
- [x] Загрузка фото профиля
- [x] Обработка и валидация изображений
- [x] Интеграция с MinIO
- [x] Управление документами

### 📱 API функции
- [x] Swagger UI документация
- [x] Система обработки ошибок
- [x] Автоматический префикс JWT токена
- [x] Транзакционные операции
- [x] Валидация данных (US форматы)

### ⏰ Автоматизация
- [x] Крон задачи для бэкапов
- [x] Автоматический бэкап базы данных в Google Drive
- [x] Автоматический бэкап MinIO в Google Drive
- [x] Очистка старых уведомлений

### 🎛️ Административная панель
- [x] Управление пользователями
- [x] Управление услугами
- [x] Мониторинг транзакций
- [x] Дашборд статистики
- [x] Система ролей администраторов (Admin, Super Admin, Accountant)
- [x] Управление правами доступа
- [x] Консольная команда создания суперадмина

---

## 🔧 Технический стек

- **Django 5.2** + **Django REST Framework**
- **JWT Authentication** (Simple JWT)
- **PostgreSQL** база данных
- **MinIO** хранилище файлов
- **Google Cloud Storage** для бэкапов
- **Firebase Authentication**
- **Swagger/OpenAPI** документация
- **Кастомная система обработки ошибок**
- **Django Crontab** для автоматизации

---

## 📚 Документация

**Полная документация находится в папке [`docs/`](./docs/)**

### 🔗 Быстрые ссылки:
- [🌐 API Documentation](./docs/API_DOCUMENTATION.md)
- [🔐 Authentication API](./docs/AUTHENTICATION_API.md)
- [🛠️ Services API](./docs/SERVICES_API.md)
- [📋 Endpoints Overview](./docs/ENDPOINTS_OVERVIEW.md)
- [💾 MinIO Implementation](./docs/MINIO_IMPLEMENTATION.md)
- [⏰ Cron Tasks Setup](./docs/CRON_SETUP.md)
- [🎛️ Admin Management](./docs/ADMIN_MANAGEMENT.md)
- [📝 Changelog](./docs/CHANGELOG.md)

### 🏗️ Структура документации
```
docs/
├── API_DOCUMENTATION.md         # 🌐 API документация
├── AUTHENTICATION_API.md        # 🔐 Аутентификация
├── SERVICES_API.md              # 🛠️ Сервисы
├── ENDPOINTS_OVERVIEW.md        # 📋 Обзор эндпоинтов
├── MINIO_IMPLEMENTATION.md      # 💾 Хранилище файлов
├── CRON_SETUP.md               # ⏰ Крон задачи
├── ADMIN_MANAGEMENT.md          # 🎛️ Управление администраторами
└── CHANGELOG.md                # 📝 История изменений
```

---

## 🏗️ Структура проекта

```
banister_backend/
├── authentication/     # 🔐 Аутентификация и пользователи
├── services/          # 🛠️ Услуги
├── bookings/          # 📅 Бронирования
├── payments/          # 💳 Платежи
├── withdrawals/       # 💰 Выводы средств
├── message/           # 💬 Сообщения и уведомления
├── file_storage/      # 📁 Хранилище файлов
├── cron_tasks/        # ⏰ Автоматические задачи
├── admin_panel/       # 🎛️ Административная панель
├── dashboard/         # 📊 Дашборд
├── documents/         # 📄 Документы
├── providers/         # 👥 Поставщики услуг
├── schedules/         # 📅 Расписания
├── public_core/       # 🌐 Публичное API
├── error_handling/    # ⚠️ Обработка ошибок
├── docs/              # 📚 Документация
└── banister_backend/  # ⚙️ Основные настройки Django
```

---

## 🔒 Безопасность

- JWT токен аутентификация
- Хеширование паролей
- Валидация входных данных
- Безопасность загрузки файлов
- CORS конфигурация
- Ограничение скорости запросов
- Транзакционные операции для целостности данных

---

## 🚀 Развертывание

### Docker
```bash
docker-compose up -d
```

### Переменные окружения
Создайте файл `.env` в корне проекта:
```env
# База данных
POSTGRES_DB=banister_db
POSTGRES_USER=banister_user
POSTGRES_PASSWORD=banister_pass
DB_HOST=localhost

# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

# Firebase
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id

# Google Cloud Storage
GOOGLE_CLOUD_BUCKET_NAME=banister-backups

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_SECURE=False
```

---

## 📞 Поддержка

- **Swagger UI:** `http://localhost:8000/swagger/`
- **Полная документация:** [docs/](./docs/)
- **Логи:** `debug.log`

---

## 🔄 Обновления

Регулярно проверяйте [CHANGELOG.md](./docs/CHANGELOG.md) для получения информации о новых функциях и обновлениях.

---

**Версия:** 1.0.0  
**Последнее обновление:** Август 2025  
**Статус:** ✅ Готово к продакшену 