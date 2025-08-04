# Настройка Stripe для платежей

## Обзор

Интеграция со Stripe позволяет безопасно обрабатывать платежи с кредитных карт и других методов оплаты, получая средства на вашу банковскую карту.

## Функциональность

### Эндпоинты Stripe:

1. **Создание Payment Intent:**
   ```
   POST /api/v1/payments/stripe/create-intent/
   ```

2. **Подтверждение платежа:**
   ```
   POST /api/v1/payments/stripe/confirm-payment/
   ```

3. **Создание клиента:**
   ```
   POST /api/v1/payments/stripe/create-customer/
   ```

4. **Привязка метода оплаты:**
   ```
   POST /api/v1/payments/stripe/attach-payment-method/
   ```

5. **Проверка статуса платежа:**
   ```
   POST /api/v1/payments/stripe/payment-status/
   ```

6. **Возврат средств:**
   ```
   POST /api/v1/payments/stripe/refund/
   ```

## Настройка Stripe

### 1. Создание аккаунта Stripe

1. Зарегистрируйтесь на [stripe.com](https://stripe.com)
2. Подтвердите email и заполните информацию о бизнесе
3. Добавьте банковскую карту для получения платежей

### 2. Получение API ключей

1. Войдите в [Dashboard Stripe](https://dashboard.stripe.com)
2. Перейдите в "Developers" > "API keys"
3. Скопируйте:
   - **Publishable key** (начинается с `pk_test_` или `pk_live_`)
   - **Secret key** (начинается с `sk_test_` или `sk_live_`)

### 3. Настройка переменных окружения

Добавьте в `.env` файл:

```env
# Stripe API Keys
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here

# Stripe Webhook Secret (опционально)
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 4. Настройка вебхуков (опционально)

1. В Dashboard Stripe перейдите в "Developers" > "Webhooks"
2. Нажмите "Add endpoint"
3. URL: `https://yourdomain.com/api/v1/payments/stripe/webhook/`
4. Выберите события:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`

## Использование API

### Пример создания Payment Intent:

```bash
curl -X POST \
  http://localhost:8000/api/v1/payments/stripe/create-intent/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 99.99,
    "currency": "usd",
    "booking_id": 1,
    "description": "Оплата за услугу"
  }'
```

### Пример ответа:

```json
{
  "success": true,
  "data": {
    "client_secret": "pi_xxx_secret_xxx",
    "payment_intent_id": "pi_xxx",
    "amount": 99.99,
    "currency": "usd",
    "payment_id": 1
  },
  "message": "Payment Intent создан успешно"
}
```

### Пример подтверждения платежа:

```bash
curl -X POST \
  http://localhost:8000/api/v1/payments/stripe/confirm-payment/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_xxx",
    "booking_id": 1
  }'
```

## Интеграция с фронтендом

### 1. Подключение Stripe.js

```html
<script src="https://js.stripe.com/v3/"></script>
```

### 2. Инициализация Stripe

```javascript
const stripe = Stripe('pk_test_your_publishable_key_here');
```

### 3. Создание Payment Intent

```javascript
// Создание Payment Intent на бэкенде
const response = await fetch('/api/v1/payments/stripe/create-intent/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    amount: 99.99,
    currency: 'usd',
    booking_id: 1
  })
});

const { client_secret } = await response.json();
```

### 4. Подтверждение платежа

```javascript
// Подтверждение платежа
const { error } = await stripe.confirmCardPayment(client_secret, {
  payment_method: {
    card: elements.getElement('card'),
    billing_details: {
      name: 'Иван Иванов',
      email: 'ivan@example.com'
    }
  }
});

if (error) {
  console.error('Ошибка платежа:', error);
} else {
  // Платеж успешен
  await fetch('/api/v1/payments/stripe/confirm-payment/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      payment_intent_id: paymentIntent.id,
      booking_id: 1
    })
  });
}
```

## Безопасность

- ✅ Все платежи обрабатываются через Stripe (PCI DSS compliant)
- ✅ Секретные ключи хранятся в переменных окружения
- ✅ Проверка аутентификации для всех платежных операций
- ✅ Валидация данных на сервере
- ✅ Логирование всех платежных операций

## Поддерживаемые методы оплаты

- 💳 Кредитные и дебетовые карты (Visa, MasterCard, American Express)
- 🏦 Банковские переводы (ACH)
- 📱 Apple Pay, Google Pay
- 💰 PayPal (через Stripe)

## Комиссии Stripe

- **Стандартная комиссия:** 2.9% + $0.30 за успешный платеж
- **Международные платежи:** +1% за валютную конвертацию
- **Возвраты:** Комиссия не возвращается

## Тестирование

### Тестовые карты:

- **Успешный платеж:** `4242 4242 4242 4242`
- **Недостаточно средств:** `4000 0000 0000 0002`
- **Карта отклонена:** `4000 0000 0000 0002`
- **3D Secure:** `4000 0025 0000 3155`

### Тестовые данные:

- **CVV:** Любые 3 цифры
- **Дата:** Любая будущая дата
- **Почтовый индекс:** Любой

## Мониторинг платежей

1. **Stripe Dashboard:** Просмотр всех транзакций
2. **Webhooks:** Автоматические уведомления о событиях
3. **Логи:** Детальная информация о платежах в базе данных
4. **Email уведомления:** Подтверждения платежей пользователям

## Поддержка

- 📧 **Stripe Support:** [support.stripe.com](https://support.stripe.com)
- 📚 **Документация:** [stripe.com/docs](https://stripe.com/docs)
- 🐛 **Отладка:** Проверьте логи Stripe в Dashboard 