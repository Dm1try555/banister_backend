# Настройка Firebase для уведомлений

## Шаг 1: Создание проекта Firebase

1. Перейдите на [Firebase Console](https://console.firebase.google.com/)
2. Нажмите "Create a project" или "Add project"
3. Введите название проекта (например, "banister-notifications")
4. Выберите настройки Google Analytics (опционально)
5. Нажмите "Create project"

## Шаг 2: Настройка Cloud Messaging

1. В левом меню выберите "Messaging"
2. Нажмите "Get started"
3. Выберите "Web app" как платформу
4. Введите название приложения (например, "Banister Web App")
5. Нажмите "Register app"

## Шаг 3: Получение конфигурации

После регистрации приложения вы получите конфигурацию:

```javascript
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};
```

Сохраните эту конфигурацию для фронтенда.

## Шаг 4: Получение сервисного аккаунта

1. В настройках проекта перейдите в "Project settings"
2. Выберите вкладку "Service accounts"
3. Нажмите "Generate new private key"
4. Скачайте JSON файл
5. Переименуйте файл в `firebase-service-account.json`
6. Поместите файл в корень проекта Django

## Шаг 5: Настройка переменных окружения

Добавьте в ваш `.env` файл:

```bash
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
```

## Шаг 6: Настройка VAPID ключа (для веб-уведомлений)

1. В Firebase Console перейдите в "Project settings"
2. Выберите вкладку "Cloud Messaging"
3. В разделе "Web configuration" найдите "Web Push certificates"
4. Нажмите "Generate key pair"
5. Скопируйте VAPID ключ

## Шаг 7: Интеграция с фронтендом

### Установка Firebase SDK

```bash
npm install firebase
```

### Инициализация Firebase

```javascript
// firebase-config.js
import { initializeApp } from 'firebase/app';
import { getMessaging } from 'firebase/messaging';

const firebaseConfig = {
  // Ваша конфигурация из Firebase Console
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { messaging };
```

### Получение FCM токена

```javascript
import { getToken } from 'firebase/messaging';
import { messaging } from './firebase-config';

const vapidKey = 'YOUR_VAPID_KEY';

export async function getFCMToken() {
  try {
    const currentToken = await getToken(messaging, { vapidKey });
    if (currentToken) {
      console.log('FCM Token:', currentToken);
      // Отправить токен на сервер
      return currentToken;
    } else {
      console.log('No registration token available');
    }
  } catch (error) {
    console.error('Error getting token:', error);
  }
}
```

### Обработка push-уведомлений

```javascript
import { onMessage } from 'firebase/messaging';
import { messaging } from './firebase-config';

export function setupNotificationListener() {
  onMessage(messaging, (payload) => {
    console.log('Получено уведомление:', payload);
    
    // Показать уведомление пользователю
    if ('serviceWorker' in navigator && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(payload.notification.title, {
          body: payload.notification.body,
          icon: '/path/to/icon.png'
        });
      }
    }
  });
}
```

### Service Worker для фоновых уведомлений

Создайте файл `firebase-messaging-sw.js` в папке `public`:

```javascript
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('Получено фоновое уведомление:', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/path/to/icon.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
```

## Шаг 8: Тестирование

### Создание тестового уведомления

```python
from notifications.utils import send_notification

# Отправить тестовое уведомление
notification = send_notification(
    user_id=1,
    notification_type='SystemAlert',
    data={'message': 'Тестовое уведомление'},
    fcm_token='your-fcm-token'
)
```

### Проверка в браузере

1. Откройте консоль разработчика
2. Проверьте, что FCM токен получен
3. Отправьте тестовое уведомление
4. Убедитесь, что уведомление появляется

## Безопасность

### Важные моменты:

1. **Никогда не коммитьте** `firebase-service-account.json` в Git
2. Добавьте файл в `.gitignore`:
   ```
   firebase-service-account.json
   ```
3. Используйте переменные окружения для конфигурации
4. Ограничьте доступ к сервисному аккаунту в Firebase Console

### Настройка CORS (если необходимо)

В Firebase Console:
1. Перейдите в "Authentication" > "Settings"
2. Добавьте домены в "Authorized domains"

## Устранение неполадок

### Ошибка "Firebase не инициализирован"

1. Проверьте путь к файлу сервисного аккаунта
2. Убедитесь, что файл существует и доступен для чтения
3. Проверьте формат JSON файла

### Уведомления не приходят

1. Проверьте FCM токен в базе данных
2. Убедитесь, что Firebase проект настроен правильно
3. Проверьте логи сервера на ошибки
4. Убедитесь, что браузер поддерживает push-уведомления

### Ошибки в браузере

1. Проверьте консоль браузера на ошибки
2. Убедитесь, что Service Worker зарегистрирован
3. Проверьте разрешения на уведомления в браузере

## Дополнительные ресурсы

- [Firebase Cloud Messaging Documentation](https://firebase.google.com/docs/cloud-messaging)
- [Web Push Protocol](https://tools.ietf.org/html/rfc8030)
- [Service Workers API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API) 