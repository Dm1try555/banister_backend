# Stripe Payment Integration

Полная документация по интеграции платежной системы Stripe в Banister Backend.

## 📋 Содержание

1. [Настройка Stripe](#настройка-stripe)
2. [Эндпоинты платежей](#эндпоинты-платежей)
3. [Финансовые операции](#финансовые-операции)
4. [Модели данных](#модели-данных)
5. [Обработка ошибок](#обработка-ошибок)
6. [Тестирование](#тестирование)

## 🔧 Настройка Stripe

### Переменные окружения

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_CONNECT_CLIENT_ID=ca_...
```

### Установка зависимостей

```bash
pip install stripe
```

### Конфигурация в settings.py

```python
# Stripe settings
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
STRIPE_CONNECT_CLIENT_ID = os.getenv('STRIPE_CONNECT_CLIENT_ID')
```

## 💳 Эндпоинты платежей

### 1. Создание Payment Intent

**Эндпоинт:** `POST /api/payments/create-payment-intent/`

**Описание:** Создает платежное намерение в Stripe для обработки платежа.

**Запрос:**
```json
{
    "amount": 1000,
    "currency": "usd",
    "booking_id": 123,
    "description": "Payment for service"
}
```

**Ответ:**
```json
{
    "success": true,
    "data": {
        "client_secret": "pi_..._secret_...",
        "payment_intent_id": "pi_...",
        "amount": 1000,
        "currency": "usd"
    }
}
```

### 2. Подтверждение платежа

**Эндпоинт:** `POST /api/payments/confirm-payment/`

**Описание:** Подтверждает успешный платеж и обновляет статус в базе данных.

**Запрос:**
```json
{
    "payment_intent_id": "pi_...",
    "booking_id": 123
}
```

**Ответ:**
```json
{
    "success": true,
    "data": {
        "payment_id": 1,
        "status": "completed",
        "amount": 1000,
        "currency": "usd"
    }
}
```

### 3. История платежей

**Эндпоинт:** `GET /api/payments/payment-history/`

**Описание:** Получает историю платежей пользователя с пагинацией.

**Параметры:**
- `page` - Номер страницы (по умолчанию 1)
- `page_size` - Размер страницы (по умолчанию 10)
- `status` - Фильтр по статусу (опционально)

**Ответ:**
```json
{
    "success": true,
    "data": {
        "payments": [
            {
                "id": 1,
                "amount": 1000,
                "currency": "usd",
                "status": "completed",
                "created_at": "2024-01-01T12:00:00Z",
                "booking_id": 123
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_count": 50
        }
    }
}
```

### 4. Возврат средств

**Эндпоинт:** `POST /api/payments/refund/`

**Описание:** Выполняет возврат средств за платеж.

**Запрос:**
```json
{
    "payment_id": 1,
    "amount": 1000,
    "reason": "customer_request"
}
```

**Ответ:**
```json
{
    "success": true,
    "data": {
        "refund_id": "re_...",
        "amount": 1000,
        "status": "succeeded"
    }
}
```

### 5. Статус платежа

**Эндпоинт:** `GET /api/payments/{payment_id}/status/`

**Описание:** Получает текущий статус платежа.

**Ответ:**
```json
{
    "success": true,
    "data": {
        "payment_id": 1,
        "status": "completed",
        "amount": 1000,
        "currency": "usd",
        "stripe_payment_intent_id": "pi_..."
    }
}
```

## 💰 Финансовые операции

### Получение финансов на карту системы

Система автоматически получает комиссию с каждого платежа:

```python
# Пример расчета комиссии
def calculate_platform_fee(amount):
    """Рассчитывает комиссию платформы (5%)"""
    return int(amount * 0.05)

def calculate_provider_payout(amount):
    """Рассчитывает выплату провайдеру (95%)"""
    return amount - calculate_platform_fee(amount)
```

### Отправка средств провайдерам

**Эндпоинт:** `POST /api/withdrawals/`

**Описание:** Создает запрос на вывод средств для провайдера.

**Запрос:**
```json
{
    "amount": 5000,
    "bank_account": {
        "account_number": "1234567890",
        "routing_number": "021000021"
    }
}
```

### Автоматические выплаты

Система поддерживает автоматические выплаты провайдерам:

1. **Еженедельные выплаты** - каждую пятницу
2. **Минимальная сумма** - $50
3. **Автоматическое одобрение** - для проверенных провайдеров

## 📊 Модели данных

### Payment Model

```python
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payments')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provider_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
```

### Withdrawal Model

```python
class Withdrawal(models.Model):
    WITHDRAWAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=WITHDRAWAL_STATUS_CHOICES, default='pending')
    bank_account_info = models.JSONField()
    stripe_transfer_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
```

## ⚠️ Обработка ошибок

### Типичные ошибки Stripe

```python
ERROR_CODES = {
    'card_declined': 'Карта отклонена',
    'insufficient_funds': 'Недостаточно средств',
    'expired_card': 'Карта истекла',
    'invalid_cvc': 'Неверный CVC код',
    'processing_error': 'Ошибка обработки платежа',
    'rate_limit': 'Превышен лимит запросов',
}
```

### Обработка в коде

```python
try:
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        metadata={'booking_id': booking_id}
    )
except stripe.error.CardError as e:
    return error_response(
        error_number='CARD_ERROR',
        error_message=str(e),
        status_code=400
    )
except stripe.error.RateLimitError as e:
    return error_response(
        error_number='RATE_LIMIT',
        error_message='Превышен лимит запросов',
        status_code=429
    )
```

## 🧪 Тестирование

### Тестовые карты Stripe

```bash
# Успешный платеж
4242 4242 4242 4242

# Недостаточно средств
4000 0000 0000 0002

# Карта отклонена
4000 0000 0000 0002

# Требует аутентификацию
4000 0025 0000 3155
```

### Тестовые команды

```bash
# Создание тестового платежа
python manage.py shell
>>> from payments.stripe_service import stripe_service
>>> stripe_service.create_test_payment(1000, 'usd')

# Проверка статуса платежа
>>> stripe_service.get_payment_status('pi_test_...')
```

## 🔒 Безопасность

### Меры безопасности

1. **Валидация данных** - все входные данные проверяются
2. **Транзакции БД** - все операции обернуты в транзакции
3. **Логирование** - все платежные операции логируются
4. **Webhook проверка** - подпись webhook'ов проверяется
5. **Rate limiting** - ограничение частоты запросов

### Переменные окружения для продакшена

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_CONNECT_CLIENT_ID=ca_...
```

## 📈 Мониторинг

### Метрики для отслеживания

- Общий объем платежей
- Успешность платежей
- Среднее время обработки
- Количество возвратов
- Комиссия платформы

### Логирование

```python
import logging

logger = logging.getLogger('stripe_payments')

def log_payment_event(event_type, payment_id, amount):
    logger.info(f"Payment {event_type}: {payment_id}, Amount: {amount}")
```

## 🚀 Развертывание

### Продакшен чек-лист

- [ ] Настроены live ключи Stripe
- [ ] Настроены webhook'и
- [ ] Проверена обработка ошибок
- [ ] Настроено логирование
- [ ] Проверены тестовые сценарии
- [ ] Настроен мониторинг
- [ ] Проверена безопасность

### Команды для развертывания

```bash
# Применение миграций
python manage.py migrate

# Создание индексов
python manage.py create_indexes

# Проверка конфигурации
python manage.py check_stripe_config
``` 