import csv
import json
import os
from datetime import datetime
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import DataProcessingTask

try:
    from apps.bookings.models import Booking
except ImportError:
    Booking = None

try:
    from apps.payments.models import Payment
except ImportError:
    Payment = None

try:
    from core.authentication.models import User
except ImportError:
    User = None

try:
    from apps.services.models import Service
except ImportError:
    Service = None


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
            if Booking is None:
                raise ImportError("Booking model not available")
            queryset = Booking.objects.filter(base_filters)
            
            # Дополнительные фильтры для бронирований
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'customer_id' in filters:
                queryset = queryset.filter(customer_id=filters['customer_id'])
            if 'provider_id' in filters:
                queryset = queryset.filter(provider_id=filters['provider_id'])
                
        elif self.task.task_type == 'payments_export':
            if Payment is None:
                raise ImportError("Payment model not available")
            queryset = Payment.objects.filter(base_filters)
            
            # Дополнительные фильтры для платежей
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'user_id' in filters:
                queryset = queryset.filter(user_id=filters['user_id'])
                
        elif self.task.task_type == 'users_export':
            if User is None:
                raise ImportError("User model not available")
            queryset = User.objects.filter(base_filters)
            
            # Дополнительные фильтры для пользователей
            if 'role' in filters:
                queryset = queryset.filter(role=filters['role'])
            if 'is_active' in filters:
                queryset = queryset.filter(is_active=filters['is_active'])
                
        elif self.task.task_type == 'services_export':
            if Service is None:
                raise ImportError("Service model not available")
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
        """Экспорт данных в CSV файл"""
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if self.task.task_type == 'bookings_export':
                self._export_bookings_to_csv(queryset, csvfile)
            elif self.task.task_type == 'payments_export':
                self._export_payments_to_csv(queryset, csvfile)
            elif self.task.task_type == 'users_export':
                self._export_users_to_csv(queryset, csvfile)
            elif self.task.task_type == 'services_export':
                self._export_services_to_csv(queryset, csvfile)
            else:
                # Общий экспорт
                writer = csv.writer(csvfile)
                # Заголовки
                if queryset.exists():
                    first_record = queryset.first()
                    headers = [field.name for field in first_record._meta.fields]
                    writer.writerow(headers)
                    
                    # Данные
                    for record in queryset:
                        row = [getattr(record, field.name) for field in first_record._meta.fields]
                        writer.writerow(row)
    
    def _export_bookings_to_csv(self, queryset, csvfile):
        """Экспорт бронирований в CSV"""
        writer = csv.writer(csvfile)
        writer.writerow([
            'ID', 'Customer Email', 'Service Title', 'Provider Email',
            'Status', 'Location', 'Preferred Date', 'Preferred Time',
            'Frequency', 'Scheduled DateTime', 'Total Price', 'Created At'
        ])
        
        for booking in queryset:
            writer.writerow([
                booking.id,
                booking.customer.email if booking.customer else '',
                booking.service.title if booking.service else '',
                booking.provider.email if booking.provider else '',
                booking.status,
                booking.location or '',
                booking.preferred_date or '',
                booking.preferred_time or '',
                booking.frequency,
                booking.scheduled_datetime or '',
                booking.total_price or '',
                booking.created_at
            ])
    
    def _export_payments_to_csv(self, queryset, csvfile):
        """Экспорт платежей в CSV"""
        writer = csv.writer(csvfile)
        writer.writerow([
            'ID', 'User Email', 'Amount', 'Currency', 'Status',
            'Payment Method', 'Transaction ID', 'Description', 'Created At'
        ])
        
        for payment in queryset:
            writer.writerow([
                payment.id,
                payment.user.email if payment.user else '',
                payment.amount,
                payment.currency,
                payment.status,
                payment.payment_method,
                payment.transaction_id or '',
                payment.description or '',
                payment.created_at
            ])
    
    def _export_users_to_csv(self, queryset, csvfile):
        """Экспорт пользователей в CSV"""
        writer = csv.writer(csvfile)
        writer.writerow([
            'ID', 'Email', 'First Name', 'Last Name', 'Role',
            'Is Active', 'Date Joined', 'Last Login'
        ])
        
        for user in queryset:
            writer.writerow([
                user.id,
                user.email,
                user.first_name or '',
                user.last_name or '',
                user.role if hasattr(user, 'role') else '',
                user.is_active,
                user.date_joined,
                user.last_login or ''
            ])
    
    def _export_services_to_csv(self, queryset, csvfile):
        """Экспорт услуг в CSV"""
        writer = csv.writer(csvfile)
        writer.writerow([
            'ID', 'Provider Email', 'Title', 'Description',
            'Price', 'Created At'
        ])
        
        for service in queryset:
            writer.writerow([
                service.id,
                service.provider.email if service.provider else '',
                service.title,
                service.description,
                service.price,
                service.created_at
            ])


class BookingDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки бронирований"""
    
    def _process_single_record(self, booking):
        """Обработать одно бронирование"""
        # Специфичная логика для бронирований
        if hasattr(booking, 'validate_booking'):
            booking.validate_booking()


class PaymentDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки платежей"""
    
    def _process_single_record(self, payment):
        """Обработать один платеж"""
        # Специфичная логика для платежей
        if hasattr(payment, 'validate_payment'):
            payment.validate_payment()


class UserDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки пользователей"""
    
    def _process_single_record(self, user):
        """Обработать одного пользователя"""
        # Специфичная логика для пользователей
        if hasattr(user, 'validate_user'):
            user.validate_user()


class ServiceDataWorker(DataProcessingWorker):
    """Специализированный воркер для обработки услуг"""
    
    def _process_single_record(self, service):
        """Обработать одну услугу"""
        # Специфичная логика для услуг
        if hasattr(service, 'validate_service'):
            service.validate_service() 