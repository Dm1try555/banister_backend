# WebSocket API для чата

## Обзор

WebSocket API позволяет реализовать реальное время обмена сообщениями в чате. Все соединения требуют аутентификации через JWT токен.

## Подключение

### URL подключения
```
ws://localhost:8000/ws/chat/{chat_id}/
```

### Аутентификация
Для подключения к WebSocket необходимо передать JWT токен в заголовке `Authorization`:
```
Authorization: Bearer <your_jwt_token>
```

### Пример подключения (JavaScript)
```javascript
const token = 'your_jwt_token_here';
const chatId = 1;

const socket = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);

// Добавляем токен в заголовки
socket.onopen = function() {
    // Токен передается автоматически через заголовки
    console.log('Connected to chat');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## Типы сообщений

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

#### Отметка сообщений как прочитанных
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
        "id": 123,
        "text": "Привет, как дела?",
        "sender": {
            "id": 1,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe"
        },
        "timestamp": "2024-01-15T10:30:00Z",
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

#### Ошибка
```json
{
    "type": "error",
    "message": "Описание ошибки"
}
```

## Обработка ошибок

### Типичные ошибки

1. **Неверный токен**
   - Соединение будет закрыто автоматически

2. **Нет доступа к чату**
   - Соединение будет закрыто автоматически

3. **Неверный формат JSON**
   ```json
   {
       "type": "error",
       "message": "Invalid JSON format"
   }
   ```

4. **Пустое сообщение**
   ```json
   {
       "type": "error",
       "message": "Message text cannot be empty"
   }
   ```

5. **Неизвестный тип сообщения**
   ```json
   {
       "type": "error",
       "message": "Unknown message type: invalid_type"
   }
   ```

## Примеры использования

### Полный пример чата (JavaScript)

```javascript
class ChatWebSocket {
    constructor(chatId, token) {
        this.chatId = chatId;
        this.token = token;
        this.socket = null;
        this.isTyping = false;
        this.typingTimeout = null;
    }

    connect() {
        this.socket = new WebSocket(`ws://localhost:8000/ws/chat/${this.chatId}/`);
        
        this.socket.onopen = () => {
            console.log('Connected to chat');
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.socket.onclose = () => {
            console.log('Disconnected from chat');
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'connection_established':
                console.log('Connection established:', data.message);
                break;
                
            case 'message':
                this.displayMessage(data.data);
                break;
                
            case 'typing':
                this.showTypingIndicator(data);
                break;
                
            case 'messages_read':
                this.showReadIndicator(data);
                break;
                
            case 'error':
                console.error('WebSocket error:', data.message);
                break;
        }
    }

    sendMessage(text) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'message',
                text: text
            }));
        }
    }

    startTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.socket.send(JSON.stringify({
                type: 'typing',
                is_typing: true
            }));
        }
        
        // Сбрасываем таймер
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 3000);
    }

    stopTyping() {
        if (this.isTyping) {
            this.isTyping = false;
            this.socket.send(JSON.stringify({
                type: 'typing',
                is_typing: false
            }));
        }
    }

    markAsRead() {
        this.socket.send(JSON.stringify({
            type: 'read_messages'
        }));
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }

    // Методы для отображения (должны быть реализованы в UI)
    displayMessage(message) {
        // Реализация отображения сообщения
        console.log('New message:', message);
    }

    showTypingIndicator(data) {
        // Реализация показа индикатора печати
        console.log('User typing:', data);
    }

    showReadIndicator(data) {
        // Реализация показа индикатора прочтения
        console.log('Messages read by:', data);
    }
}

// Использование
const chat = new ChatWebSocket(1, 'your_jwt_token');
chat.connect();

// Отправка сообщения
chat.sendMessage('Привет!');

// Индикатор печати
chat.startTyping();
setTimeout(() => chat.stopTyping(), 2000);

// Отметка как прочитанное
chat.markAsRead();
```

## Безопасность

1. **Аутентификация**: Все WebSocket соединения требуют валидный JWT токен
2. **Авторизация**: Пользователь может подключаться только к чатам, в которых он является участником
3. **Валидация**: Все входящие сообщения проверяются на корректность
4. **Изоляция**: Каждый чат изолирован в отдельной комнате

## Ограничения

1. **Размер сообщения**: Максимальная длина текста сообщения - 1000 символов
2. **Частота сообщений**: Не более 10 сообщений в минуту на пользователя
3. **Подключения**: Один пользователь может быть подключен к одному чату только один раз

## Мониторинг

Все WebSocket события логируются для отладки и мониторинга:
- Подключения/отключения пользователей
- Отправленные сообщения
- Ошибки аутентификации и авторизации
- Технические ошибки 