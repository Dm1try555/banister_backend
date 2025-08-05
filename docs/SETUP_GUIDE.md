# Настройка сервисов - Banister Backend

## 🚀 Быстрый старт

### 1. Клонирование и установка
```bash
git clone <repository>
cd banister_backend
pip install -r requirements.txt
```

### 2. Переменные окружения
Создайте файл `.env` в корне проекта:
```env
# База данных
POSTGRES_DB=banister_db
POSTGRES_USER=banister_user
POSTGRES_PASSWORD=your-secure-password
DB_HOST=db

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
FRONTEND_URL=http://localhost:3000

# SMTP (Email)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@banister.com

# Stripe (Платежи)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Firebase (Уведомления)
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id

# MinIO (Файловое хранилище)
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_ENDPOINT=minio:9000

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@banister.com
PGADMIN_DEFAULT_PASSWORD=your-secure-password

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
```

### 3. Запуск с Docker
```bash
docker-compose up -d
```

### 4. Миграции и создание пользователей
```bash
python manage.py migrate
python manage.py create-superadmin
python manage.py create-admin
python manage.py create-accountant
```

### 5. Запуск сервера
```bash
python manage.py runserver
```

## 🔧 Настройка сервисов

### Stripe (Платежи)

1. **Создайте аккаунт в Stripe:**
   - Перейдите на [Stripe Dashboard](https://dashboard.stripe.com/)
   - Создайте аккаунт и получите API ключи

2. **Настройте переменные окружения:**
   ```env
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

3. **Тестирование:**
   - Используйте тестовые карты Stripe
   - Проверьте эндпоинты в Swagger UI

### Google Calendar

1. **Создайте сервисный аккаунт:**
   - Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
   - Создайте новый проект или используйте существующий
   - Перейдите в "IAM & Admin" > "Service Accounts"
   - Создайте новый сервисный аккаунт
   - Скачайте JSON файл с ключами

2. **Разместите файл с ключами:**
   - Поместите скачанный JSON файл в корень проекта
   - Переименуйте его в `google-credentials.json`
   - Убедитесь, что файл добавлен в `.gitignore`

3. **Включите Google Calendar API:**
   - В том же проекте перейдите в "APIs & Services" > "Library"
   - Найдите "Google Calendar API" и включите его

4. **Настройте права доступа:**
   - Убедитесь, что у сервисного аккаунта есть права на Google Calendar API
   - Проверьте, что аккаунт может создавать события

### Firebase (Уведомления)

1. **Создайте проект в Firebase:**
   - Перейдите в [Firebase Console](https://console.firebase.google.com/)
   - Создайте новый проект
   - Добавьте веб-приложение

2. **Настройте Cloud Messaging:**
   - Перейдите в "Project Settings" > "Cloud Messaging"
   - Скопируйте Server Key

3. **Скачайте credentials:**
   - Перейдите в "Project Settings" > "Service Accounts"
   - Скачайте JSON файл с ключами
   - Поместите файл в корень проекта как `firebase-service-account.json`

4. **Настройте переменные окружения:**
   ```env
   FIREBASE_API_KEY=your-firebase-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   FIREBASE_APP_ID=your-app-id
   ```

### MinIO (Файловое хранилище)

1. **Docker Compose уже настроен:**
   ```yaml
   minio:
     image: minio/minio:latest
     ports:
       - "9000:9000"
       - "9001:9001"
     environment:
       - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
       - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
   ```

2. **Создайте бакеты:**
   ```bash
   python manage.py create_minio_buckets
   ```

3. **Доступ к консоли:**
   - Откройте http://localhost:9001
   - Войдите с MINIO_ACCESS_KEY и MINIO_SECRET_KEY

### SMTP (Email)

1. **Настройте Gmail:**
   - Включите двухфакторную аутентификацию
   - Создайте пароль приложения
   - Используйте его в EMAIL_HOST_PASSWORD

2. **Альтернативные провайдеры:**
   - **SendGrid:** EMAIL_HOST=smtp.sendgrid.net
   - **Mailgun:** EMAIL_HOST=smtp.mailgun.org
   - **Amazon SES:** EMAIL_HOST=email-smtp.us-east-1.amazonaws.com

## 📊 Мониторинг

### Логи
```bash
# Просмотр логов Django
tail -f debug.log

# Просмотр логов Docker
docker-compose logs -f
```

### Cron задачи
```bash
# Проверка статуса cron задач
python manage.py crontab show

# Добавление cron задач
python manage.py crontab add

# Удаление cron задач
python manage.py crontab remove
```

### Резервное копирование
```bash
# Ручной бэкап БД
python manage.py backup_database

# Ручной бэкап MinIO
python manage.py backup_minio

# Очистка уведомлений
python manage.py cleanup_notifications
```

## 🔒 Безопасность

### JWT токены
- Токены автоматически обновляются
- Время жизни: 5 минут (access), 1 день (refresh)
- Хранятся в Redis

### Роли пользователей
- **customer** - клиенты (базовые права)
- **provider** - провайдеры услуг
- **management** - менеджеры поддержки
- **admin** - администраторы
- **super_admin** - суперадминистраторы
- **accountant** - бухгалтеры

### Валидация данных
- Все входные данные валидируются
- Проверка типов файлов и размеров
- Защита от SQL инъекций

## 🚀 Продакшн

### Переменные окружения
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DJANGO_SECRET_KEY=your-production-secret-key
```

### SSL сертификаты
```bash
# Установка SSL сертификатов
sudo certbot --nginx -d your-domain.com
```

### Gunicorn
```bash
# Установка Gunicorn
pip install gunicorn

# Запуск
gunicorn banister_backend.wsgi:application --bind 0.0.0.0:8000
```

### Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/static/;
    }
}
```

## 📞 Поддержка

- **Email:** developer@banister.com
- **Документация:** http://localhost:8000/swagger/
- **GitHub Issues:** Создайте issue в репозитории

---

**Banister Backend** - Полная настройка всех сервисов 