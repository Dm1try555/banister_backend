# Настройка Google Calendar API

## Обзор

Интеграция с Google Calendar API позволяет автоматически создавать события встреч и отправлять приглашения пользователям с подтвержденной почтой.

## Функциональность

### Эндпоинты для отправки приглашений:

1. **Для пользователей (клиент/провайдер):**
   ```
   POST /api/v1/bookings/{booking_id}/send-invitation/
   ```

2. **Для администраторов:**
   ```
   POST /api/v1/bookings/{booking_id}/admin/send-invitation/
   ```

### Что происходит при отправке приглашения:

1. **Создание события в Google Calendar** с деталями встречи
2. **Отправка email уведомлений** пользователям с подтвержденной почтой
3. **Добавление участников** в событие календаря
4. **Настройка напоминаний** (за день и за 30 минут)

## Настройка Google Calendar API

### 1. Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Calendar API:
   - Перейдите в "APIs & Services" > "Library"
   - Найдите "Google Calendar API"
   - Нажмите "Enable"

### 2. Создание сервисного аккаунта

1. Перейдите в "APIs & Services" > "Credentials"
2. Нажмите "Create Credentials" > "Service Account"
3. Заполните форму:
   - **Name**: `banister-calendar-service`
   - **Description**: `Service account for Google Calendar integration`
4. Нажмите "Create and Continue"
5. Пропустите шаги с ролями (нажмите "Continue")
6. Нажмите "Done"

### 3. Создание ключа сервисного аккаунта

1. Найдите созданный сервисный аккаунт в списке
2. Нажмите на email сервисного аккаунта
3. Перейдите на вкладку "Keys"
4. Нажмите "Add Key" > "Create new key"
5. Выберите "JSON" и нажмите "Create"
6. Скачайте файл ключа

### 4. Настройка календаря

1. Переименуйте скачанный файл в `google-service-account.json`
2. Поместите файл в корневую папку проекта Django
3. Предоставьте доступ к календарю сервисному аккаунту:
   - Откройте Google Calendar
   - Найдите email сервисного аккаунта в настройках
   - Добавьте его как участника с правами "Make changes to events"

### 5. Настройка переменных окружения

Добавьте в `.env` файл:

```env
# Google Calendar API
GOOGLE_CALENDAR_ENABLED=True
GOOGLE_SERVICE_ACCOUNT_FILE=google-service-account.json
```

## Использование API

### Пример запроса для отправки приглашения:

```bash
curl -X POST \
  http://localhost:8000/api/v1/bookings/1/send-invitation/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Пример ответа:

```json
{
  "success": true,
  "data": {
    "calendar_created": true,
    "calendar_event_id": "abc123def456",
    "emails_sent": 2,
    "total_users": 2
  },
  "message": "Приглашения отправлены. Email отправлено: 2/2"
}
```

## Требования к пользователям

Для отправки приглашений пользователь должен иметь:
- ✅ Подтвержденную почту (`email` не пустой)
- ✅ Активный статус (`is_active = True`)
- ✅ Участие в бронировании (клиент или провайдер)

## Безопасность

- ✅ Проверка прав доступа (только участники бронирования или админ)
- ✅ Проверка статуса бронирования (только confirmed/pending)
- ✅ Проверка наличия времени встречи
- ✅ Транзакционная обработка данных

## Обработка ошибок

API возвращает понятные сообщения об ошибках:

- `AUTHENTICATION_REQUIRED` - требуется аутентификация
- `PERMISSION_DENIED` - нет прав для отправки
- `BOOKING_NOT_FOUND` - бронирование не найдено
- `INVALID_STATUS` - неподходящий статус бронирования
- `NO_SCHEDULED_TIME` - время встречи не назначено
- `INVITATION_SEND_ERROR` - ошибка отправки приглашений

## Тестирование

Для тестирования без реального Google Calendar API:

1. Создайте тестовый файл `google-service-account.json` с минимальными данными
2. API будет работать в режиме "только email" без создания событий в календаре
3. Проверьте логи на наличие сообщений об ошибках инициализации API 