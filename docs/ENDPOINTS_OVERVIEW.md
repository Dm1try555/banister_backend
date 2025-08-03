# Обзор API Эндпоинтов Banister

## 🔐 Аутентификация

### Регистрация
- `POST /api/v1/auth/register/customer/` - Регистрация клиента
- `POST /api/v1/auth/register/provider/` - Регистрация поставщика
- `POST /api/v1/auth/register/management/` - Регистрация менеджера поддержки

### Вход в систему
- `POST /api/v1/auth/login/customer/` - Вход для клиентов
- `POST /api/v1/auth/login/provider/` - Вход для поставщиков
- `POST /api/v1/auth/login/management/` - Вход для менеджеров поддержки
- `POST /api/v1/auth/login/admin/` - Вход для администраторов
- `POST /api/v1/auth/login/superadmin/` - Вход для супер-администраторов
- `POST /api/v1/auth/login/accountant/` - Вход для бухгалтеров

### Управление профилем
- `GET /api/v1/auth/profile/` - Получение профиля
- `PUT /api/v1/auth/profile/` - Обновление профиля
- `DELETE /api/v1/auth/profile/` - Удаление аккаунта

### Сброс пароля
- `POST /api/v1/auth/password-reset/request/` - Запрос кода сброса
- `POST /api/v1/auth/password-reset/confirm/` - Подтверждение сброса

### Подтверждение email
- `POST /api/v1/auth/email-confirm/request/` - Запрос кода подтверждения
- `POST /api/v1/auth/email-confirm/verify/` - Подтверждение email

### Обновление токенов
- `POST /api/v1/auth/token/refresh/` - Обновление access токена

## 👨‍💼 Административная система

### Создание административных ролей (Super Admin)
- `POST /api/v1/auth/admin/create/` - Создание администратора
- `POST /api/v1/auth/admin/create-accountant/` - Создание бухгалтера
- `POST /api/v1/auth/admin/create-support/` - Создание менеджера поддержки

### Управление администраторами
- `GET /api/v1/auth/admin/list/` - Список администраторов (только role='admin')
- `DELETE /api/v1/auth/admin/list/` - Удаление администратора

### CRUD для бухгалтеров (Super Admin)
- `GET /api/v1/auth/accountant/` - Список бухгалтеров
- `PUT /api/v1/auth/accountant/` - Обновление бухгалтера
- `DELETE /api/v1/auth/accountant/` - Удаление бухгалтера

### CRUD для менеджеров поддержки (Super Admin)
- `GET /api/v1/auth/support-manager/` - Список менеджеров поддержки
- `PUT /api/v1/auth/support-manager/` - Обновление менеджера поддержки
- `DELETE /api/v1/auth/support-manager/` - Удаление менеджера поддержки

### Управление разрешениями (Super Admin)

#### Детальная информация
- `GET /api/v1/auth/admin/permissions/detail/` - Список админов с разрешениями
- `POST /api/v1/auth/admin/permissions/detail/` - Массовое обновление разрешений
- `PUT /api/v1/auth/admin/permissions/detail/` - Проверка разрешений
- `DELETE /api/v1/auth/admin/permissions/detail/` - Сброс всех разрешений

#### Гранулярное управление
- `POST /api/v1/auth/admin/permissions/grant/` - Предоставление разрешений
- `POST /api/v1/auth/admin/permissions/revoke/` - Отзыв разрешений
- `GET /api/v1/auth/admin/permissions/list/` - Список разрешений пользователя
- `DELETE /api/v1/auth/admin/permissions/delete/` - Удаление конкретного разрешения

## 🛠️ Услуги

### CRUD для услуг (Providers)
- `GET /api/v1/services/` - Список услуг
- `POST /api/v1/services/` - Создание услуги
- `GET /api/v1/services/{id}/` - Получение услуги
- `PUT /api/v1/services/{id}/` - Обновление услуги
- `DELETE /api/v1/services/{id}/` - Удаление услуги

## 📅 Бронирования

### CRUD для бронирований
- `GET /api/v1/bookings/` - Список бронирований
- `POST /api/v1/bookings/` - Создание бронирования (Customers)
- `GET /api/v1/bookings/{id}/` - Получение бронирования
- `PUT /api/v1/bookings/{id}/` - Обновление бронирования
- `DELETE /api/v1/bookings/{id}/` - Удаление бронирования

### Управление статусом (Providers)
- `POST /api/v1/bookings/status/{booking_id}/` - Изменение статуса бронирования

## 📸 Файлы

### Управление фото профиля
- `POST /api/v1/files/profile-photo/upload/` - Загрузка фото профиля
- `GET /api/v1/files/profile-photo/` - Получение фото профиля
- `DELETE /api/v1/files/profile-photo/delete/` - Удаление фото профиля

## 🌐 Публичные эндпоинты

### Публичные услуги
- `GET /api/v1/public/services/` - Публичный список услуг (без аутентификации)

### Публичные поставщики
- `GET /api/v1/public/providers/` - Публичный список поставщиков (без аутентификации)
- `GET /api/v1/public/providers/{id}/` - Публичная информация о поставщике (без аутентификации)

## 📊 Статус разработки

### ✅ Реализовано
- [x] Полная система аутентификации с 6 ролями
- [x] Административная система с гранулярными разрешениями
- [x] CRUD операции для всех ролей
- [x] Управление профилями и файлами
- [x] Система бронирований
- [x] Публичные эндпоинты
- [x] Swagger документация
- [x] Обработка ошибок
- [x] Логирование

### 🔄 В разработке
- [ ] Система платежей
- [ ] Система вывода средств
- [ ] Система сообщений
- [ ] Управление расписанием
- [ ] Управление документами
- [ ] Аналитика и дашборд


## 🔒 Безопасность

### Реализованные меры
- JWT аутентификация с ролевым доступом
- Гранулярная система разрешений
- Rate limiting для предотвращения брутфорс атак
- Валидация всех входных данных
- Логирование всех административных действий
- Защита от CSRF атак
- Безопасное хранение файлов через MinIO

### Middleware
- `RoleBasedAccessMiddleware` - Контроль доступа на основе ролей
- `AdminPermissionMiddleware` - Проверка разрешений администраторов
- `AdminActivityLoggingMiddleware` - Логирование действий администраторов

## 📝 Документация

- **Swagger UI**: `http://localhost:8000/swagger/`
- **Полная API документация**: `docs/API_DOCUMENTATION.md`
- **Документация аутентификации**: `docs/AUTHENTICATION_API.md`
- **Административная система**: `docs/ADMIN_MANAGEMENT.md`
- **Услуги API**: `docs/SERVICES_API.md`
- **MinIO интеграция**: `docs/MINIO_IMPLEMENTATION.md`
- **Настройка cron задач**: `docs/CRON_SETUP.md` 