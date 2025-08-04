# Notifications API - Система уведомлений с Firebase

## Обзор

API для управления уведомлениями с интеграцией Firebase Cloud Messaging для отправки push-уведомлений в браузер.

## Возможности

- ✅ Создание уведомлений с сохранением в базе данных
- ✅ Отправка push-уведомлений через Firebase
- ✅ Получение списка уведомлений с пагинацией
- ✅ Отметка уведомлений как прочитанных
- ✅ Удаление уведомлений
- ✅ Массовые операции (отметить все как прочитанные, удалить все)
- ✅ Фильтрация по статусу и типу уведомления

## Эндпоинты

### 1. Получить список уведомлений
**URL:** `GET /api/v1/notifications/`

**Параметры запроса:**
- `status` (опционально) - фильтр по статусу: `unread`, `read`, `deleted`
- `notification_type` (опционально) - фильтр по типу уведомления
- `page` (опционально) - номер страницы
- `page_size` (опционально) - размер страницы (максимум 100)

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/?status=unread&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Создать уведомление
**URL:** `POST /api/v1/notifications/create/`

**Тело запроса:**
```json
{
  "user": 1,
  "notification_type": "ClientSendBookingNotigicationToAdmin",
  "data": {
    "booking_id": 123,
    "client_name": "John Doe",
    "service_name": "Cleaning Service"
  },
  "fcm_token": "firebase_fcm_token_here"
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/create/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "notification_type": "ClientSendBookingNotigicationToAdmin",
    "data": {"booking_id": 123, "client_name": "John Doe"},
    "fcm_token": "your_fcm_token"
  }'
```

### 3. Получить детали уведомления
**URL:** `GET /api/v1/notifications/{notification_id}/`

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Отметить уведомление как прочитанное
**URL:** `POST /api/v1/notifications/{notification_id}/read/`

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/1/read/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Удалить уведомление
**URL:** `DELETE /api/v1/notifications/{notification_id}/`

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/notifications/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Отметить все уведомления как прочитанные
**URL:** `POST /api/v1/notifications/mark-all-read/`

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/mark-all-read/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Удалить все уведомления
**URL:** `DELETE /api/v1/notifications/delete-all/`

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/notifications/delete-all/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Типы уведомлений

- `ClientSendBookingNotigicationToAdmin` - Уведомление о бронировании от клиента к админу
- `BookingConfirmed` - Бронирование подтверждено
- `BookingCancelled` - Бронирование отменено
- `PaymentReceived` - Платеж получен
- `PaymentFailed` - Ошибка платежа
- `ServiceUpdated` - Услуга обновлена
- `NewMessage` - Новое сообщение
- `SystemAlert` - Системное уведомление

## Статусы уведомлений

- `unread` - Не прочитано
- `read` - Прочитано
- `deleted` - Удалено

## Настройка Firebase

### 1. Создание проекта Firebase
1. Перейдите на [Firebase Console](https://console.firebase.google.com/)
2. Создайте новый проект
3. Включите Cloud Messaging

### 2. Получение сервисного аккаунта
1. В настройках проекта перейдите в "Service accounts"
2. Создайте новый сервисный ключ
3. Скачайте JSON файл
4. Поместите файл в корень проекта как `firebase-service-account.json`

### 3. Настройка переменных окружения
```bash
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
```

## Интеграция с фронтендом

### 1. Получение FCM токена
```javascript
// В браузере
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';

const firebaseConfig = {
  // Ваша конфигурация Firebase
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// Получить токен
getToken(messaging, { vapidKey: 'YOUR_VAPID_KEY' })
  .then((currentToken) => {
    if (currentToken) {
      // Отправить токен на сервер
      console.log('FCM Token:', currentToken);
    }
  });
```

### 2. Обработка push-уведомлений
```javascript
import { onMessage } from 'firebase/messaging';

onMessage(messaging, (payload) => {
  console.log('Получено уведомление:', payload);
  // Показать уведомление пользователю
});
```

## Структура данных

### Модель Notification
```python
{
  "id": 1,
  "user": 1,
  "user_email": "user@example.com",
  "notification_type": "ClientSendBookingNotigicationToAdmin",
  "notification_type_display": "Уведомление о бронировании от клиента к админу",
  "data": {
    "booking_id": 123,
    "client_name": "John Doe"
  },
  "status": "unread",
  "status_display": "Не прочитано",
  "fcm_token": "firebase_fcm_token",
  "created_at": "2024-01-01T12:00:00Z",
  "read_at": null
}
```

## Обработка ошибок

API использует стандартную систему обработки ошибок проекта:

- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Уведомление не найдено
- `500` - Внутренняя ошибка сервера

## Безопасность

- Все эндпоинты требуют аутентификации
- Пользователи видят только свои уведомления
- Валидация всех входных данных
- Транзакции для операций записи

## Производительность

- Пагинация для больших списков
- Индексы в базе данных для быстрого поиска
- Оптимизированные запросы с select_related
- Асинхронная отправка push-уведомлений 