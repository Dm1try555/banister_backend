# 📚 Документация Banister Backend

Добро пожаловать в документацию проекта Banister Backend! Здесь вы найдете всю необходимую информацию для работы с API и сервисами.

## 📋 Содержание

### 🔐 Аутентификация и авторизация
- [**AUTHENTICATION_API.md**](./AUTHENTICATION_API.md) - Полная документация по аутентификации
  - Firebase Authentication
  - JWT токены
  - Регистрация и вход пользователей
  - Управление профилями

### 🌐 API и эндпоинты
- [**API_DOCUMENTATION.md**](./API_DOCUMENTATION.md) - Основная документация API
  - Все эндпоинты
  - Примеры запросов и ответов
  - Коды ошибок
- [**ENDPOINTS_OVERVIEW.md**](./ENDPOINTS_OVERVIEW.md) - Обзор всех эндпоинтов
  - Краткое описание каждого эндпоинта
  - Методы HTTP
  - Параметры запросов

### 🛠️ Сервисы и функциональность
- [**SERVICES_API.md**](./SERVICES_API.md) - Документация по сервисам
  - Управление услугами
  - Бронирования
  - Платежи
  - Выводы средств

### 💾 Хранилище файлов
- [**MINIO_IMPLEMENTATION.md**](./MINIO_IMPLEMENTATION.md) - Реализация MinIO
  - Настройка MinIO
  - Загрузка файлов
  - Управление bucket'ами
  - Бэкап файлов

### ⏰ Автоматизация
- [**CRON_SETUP.md**](./CRON_SETUP.md) - Настройка крон задач
  - Бэкап базы данных
  - Бэкап MinIO
  - Очистка уведомлений
  - Расписание выполнения

### 📝 История изменений
- [**CHANGELOG.md**](./CHANGELOG.md) - Журнал изменений
  - Версии проекта
  - Новые функции
  - Исправления ошибок

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
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

### 3. Запуск проекта
```bash
# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver
```

### 4. Настройка крон задач
```bash
# Установка крон задач
python manage.py crontab add

# Проверка установленных задач
python manage.py crontab show
```

## 🔧 Разработка

### Структура проекта
```
banister_backend/
├── authentication/     # Аутентификация и пользователи
├── bookings/          # Бронирования
├── services/          # Услуги
├── payments/          # Платежи
├── withdrawals/       # Выводы средств
├── message/           # Сообщения и уведомления
├── file_storage/      # Хранилище файлов
├── cron_tasks/        # Автоматические задачи
├── docs/              # Документация
└── banister_backend/  # Основные настройки Django
```

### Полезные команды
```bash
# Проверка проекта
python manage.py check

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic

# Тестирование
python manage.py test
```

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте документацию в соответствующих разделах
2. Посмотрите журнал изменений в [CHANGELOG.md](./CHANGELOG.md)
3. Проверьте логи в файле `debug.log`

## 🔄 Обновления

Регулярно проверяйте [CHANGELOG.md](./CHANGELOG.md) для получения информации о новых функциях и обновлениях.

---

**Последнее обновление:** Август 2025
**Версия проекта:** 1.0.0 