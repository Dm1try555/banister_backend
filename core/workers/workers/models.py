from django.db import models
from django.utils import timezone
from core.authentication.models import User


class DataProcessingTask(models.Model):
    """Модель для отслеживания задач обработки данных"""
    
    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменено'),
    )
    
    TASK_TYPE_CHOICES = (
        ('bookings_export', 'Экспорт бронирований'),
        ('payments_export', 'Экспорт платежей'),
        ('users_export', 'Экспорт пользователей'),
        ('services_export', 'Экспорт услуг'),
        ('data_cleanup', 'Очистка данных'),
        ('data_analysis', 'Анализ данных'),
        ('report_generation', 'Генерация отчетов'),
    )
    
    # Основная информация
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Параметры обработки
    batch_size = models.IntegerField(default=100, help_text="Размер пакета для обработки")
    total_records = models.IntegerField(default=0, help_text="Общее количество записей")
    processed_records = models.IntegerField(default=0, help_text="Обработанных записей")
    
    # Фильтры и параметры
    filters = models.JSONField(default=dict, blank=True, help_text="Фильтры для данных")
    date_from = models.DateTimeField(null=True, blank=True, help_text="Дата начала периода")
    date_to = models.DateTimeField(null=True, blank=True, help_text="Дата окончания периода")
    
    # Результаты
    result_file = models.CharField(max_length=255, blank=True, null=True, help_text="Путь к файлу результата")
    error_message = models.TextField(blank=True, null=True, help_text="Сообщение об ошибке")
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Задача обработки данных'
        verbose_name_plural = 'Задачи обработки данных'
    
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def start_processing(self):
        """Начать обработку задачи"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save()
    
    def complete_processing(self, result_file=None):
        """Завершить обработку задачи"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if result_file:
            self.result_file = result_file
        self.save()
    
    def fail_processing(self, error_message):
        """Отметить задачу как неудачную"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()
    
    def update_progress(self, processed_count):
        """Обновить прогресс обработки"""
        self.processed_records = processed_count
        self.save() 