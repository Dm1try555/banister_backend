# 🧪 Тестирование Banister Backend API

## 🚀 Быстрый запуск всех тестов

```cmd
docker-compose exec web python tests/run_all_tests.py
```

## 📂 Структура тестов

### **Основные тесты функционала:**

- `test_api.py` - Базовое тестирование API (регистрация, логин, профиль, email верификация)
- `test_admin.py` - Тестирование админских функций (логин админа, обновление профиля, разрешения)
- `test_permissions.py` - Тестирование системы разрешений (создание админа, управление правами)
- `test_drf_classes.py` - Тестирование DRF классов и архитектуры
- `test_pagination_minio.py` - Тестирование пагинации и загрузки файлов в MinIO
- `test_notifications.py` - **НОВОЕ!** Система уведомлений с Firebase 🔔
- `test_smtp_only.py` - SMTP отправка email
- `test_cron_only.py` - Cron задачи и расписание
- `test_backups.py` - Локальные бекапы с автоматической ротацией
- `check_backup_files.py` - Проверка локальных файлов бекапов
- `run_all_tests.py` - Запуск всех тестов сразу

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
docker-compose exec web python tests/run_all_tests.py
```

**⚡ Это запустит все 10 тестов автоматически!**

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

### **6. 🔔 Система уведомлений (test_notifications.py):**
- POST `/api/v1/notifications/` - Создание + Firebase push
- GET `/api/v1/notifications/` - Список с пагинацией
- POST `/api/v1/notifications/{id}/mark_read/` - Отметить прочитанным
- DELETE `/api/v1/notifications/{id}/` - Удалить уведомление
- POST `/api/v1/notifications/mark_all_read/` - Отметить все
- DELETE `/api/v1/notifications/delete_all/` - Удалить все
- GET `/api/v1/notifications/unread/` - Непрочитанные

### **7. 📧 SMTP отправка (test_smtp_only.py):**
- SMTP конфигурация через email верификацию
- Тестирование отправки email

### **8. ⏰ Cron задачи (test_cron_only.py):**
- Проверка Celery beat расписания
- database-backup: ежедневно в полночь
- minio-backup: ежедневно в полночь
- cleanup-old-notifications: еженедельно

### **9. 💾 Локальные бекапы (test_backups.py):**
- Создание бекапов PostgreSQL + MinIO
- Автоматическая ротация (последние 7 файлов)
- Сохранение в Docker volume `/app/backups`

### **10. 🔍 Проверка бекапов (check_backup_files.py):**
- Список всех созданных файлов бекапов
- Размеры и даты создания
- Пути к файлам в Docker volume

## 🎯 Результаты тестирования

**✅ ПРОЙДЕНО: 10/10 ТЕСТОВ**

**Дата:** 20.08.2025  
**Статус:** ✅ Все системы работают!  
**Новое:** 🔔 Система уведомлений с Firebase  
**Бекапы:** 💾 Локальная система с ротацией  
**API endpoints:** 25+ протестированных вызовов