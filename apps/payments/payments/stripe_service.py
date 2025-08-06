import stripe
import os
from django.conf import settings
from core.mail.service import core.mail_service
from .models import Payment
from core.authentication.models import User

class StripeService:
    """Сервис для работы со Stripe API"""
    
    def __init__(self):
        self.stripe = None
        self._initialize_stripe()
    
    def _initialize_stripe(self):
        """Инициализация Stripe API"""
        try:
            # Получение ключей из переменных окружения
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            if not stripe.api_key:
                print("Stripe API ключ не найден в переменных окружения")
                return
            
            self.stripe = stripe
            print("Stripe API инициализирован успешно")
            
        except Exception as e:
            print(f"Ошибка инициализации Stripe API: {str(e)}")
    
    def create_payment_intent(self, amount, currency='usd', customer_email=None):
        """Создание Payment Intent для обработки платежа"""
        if not self.stripe:
            return False, "Stripe API не инициализирован"
        
        try:
            # Создание Payment Intent
            intent_data = {
                'amount': int(amount * 100),  # Stripe работает в центах
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            # Добавление метаданных если есть email
            if customer_email:
                intent_data['metadata'] = {
                    'customer_email': customer_email
                }
            
            payment_intent = self.stripe.PaymentIntent.create(**intent_data)
            
            return True, {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount,
                'currency': currency
            }
            
        except Exception as e:
            return False, f"Ошибка создания Payment Intent: {str(e)}"
    
    def confirm_payment(self, payment_intent_id):
        """Подтверждение платежа"""
        if not self.stripe:
            return False, "Stripe API не инициализирован"
        
        try:
            payment_intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == 'succeeded':
                return True, {
                    'status': 'succeeded',
                    'amount': payment_intent.amount / 100,
                    'currency': payment_intent.currency,
                    'customer_email': payment_intent.metadata.get('customer_email')
                }
            elif payment_intent.status == 'requires_payment_method':
                return False, "Требуется метод оплаты"
            elif payment_intent.status == 'requires_confirmation':
                return False, "Требуется подтверждение"
            else:
                return False, f"Неожиданный статус платежа: {payment_intent.status}"
                
        except Exception as e:
            return False, f"Ошибка подтверждения платежа: {str(e)}"
    
    def create_customer(self, email, name=None):
        """Создание клиента в Stripe"""
        if not self.stripe:
            return False, "Stripe API не инициализирован"
        
        try:
            customer_data = {
                'email': email,
            }
            
            if name:
                customer_data['name'] = name
            
            customer = self.stripe.Customer.create(**customer_data)
            
            return True, {
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name
            }
            
        except Exception as e:
            return False, f"Ошибка создания клиента: {str(e)}"
    
    def create_payment_method(self, payment_method_id, customer_id):
        """Привязка метода оплаты к клиенту"""
        if not self.stripe:
            return False, "Stripe API не инициализирован"
        
        try:
            payment_method = self.stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            
            return True, {
                'payment_method_id': payment_method.id,
                'type': payment_method.type,
                'card_last4': payment_method.card.last4 if payment_method.card else None
            }
            
        except Exception as e:
            return False, f"Ошибка привязки метода оплаты: {str(e)}"
    
    def process_payment(self, payment_intent_id, user, booking=None):
        """Обработка платежа и обновление базы данных"""
        try:
            # Подтверждение платежа в Stripe
            success, result = self.confirm_payment(payment_intent_id)
            
            if not success:
                return False, result
            
            # Создание или обновление записи платежа в базе данных
            payment_data = {
                'user': user,
                'amount': result['amount'],
                'currency': result['currency'],
                'payment_method': 'stripe',
                'status': 'completed',
                'stripe_payment_intent_id': payment_intent_id,
                'transaction_id': payment_intent_id,
            }
            
            if booking:
                payment_data['booking'] = booking
            
            # Создание записи платежа
            payment = Payment.objects.create(**payment_data)
            
            # Отправка уведомления о успешном платеже
            self._send_payment_confirmation_email(user, payment)
            
            return True, {
                'payment_id': payment.id,
                'amount': payment.amount,
                'currency': payment.currency,
                'status': payment.status
            }
            
        except Exception as e:
            return False, f"Ошибка обработки платежа: {str(e)}"
    
    def _send_payment_confirmation_email(self, user, payment):
        """Отправка email подтверждения платежа"""
        try:
            subject = f'Подтверждение платежа - ${payment.amount}'
            
            message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Ваш платеж был успешно обработан:

Сумма: ${payment.amount} {payment.currency.upper()}
Дата: {payment.created_at.strftime('%d.%m.%Y в %H:%M')}
ID транзакции: {payment.transaction_id}

Спасибо за использование наших услуг!

С уважением,
Команда Banister
            """.strip()
            
            mail_service.send_email(
                subject=subject,
                message=message,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
        except Exception as e:
            print(f"Ошибка отправки email подтверждения платежа: {str(e)}")
    
    def get_payment_status(self, payment_intent_id):
        """Получение статуса платежа"""
        if not self.stripe:
            return False, "Stripe API не инициализирован"
        
        try:
            payment_intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return True, {
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency,
                'created': payment_intent.created,
                'customer_email': payment_intent.metadata.get('customer_email')
            }
            
        except Exception as e:
            return False, f"Ошибка получения статуса платежа: {str(e)}"
    
    def refund_payment(self, payment_intent_id, amount=None):
        """Возврат средств"""
        if not self.stripe:
            return False, "Stripe API не инициализирован"
        
        try:
            refund_data = {
                'payment_intent': payment_intent_id,
            }
            
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = self.stripe.Refund.create(**refund_data)
            
            return True, {
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status
            }
            
        except Exception as e:
            return False, f"Ошибка возврата средств: {str(e)}"

# Глобальный экземпляр сервиса
stripe_service = StripeService() 