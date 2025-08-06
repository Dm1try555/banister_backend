from django.db import models
from core.authentication.models import User
from apps.bookings.models import Booking

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    CURRENCY_CHOICES = (
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('rub', 'RUB'),
    )
    
    # Основная информация
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Сумма и валюта
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')
    
    # Статус и метод оплаты
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='stripe')
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe интеграция
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Общая информация о транзакции
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Метаданные
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
    
    def __str__(self):
        return f"Payment {self.id} - ${self.amount} {self.currency} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Автоматическое обновление completed_at при завершении платежа
        if self.status == 'completed' and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        """Проверка успешности платежа"""
        return self.status in ['completed']
    
    @property
    def is_pending(self):
        """Проверка ожидания платежа"""
        return self.status in ['pending', 'processing']
    
    @property
    def is_failed(self):
        """Проверка неудачного платежа"""
        return self.status in ['failed', 'cancelled']
    
    def get_formatted_amount(self):
        """Получение отформатированной суммы"""
        return f"${self.amount} {self.currency.upper()}"
    
    def get_payment_method_display_name(self):
        """Получение отображаемого названия метода оплаты"""
        method_names = {
            'stripe': 'Credit Card (Stripe)',
            'paypal': 'PayPal',
            'cash': 'Cash',
            'bank_transfer': 'Bank Transfer',
        }
        return method_names.get(self.payment_method, self.payment_method.title())