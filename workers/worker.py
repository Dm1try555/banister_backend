import csv
import json
import os
from datetime import datetime
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import DataProcessingTask
from bookings.models import Booking
from payments.models import Payment
from authentication.models import User
from services.models import Service


class DataProcessingWorker:
    """Воркер для обработки множественных данных с пагинацией"""
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.task = DataProcessingTask.objects.get(id=task_id)
        self.batch_size = self.task.batch_size
        
    def process_task(self):
        """Основной метод обработки задачи"""
        try:
            # Начинаем обработку
            self.task.start_processing()
            
            # Получаем данные для обработки
            queryset = self._get_queryset_for_task()
            total_records = queryset.count()
            
            if total_records == 0:
                self.task.complete_processing()
                return
            
            # Обновляем общее количество записей
            self.task.total_records = total_records
            self.task.save()
            
            # Создаем пагинатор
            paginator = Paginator(queryset, self.batch_size)
            total_pages = paginator.num_pages
            
            processed_records = 0
            
            # Обрабатываем каждый пакет
            for page_number in range(1, total_pages + 1):
                try:
                    # Получаем данные для текущей страницы
                    page = paginator.page(page_number)
                    records_in_batch = self._process_batch(page.object_list)
                    
                    # Обновляем прогресс
                    processed_records += records_in_batch
                    self.task.update_progress(processed_records)
                    
                except Exception as e:
                    print(f"Ошибка обработки пакета {page_number}: {str(e)}")
                    continue
            
            # Завершаем задачу
            result_file = self._generate_result_file()
            self.task.complete_processing(result_file)
            
        except Exception as e:
            self.task.fail_processing(str(e))
            raise e
    
    def _get_queryset_for_task(self):
        """Получить queryset в зависимости от типа задачи"""
        filters = self.task.filters or {}
        date_from = self.task.date_from
        date_to = self.task.date_to
        
        base_filters = Q()
        
        # Применяем фильтры по датам
        if date_from:
            base_filters &= Q(created_at__gte=date_from)
        if date_to:
            base_filters &= Q(created_at__lte=date_to)
        
        if self.task.task_type == 'bookings_export':
            queryset = Booking.objects.filter(base_filters)
            
            # Дополнительные фильтры для бронирований
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'customer_id' in filters:
                queryset = queryset.filter(customer_id=filters['customer_id'])
            if 'provider_id' in filters:
                queryset = queryset.filter(provider_id=filters['provider_id'])
                
        elif self.task.task_type == 'payments_export':
            queryset = Payment.objects.filter(base_filters)
            
            # Дополнительные фильтры для платежей
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'user_id' in filters:
                queryset = queryset.filter(user_id=filters['user_id'])
                
        elif self.task.task_type == 'users_export':
            queryset = User.objects.filter(base_filters)
            
            # Дополнительные фильтры для пользователей
            if 'role' in filters:
                queryset = queryset.filter(role=filters['role'])
            if 'is_active' in filters:
                queryset = queryset.filter(is_active=filters['is_active'])
                
        elif self.task.task_type == 'services_export':
            queryset = Service.objects.filter(base_filters)
            
            # Дополнительные фильтры для услуг
            if 'provider_id' in filters:
                queryset = queryset.filter(provider_id=filters['provider_id'])
            if 'min_price' in filters:
                queryset = queryset.filter(price__gte=filters['min_price'])
            if 'max_price' in filters:
                queryset = queryset.filter(price__lte=filters['max_price'])
                
        else:
            raise ValueError(f"Неизвестный тип задачи: {self.task.task_type}")
        
        return queryset
    
    def _process_batch(self, records):
        """Обработать пакет записей"""
        processed_count = 0
        
        for record in records:
            try:
                # Здесь можно добавить специфичную логику обработки
                # Например, валидация, трансформация данных и т.д.
                self._process_single_record(record)
                processed_count += 1
                
            except Exception as e:
                # Логируем ошибку, но продолжаем обработку
                print(f"Ошибка обработки записи {record.id}: {str(e)}")
                continue
        
        return processed_count
    
    def _process_single_record(self, record):
        """Обработать одну запись"""
        # Базовая обработка - можно переопределить в наследниках
        if hasattr(record, 'validate_data'):
            record.validate_data()
        
        # Здесь можно добавить дополнительную логику
        # Например, отправка уведомлений, обновление связанных данных и т.д.
        pass
    
    def _generate_result_file(self):
        """Генерировать файл с результатами"""
        try:
            # Создаем директорию для результатов
            results_dir = 'media/worker_results'
            os.makedirs(results_dir, exist_ok=True)
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.task.task_type}_{self.task.id}_{timestamp}.csv"
            filepath = os.path.join(results_dir, filename)
            
            # Получаем данные для экспорта
            queryset = self._get_queryset_for_task()
            
            # Экспортируем в CSV
            self._export_to_csv(queryset, filepath)
            
            return filepath
            
        except Exception as e:
            print(f"Ошибка генерации файла результата: {str(e)}")
            return None
    
    def _export_to_csv(self, queryset, filepath):
        """Экспортировать данные в CSV файл"""
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if self.task.task_type == 'bookings_export':
                self._export_bookings_to_csv(queryset, csvfile)
            elif self.task.task_type == 'payments_export':
                self._export_payments_to_csv(queryset, csvfile)
            elif self.task.task_type == 'users_export':
                self._export_users_to_csv(queryset, csvfile)
            elif self.task.task_type == 'services_export':
                self._export_services_to_csv(queryset, csvfile)
    
    def _export_bookings_to_csv(self, queryset, csvfile):
        """Экспорт бронирований в CSV"""
        fieldnames = [
            'id', 'customer_email', 'provider_email', 'service_title',
            'status', 'location', 'preferred_date', 'preferred_time',
            'scheduled_datetime', 'frequency', 'total_price', 'notes',
            'created_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for booking in queryset.select_related('customer', 'provider', 'service'):
            writer.writerow({
                'id': booking.id,
                'customer_email': booking.customer.email,
                'provider_email': booking.provider.email,
                'service_title': booking.service.title,
                'status': booking.status,
                'location': booking.location,
                'preferred_date': booking.preferred_date,
                'preferred_time': booking.preferred_time,
                'scheduled_datetime': booking.scheduled_datetime,
                'frequency': booking.frequency,
                'total_price': booking.total_price,
                'notes': booking.notes,
                'created_at': booking.created_at
            })
    
    def _export_payments_to_csv(self, queryset, csvfile):
        """Экспорт платежей в CSV"""
        fieldnames = [
            'id', 'user_email', 'amount', 'currency', 'status',
            'payment_method', 'transaction_id', 'created_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for payment in queryset.select_related('user'):
            writer.writerow({
                'id': payment.id,
                'user_email': payment.user.email,
                'amount': payment.amount,
                'currency': payment.currency,
                'status': payment.status,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at
            })
    
    def _export_users_to_csv(self, queryset, csvfile):
        """Экспорт пользователей в CSV"""
        fieldnames = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'phone_number', 'date_joined'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for user in queryset:
            writer.writerow({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'phone_number': user.phone_number,
                'date_joined': user.date_joined
            })
    
    def _export_services_to_csv(self, queryset, csvfile):
        """Экспорт услуг в CSV"""
        fieldnames = [
            'id', 'title', 'description', 'price', 'currency',
            'provider_email', 'category', 'is_active', 'created_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for service in queryset.select_related('provider'):
            writer.writerow({
                'id': service.id,
                'title': service.title,
                'description': service.description,
                'price': service.price,
                'currency': service.currency,
                'provider_email': service.provider.email,
                'category': service.category,
                'is_active': service.is_active,
                'created_at': service.created_at
            })


class BookingDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки бронирований"""
    
    def _process_single_record(self, booking):
        """Обработать одно бронирование"""
        # Специфичная логика для бронирований
        if booking.status == 'pending':
            # Можно добавить логику уведомлений
            pass
        
        # Валидация данных
        if not booking.customer or not booking.provider:
            raise ValueError("Неполные данные бронирования")


class PaymentDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки платежей"""
    
    def _process_single_record(self, payment):
        """Обработать один платеж"""
        # Специфичная логика для платежей
        if payment.status == 'completed':
            # Можно добавить логику обновления баланса
            pass
        
        # Валидация данных
        if payment.amount <= 0:
            raise ValueError("Некорректная сумма платежа")


class UserDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки пользователей"""
    
    def _process_single_record(self, user):
        """Обработать одного пользователя"""
        # Специфичная логика для пользователей
        if not user.is_active:
            # Можно добавить логику деактивации
            pass
        
        # Валидация данных
        if not user.email:
            raise ValueError("Отсутствует email пользователя")


class ServiceDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки услуг"""
    
    def _process_single_record(self, service):
        """Обработать одну услугу"""
        # Специфичная логика для услуг
        if not service.is_active:
            # Можно добавить логику деактивации
            pass
        
        # Валидация данных
        if service.price < 0:
            raise ValueError("Некорректная цена услуги") 