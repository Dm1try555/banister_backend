from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from workers.models import DataProcessingTask
from workers.worker import (
    DataProcessingWorker, BookingDataWorker, PaymentDataWorker,
    UserDataWorker, ServiceDataWorker
)


class Command(BaseCommand):
    help = 'Запустить воркер для обработки задач с пагинацией'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--task-id',
            type=int,
            help='ID конкретной задачи для обработки'
        )
        parser.add_argument(
            '--task-type',
            type=str,
            choices=['bookings_export', 'payments_export', 'users_export', 'services_export'],
            help='Тип задачи для обработки'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['pending', 'processing'],
            default='pending',
            help='Статус задач для обработки'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Размер пакета для обработки'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Запустить воркер в непрерывном режиме'
        )
        parser.add_argument(
            '--sleep-interval',
            type=int,
            default=10,
            help='Интервал проверки новых задач в секундах (для непрерывного режима)'
        )
    
    def handle(self, *args, **options):
        task_id = options.get('task_id')
        task_type = options.get('task_type')
        status = options.get('status')
        batch_size = options.get('batch_size')
        continuous = options.get('continuous')
        sleep_interval = options.get('sleep_interval')
        
        if task_id:
            # Обработать конкретную задачу
            self.process_specific_task(task_id)
        elif continuous:
            # Запустить воркер в непрерывном режиме
            self.run_continuous_worker(task_type, status, batch_size, sleep_interval)
        else:
            # Обработать все задачи с указанными параметрами
            self.process_tasks(task_type, status, batch_size)
    
    def process_specific_task(self, task_id):
        """Обработать конкретную задачу"""
        try:
            task = DataProcessingTask.objects.get(id=task_id)
            self.stdout.write(f"Обрабатываем задачу {task_id}: {task.task_type}")
            
            worker = self.get_worker_for_task(task)
            worker.process_task()
            
            self.stdout.write(
                self.style.SUCCESS(f"Задача {task_id} обработана успешно")
            )
            
        except DataProcessingTask.DoesNotExist:
            raise CommandError(f"Задача {task_id} не найдена")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Ошибка обработки задачи {task_id}: {str(e)}")
            )
    
    def process_tasks(self, task_type, status, batch_size):
        """Обработать все задачи с указанными параметрами"""
        queryset = DataProcessingTask.objects.filter(status=status)
        
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        
        tasks = queryset.order_by('created_at')
        
        if not tasks.exists():
            self.stdout.write("Нет задач для обработки")
            return
        
        self.stdout.write(f"Найдено {tasks.count()} задач для обработки")
        
        for task in tasks:
            try:
                self.stdout.write(f"Обрабатываем задачу {task.id}: {task.task_type}")
                
                # Обновляем размер пакета если указан
                if batch_size != 100:
                    task.batch_size = batch_size
                    task.save()
                
                worker = self.get_worker_for_task(task)
                worker.process_task()
                
                self.stdout.write(
                    self.style.SUCCESS(f"Задача {task.id} обработана успешно")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка обработки задачи {task.id}: {str(e)}")
                )
    
    def run_continuous_worker(self, task_type, status, batch_size, sleep_interval):
        """Запустить воркер в непрерывном режиме"""
        self.stdout.write("Запуск воркера в непрерывном режиме...")
        self.stdout.write(f"Интервал проверки: {sleep_interval} секунд")
        
        import time
        
        while True:
            try:
                # Ищем задачи для обработки
                queryset = DataProcessingTask.objects.filter(status=status)
                
                if task_type:
                    queryset = queryset.filter(task_type=task_type)
                
                tasks = queryset.order_by('created_at')
                
                if tasks.exists():
                    self.stdout.write(f"Найдено {tasks.count()} задач для обработки")
                    
                    for task in tasks:
                        try:
                            self.stdout.write(f"Обрабатываем задачу {task.id}: {task.task_type}")
                            
                            # Обновляем размер пакета если указан
                            if batch_size != 100:
                                task.batch_size = batch_size
                                task.save()
                            
                            worker = self.get_worker_for_task(task)
                            worker.process_task()
                            
                            self.stdout.write(
                                self.style.SUCCESS(f"Задача {task.id} обработана успешно")
                            )
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"Ошибка обработки задачи {task.id}: {str(e)}")
                            )
                else:
                    self.stdout.write("Нет задач для обработки")
                
                # Ждем перед следующей проверкой
                time.sleep(sleep_interval)
                
            except KeyboardInterrupt:
                self.stdout.write("Воркер остановлен пользователем")
                break
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка воркера: {str(e)}")
                )
                time.sleep(sleep_interval)
    
    def get_worker_for_task(self, task):
        """Получить соответствующий воркер для задачи"""
        if task.task_type == 'bookings_export':
            return BookingDataWorker(task.id)
        elif task.task_type == 'payments_export':
            return PaymentDataWorker(task.id)
        elif task.task_type == 'users_export':
            return UserDataWorker(task.id)
        elif task.task_type == 'services_export':
            return ServiceDataWorker(task.id)
        else:
            return DataProcessingWorker(task.id) 