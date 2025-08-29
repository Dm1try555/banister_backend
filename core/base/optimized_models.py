"""
Оптимизированные базовые модели для устранения дублирования кода
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    """Базовая модель с общими полями"""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class TimestampedModel(BaseModel):
    """Модель с временными метками"""
    
    class Meta:
        abstract = True


class SoftDeleteModel(BaseModel):
    """Модель с поддержкой soft delete"""
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Hard delete"""
        super().delete(using=using, keep_parents=keep_parents)


class UserRelatedModel(BaseModel):
    """Модель связанная с пользователем"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_set')
    
    class Meta:
        abstract = True


class CustomerProviderModel(BaseModel):
    """Модель с клиентом и провайдером"""
    
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='customer_%(class)s_set',
        limit_choices_to={'role': 'customer'}
    )
    provider = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='provider_%(class)s_set',
        limit_choices_to={'role': 'service_provider'}
    )
    
    class Meta:
        abstract = True


class StatusModel(BaseModel):
    """Модель со статусом"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        abstract = True


class OptimizedModel(BaseModel):
    """Оптимизированная модель с общими методами"""
    
    class Meta:
        abstract = True
    
    def __str__(self):
        """Строковое представление"""
        if hasattr(self, 'name'):
            return self.name
        elif hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'username'):
            return self.username
        elif hasattr(self, 'email'):
            return self.email
        else:
            return f"{self.__class__.__name__} {self.id}"
    
    def get_absolute_url(self):
        """Получение абсолютного URL"""
        if hasattr(self, 'id'):
            return f"/api/v1/{self.__class__.__name__.lower()}/{self.id}/"
        return None
    
    def is_owner(self, user):
        """Проверка владения"""
        if hasattr(self, 'user'):
            return self.user == user
        elif hasattr(self, 'customer'):
            return self.customer == user
        elif hasattr(self, 'provider'):
            return self.provider == user
        return False
    
    def can_edit(self, user):
        """Проверка возможности редактирования"""
        if user.role == 'super_admin':
            return True
        elif user.role == 'admin':
            return getattr(self, 'is_active', True)
        else:
            return self.is_owner(user)
    
    def can_delete(self, user):
        """Проверка возможности удаления"""
        if user.role == 'super_admin':
            return True
        elif user.role == 'admin':
            return getattr(self, 'is_active', True)
        else:
            return self.is_owner(user)


class OptimizedSoftDeleteModel(OptimizedModel, SoftDeleteModel):
    """Оптимизированная модель с soft delete"""
    
    class Meta:
        abstract = True


class OptimizedUserModel(OptimizedModel, UserRelatedModel):
    """Оптимизированная модель связанная с пользователем"""
    
    class Meta:
        abstract = True


class OptimizedCustomerProviderModel(OptimizedModel, CustomerProviderModel):
    """Оптимизированная модель с клиентом и провайдером"""
    
    class Meta:
        abstract = True


class OptimizedStatusModel(OptimizedModel, StatusModel):
    """Оптимизированная модель со статусом"""
    
    class Meta:
        abstract = True


class OptimizedFullModel(OptimizedModel, SoftDeleteModel, StatusModel):
    """Полная оптимизированная модель"""
    
    class Meta:
        abstract = True


class BaseManager(models.Manager):
    """Базовый менеджер с общими методами"""
    
    def active(self):
        """Активные объекты"""
        return self.filter(is_active=True)
    
    def inactive(self):
        """Неактивные объекты"""
        return self.filter(is_active=False)
    
    def not_deleted(self):
        """Не удаленные объекты"""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """Удаленные объекты"""
        return self.filter(is_deleted=True)
    
    def by_user(self, user):
        """Объекты пользователя"""
        return self.filter(user=user)
    
    def by_customer(self, customer):
        """Объекты клиента"""
        return self.filter(customer=customer)
    
    def by_provider(self, provider):
        """Объекты провайдера"""
        return self.filter(provider=provider)


class OptimizedManager(BaseManager):
    """Оптимизированный менеджер"""
    
    def get_queryset(self):
        """Оптимизированный queryset"""
        return super().get_queryset().select_related().prefetch_related()
    
    def with_related(self):
        """Queryset с связанными объектами"""
        return self.get_queryset()
    
    def recent(self, days=30):
        """Недавние объекты"""
        from django.utils import timezone
        from datetime import timedelta
        return self.filter(created_at__gte=timezone.now() - timedelta(days=days))
    
    def this_month(self):
        """Объекты этого месяца"""
        from django.utils import timezone
        now = timezone.now()
        return self.filter(created_at__year=now.year, created_at__month=now.month)
    
    def this_year(self):
        """Объекты этого года"""
        from django.utils import timezone
        now = timezone.now()
        return self.filter(created_at__year=now.year)