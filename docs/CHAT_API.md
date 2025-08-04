# Chat API Documentation

## Обзор

Система чата включает в себя как HTTP API для управления чатами и сообщениями, так и WebSocket API для реального времени обмена сообщениями.

## HTTP API

### Чаты

#### Получить список чатов пользователя
```
GET /api/v1/message/chats/
```

**Ответ:**
```json
{
    "success": true,
    "message": "Список чатов получен успешно",
    "data": [
        {
            "id": 1,
            "type": "private",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "participants": [
                {
                    "id": 1,
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                {
                    "id": 2,
                    "username": "jane_smith",
                    "first_name": "Jane",
                    "last_name": "Smith"
                }
            ],
            "last_message": {
                "id": 123,
                "text": "Привет!",
                "sender": {
                    "id": 1,
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "is_edited": false,
                "is_deleted": false
            },
            "unread_count": 0
        }
    ]
}
```

#### Создать новый чат
```
POST /api/v1/message/chats/
```

**Тело запроса:**
```json
{
    "type": "private",
    "participant_ids": [2, 3]
}
```

**Ответ:**
```json
{
    "success": true,
    "message": "Чат создан успешно",
    "data": {
        "id": 2,
        "type": "private",
        "created_at": "2024-01-15T11:00:00Z",
        "updated_at": "2024-01-15T11:00:00Z",
        "participants": [...],
        "messages": [],
        "last_message": null,
        "unread_count": 0
    }
}
```

#### Получить информацию о чате
```
GET /api/v1/message/chats/{chat_id}/
```

### Сообщения

#### Получить сообщения чата с пагинацией
```
GET /api/v1/message/chats/{chat_id}/messages/?page=1&page_size=50
```

**Параметры:**
- `page` - номер страницы (по умолчанию: 1)
- `page_size` - размер страницы (по умолчанию: 50, максимум: 100)

**Ответ:**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/v1/message/chats/1/messages/?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "chat": 1,
            "sender": {
                "id": 1,
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe"
            },
            "text": "Привет!",
            "timestamp": "2024-01-15T10:30:00Z",
            "is_edited": false,
            "edited_at": null,
            "is_deleted": false,
            "deleted_at": null
        }
    ]
}
```

#### Отправить сообщение
```
POST /api/v1/message/messages/
```

**Тело запроса:**
```json
{
    "chat": 1,
    "text": "Привет, как дела?"
}
```

**Ответ:**
```json
{
    "success": true,
    "message": "Сообщение отправлено успешно",
    "data": {
        "id": 124,
        "chat": 1,
        "sender": {
            "id": 1,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe"
        },
        "text": "Привет, как дела?",
        "timestamp": "2024-01-15T10:35:00Z",
        "is_edited": false,
        "edited_at": null,
        "is_deleted": false,
        "deleted_at": null
    }
}
```

#### Получить информацию о сообщении
```
GET /api/v1/message/messages/{message_id}/
```

#### Редактировать сообщение
```
PUT /api/v1/message/messages/{message_id}/
```

**Тело запроса:**
```json
{
    "text": "Обновленный текст сообщения"
}
```

#### Удалить сообщение
```
DELETE /api/v1/message/messages/{message_id}/
```

## WebSocket API

### Подключение
```
ws://localhost:8000/ws/chat/{chat_id}/
```

### Аутентификация
Передайте JWT токен в заголовке `Authorization`:
```
Authorization: Bearer <your_jwt_token>
```

### Отправка сообщений

#### Новое сообщение
```json
{
    "type": "message",
    "text": "Привет, как дела?"
}
```

#### Индикатор печати
```json
{
    "type": "typing",
    "is_typing": true
}
```

#### Отметка как прочитанное
```json
{
    "type": "read_messages"
}
```

### Получение сообщений

#### Подтверждение подключения
```json
{
    "type": "connection_established",
    "message": "Successfully connected to chat",
    "chat_id": 1
}
```

#### Новое сообщение
```json
{
    "type": "message",
    "data": {
        "id": 124,
        "text": "Привет, как дела?",
        "sender": {
            "id": 1,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe"
        },
        "timestamp": "2024-01-15T10:35:00Z",
        "is_edited": false,
        "is_deleted": false
    }
}
```

#### Индикатор печати
```json
{
    "type": "typing",
    "user_id": 1,
    "username": "john_doe",
    "is_typing": true
}
```

#### Сообщения прочитаны
```json
{
    "type": "messages_read",
    "user_id": 1,
    "username": "john_doe"
}
```

## Модели данных

### Chat
- `id` - уникальный идентификатор
- `type` - тип чата (`private` или `group`)
- `participants` - участники чата (ManyToMany с User)
- `created_at` - дата создания
- `updated_at` - дата последнего обновления

### Message
- `id` - уникальный идентификатор
- `chat` - ссылка на чат
- `sender` - отправитель сообщения
- `text` - текст сообщения
- `timestamp` - время отправки
- `is_edited` - было ли сообщение отредактировано
- `edited_at` - время редактирования
- `is_deleted` - было ли сообщение удалено
- `deleted_at` - время удаления

### ChatUser
- `chat` - ссылка на чат
- `user` - ссылка на пользователя
- `joined_at` - время присоединения к чату
- `is_active` - активен ли пользователь в чате

## Безопасность

1. **Аутентификация**: Все API требуют валидный JWT токен
2. **Авторизация**: Пользователи могут работать только с чатами, в которых они участвуют
3. **Редактирование/удаление**: Пользователи могут редактировать/удалять только свои сообщения
4. **WebSocket**: Соединения проверяются на аутентификацию и авторизацию

## Ограничения

1. **Размер сообщения**: Максимум 1000 символов
2. **Пагинация**: Максимум 100 сообщений на страницу
3. **Частота**: Не более 10 сообщений в минуту на пользователя
4. **WebSocket**: Один пользователь может быть подключен к одному чату только один раз

## Примеры использования

### JavaScript клиент

```javascript
// HTTP API
const token = 'your_jwt_token';

// Получить список чатов
fetch('/api/v1/message/chats/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(response => response.json())
.then(data => console.log(data));

// Отправить сообщение
fetch('/api/v1/message/messages/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        chat: 1,
        text: 'Привет!'
    })
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket
const socket = new WebSocket(`ws://localhost:8000/ws/chat/1/`);

socket.onopen = () => {
    console.log('Connected to chat');
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Отправить сообщение через WebSocket
socket.send(JSON.stringify({
    type: 'message',
    text: 'Привет через WebSocket!'
}));
```

### Python клиент

```python
import requests
import websocket
import json

# HTTP API
token = 'your_jwt_token'
headers = {'Authorization': f'Bearer {token}'}

# Получить список чатов
response = requests.get('http://localhost:8000/api/v1/message/chats/', headers=headers)
chats = response.json()
print(chats)

# Отправить сообщение
data = {'chat': 1, 'text': 'Привет!'}
response = requests.post('http://localhost:8000/api/v1/message/messages/', 
                       headers=headers, json=data)
message = response.json()
print(message)

# WebSocket
def on_message(ws, message):
    data = json.loads(message)
    print('Received:', data)

def on_error(ws, error):
    print('Error:', error)

def on_close(ws, close_status_code, close_msg):
    print('Connection closed')

def on_open(ws):
    print('Connected to chat')
    # Отправить сообщение
    ws.send(json.dumps({
        'type': 'message',
        'text': 'Привет через WebSocket!'
    }))

# Подключение к WebSocket
ws = websocket.WebSocketApp(
    'ws://localhost:8000/ws/chat/1/',
    header={'Authorization': f'Bearer {token}'},
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

## Обработка ошибок

### HTTP API
Все ошибки возвращаются в формате:
```json
{
    "success": false,
    "error_number": "ERROR_CODE",
    "error_message": "Описание ошибки",
    "status_code": 400
}
```

### WebSocket
Ошибки отправляются в формате:
```json
{
    "type": "error",
    "message": "Описание ошибки"
}
```

## Мониторинг

Все операции логируются для отладки и мониторинга:
- Подключения/отключения WebSocket
- Отправленные сообщения
- Ошибки аутентификации и авторизации
- Технические ошибки 