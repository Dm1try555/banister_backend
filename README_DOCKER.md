# Docker Setup для Banister Backend

## Настройка переменных окружения

1. Скопируйте файл `env.example` в `.env`:
```bash
cp env.example .env
```

2. Отредактируйте файл `.env` и замените значения на ваши реальные данные:

### Обязательные переменные для настройки:

**База данных:**
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `DB_HOST` - хост базы данных (обычно `db`)

**Django:**
- `DJANGO_DEBUG` - режим отладки (True/False)

**Firebase (для аутентификации и уведомлений):**
- `FIREBASE_API_KEY` - API ключ Firebase
- `FIREBASE_AUTH_DOMAIN` - домен аутентификации Firebase
- `FIREBASE_PROJECT_ID` - ID проекта Firebase
- `FIREBASE_STORAGE_BUCKET` - bucket для хранения файлов
- `FIREBASE_MESSAGING_SENDER_ID` - ID отправителя сообщений
- `FIREBASE_APP_ID` - ID приложения Firebase

**MinIO (для хранения файлов):**
- `MINIO_ACCESS_KEY` - ключ доступа MinIO
- `MINIO_SECRET_KEY` - секретный ключ MinIO
- `MINIO_ENDPOINT` - endpoint MinIO
- `MINIO_ROOT_USER` - пользователь root MinIO
- `MINIO_ROOT_PASSWORD` - пароль root MinIO

**PgAdmin:**
- `PGADMIN_DEFAULT_EMAIL` - email для входа в PgAdmin
- `PGADMIN_DEFAULT_PASSWORD` - пароль для PgAdmin

## Запуск проекта

После настройки `.env` файла запустите проект:

```bash
docker-compose up -d
```

## Доступные сервисы

- **Backend API**: http://localhost:8000
- **PgAdmin**: http://localhost:5050
- **MinIO Console**: http://localhost:9001
- **Traefik Dashboard**: http://localhost:8080

## Остановка проекта

```bash
docker-compose down
```

## Очистка данных

Для полной очистки всех данных (включая volumes):

```bash
docker-compose down -v
``` 