# Banister Backend API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Start Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 4. Access API Documentation
Open your browser and go to: `http://localhost:8000/swagger/`

### 5. Test Accounts

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

### 6. Authentication
1. Use the login endpoints to get your JWT token
2. Insert your token in the Authorization field in Swagger UI
3. The system automatically adds "Bearer " prefix to your token

---

## 📋 Ready Features

### ✅ Authentication & Users
- [x] User registration (customer, provider, management)
- [x] JWT authentication (login/logout)
- [x] Profile management (CRUD)
- [x] Password reset (6-digit code)
- [x] Email confirmation
- [x] Profile photo upload/management

### ✅ Services & Bookings
- [x] Services CRUD (providers only)
- [x] Bookings CRUD (customers create, providers manage)
- [x] Booking status management
- [x] Search and filtering

### ✅ File Storage
- [x] Profile photo upload
- [x] Image processing and validation
- [x] MinIO integration

### ✅ API Features
- [x] Swagger UI documentation
- [x] Error handling system
- [x] JWT token auto-prefix
- [x] Transaction-based operations

---

## 🔧 Technical Stack

- **Django 5.2** + **Django REST Framework**
- **JWT Authentication** (Simple JWT)
- **PostgreSQL** database
- **MinIO** file storage
- **Swagger/OpenAPI** documentation
- **Custom error handling**

---

## 📚 Documentation

**Полная документация находится в папке [`docs/`](./docs/)**

### 🔗 Быстрые ссылки:
- [📖 Главная документация](./docs/README.md)
- [🌐 API Documentation](./docs/API_DOCUMENTATION.md)
- [🔐 Authentication API](./docs/AUTHENTICATION_API.md)
- [🛠️ Services API](./docs/SERVICES_API.md)
- [💾 MinIO Implementation](./docs/MINIO_IMPLEMENTATION.md)
- [⏰ Cron Tasks Setup](./docs/CRON_SETUP.md)
- [📝 Changelog](./docs/CHANGELOG.md)

### 🏗️ Структура документации
```
docs/
├── README.md                    # 📖 Главная документация
├── API_DOCUMENTATION.md         # 🌐 API документация
├── AUTHENTICATION_API.md        # 🔐 Аутентификация
├── SERVICES_API.md              # 🛠️ Сервисы
├── ENDPOINTS_OVERVIEW.md        # 📋 Обзор эндпоинтов
├── MINIO_IMPLEMENTATION.md      # 💾 Хранилище файлов
├── CRON_SETUP.md               # ⏰ Крон задачи
└── CHANGELOG.md                # 📝 История изменений
```

---

## 🔒 Security

- JWT token authentication
- Password hashing
- Input validation
- File upload security
- CORS configuration
- Rate limiting

---

## 📞 Support

- **Swagger UI:** `http://localhost:8000/swagger/`
- **Full Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

*Last updated: August 2, 2024* 