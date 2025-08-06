from rest_framework import serializers
from .models import DataProcessingTask
from django.utils import timezone


class DataProcessingTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач обработки данных"""
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = DataProcessingTask
        fields = [
            'id', 'task_type', 'task_type_display', 'status', 'status_display',
            'created_by', 'created_by_email', 'total_records', 'processed_records',
            'progress_percentage', 'result_file', 'error_message', 'created_at', 
            'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'total_records', 'processed_records',
            'result_file', 'error_message', 'created_at', 'started_at', 'completed_at'
        ]
    
    def get_progress_percentage(self, obj):
        """Вычислить процент выполнения"""
        if obj.total_records == 0:
            return 0
        return round((obj.processed_records / obj.total_records) * 100, 2)


class CreateTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для создания новой задачи"""
    
    class Meta:
        model = DataProcessingTask
        fields = [
            'task_type', 'batch_size', 'filters', 'date_from', 'date_to'
        ]
    
    def validate_batch_size(self, value):
        """Проверить размер пакета"""
        if value < 1 or value > 10000:
            raise serializers.ValidationError(
                "Размер пакета должен быть от 1 до 10000"
            )
        return value
    
    def validate_date_from(self, value):
        """Проверить дату начала"""
        if value and hasattr(self, 'initial_data'):
            date_to = self.initial_data.get('date_to')
            if date_to and value > date_to:
                raise serializers.ValidationError(
                    "Дата начала не может быть позже даты окончания"
                )
        return value


class TaskStatusSerializer(serializers.ModelSerializer):
    """Сериализатор для статуса задачи"""
    
    progress_percentage = serializers.SerializerMethodField()
    estimated_time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = DataProcessingTask
        fields = [
            'id', 'status', 'total_records', 'processed_records',
            'progress_percentage', 'estimated_time_remaining', 'error_message'
        ]
    
    def get_progress_percentage(self, obj):
        """Вычислить процент выполнения"""
        if obj.total_records == 0:
            return 0
        return round((obj.processed_records / obj.total_records) * 100, 2)
    
    def get_estimated_time_remaining(self, obj):
        """Оценить оставшееся время"""
        if obj.status != 'processing' or obj.processed_records == 0:
            return None
        
        if obj.started_at:
            elapsed_time = (timezone.now() - obj.started_at).total_seconds()
            if elapsed_time > 0:
                records_per_second = obj.processed_records / elapsed_time
                remaining_records = obj.total_records - obj.processed_records
                if records_per_second > 0:
                    remaining_seconds = remaining_records / records_per_second
                    return int(remaining_seconds)
        return None 