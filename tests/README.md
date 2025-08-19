# 🧪 Тестирование Banister Backend API

## 📂 Структура тестов

### **Основные тесты функционала:**

- `test_api.py` - Базовое тестирование API (регистрация, логин, профиль, email верификация)
- `test_admin.py` - Тестирование админских функций (логин админа, обновление профиля, разрешения)
- `test_permissions.py` - Тестирование системы разрешений (создание админа, управление правами)
- `test_drf_classes.py` - Тестирование DRF классов и архитектуры
- `test_pagination_minio.py` - Тестирование пагинации и загрузки файлов в MinIO
- `test_cron_smtp.py` - Тестирование крон задач и SMTP настроек

### **Тестовые данные:**

- `test_user.json` - JSON данные для тестирования регистрации пользователя

## 🚀 Как запускать тесты

### **Запуск отдельных тестов:**

```bash
# Базовое API тестирование
docker-compose exec web python /app/tests/test_api.py

# Админские функции
docker-compose exec web python /app/tests/test_admin.py

# Система разрешений
docker-compose exec web python /app/tests/test_permissions.py

# DRF классы и архитектура
docker-compose exec web python /app/tests/test_drf_classes.py
```

### **Запуск всех тестов:**

```bash
docker-compose exec web python /app/tests/test_api.py
docker-compose exec web python /app/tests/test_admin.py
docker-compose exec web python /app/tests/test_permissions.py
docker-compose exec web python /app/tests/test_drf_classes.py
docker-compose exec web python /app/tests/test_pagination_minio.py
docker-compose exec web python /app/tests/test_cron_smtp.py
```

## ✅ Что тестируется

### **1. Базовое API (test_api.py):**
- POST `/api/v1/auth/register/` - Регистрация пользователя
- POST `/api/v1/auth/login/` - Логин пользователя
- GET `/api/v1/auth/profile/` - Получение профиля
- POST `/api/v1/auth/send-verification/` - Отправка кода верификации

### **2. Админские функции (test_admin.py):**
- POST `/api/v1/auth/login/` - Логин суперадмина
- PATCH `/api/v1/auth/admin/update-profile/` - Обновление профиля админа
- GET `/api/v1/auth/admin/permissions/` - Получение разрешений
- GET `/api/v1/users/` - Список пользователей (ModelViewSet)

### **3. Система разрешений (test_permissions.py):**
- Создание обычного админа
- POST `/api/v1/auth/admin/manage-permissions/` - Управление разрешениями
- Верификация email с неправильным кодом

### **4. DRF классы (test_drf_classes.py):**
- CreateAPIView - регистрация
- RetrieveAPIView - профиль
- APIView - refresh token
- ModelViewSet - CRUD пользователей
- Swagger UI доступность

### **5. Пагинация и MinIO (test_pagination_minio.py):**
- GET `/api/v1/users/?page=1&page_size=3` - Пагинация списков
- POST `/api/v1/auth/upload-photo/` - Загрузка профильного фото
- Валидация типов файлов
- Автоматическое создание MinIO бакетов

### **6. Крон задачи и SMTP (test_cron_smtp.py):**
- SMTP конфигурация через email верификацию
- Проверка Celery beat расписания
- Тестирование файлов backup сервиса
- Проверка API уведомлений

## 🎯 Ожидаемые результаты

Все тесты должны проходить с зелеными галочками ✅ и корректными HTTP статусами:
- 200 - Успешные GET/PATCH запросы
- 201 - Успешное создание (POST)
- 400 - Корректная валидация ошибок

## 📊 Последние результаты тестирования

**Дата:** 19.08.2025  
**Статус:** ✅ Все тесты проходят успешно  
**Пользователей создано:** 7  
**API вызовов протестировано:** 15+