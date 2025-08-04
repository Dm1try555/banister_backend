from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
from .models import Notification
from .serializers import (
    NotificationSerializer, CreateNotificationSerializer, 
    NotificationStatusSerializer, NotificationListSerializer
)
from .firebase_service import firebase_service
from error_handling.views import BaseAPIView
from error_handling.utils import format_validation_errors
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(BaseAPIView):
    """View для получения списка уведомлений с пагинацией"""
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    @swagger_auto_schema(
        operation_description="Получить список уведомлений пользователя с пагинацией",
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY, description="Фильтр по статусу уведомления",
                type=openapi.TYPE_STRING, enum=['unread', 'read', 'deleted'], required=False),
            openapi.Parameter(
                'notification_type', openapi.IN_QUERY, description="Фильтр по типу уведомления",
                type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: openapi.Response('Список уведомлений', NotificationListSerializer(many=True))},
        tags=['Notifications']
    )
    def get(self, request):
        queryset = self._get_filtered_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NotificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NotificationListSerializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список уведомлений получен успешно')

    def _get_filtered_queryset(self):
        """Получить отфильтрованный queryset уведомлений"""
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Фильтр по статусу
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтр по типу уведомления
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset


class NotificationDetailView(BaseAPIView):
    """View для работы с конкретным уведомлением"""
    http_method_names = ['get', 'delete']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить детальную информацию об уведомлении",
        responses={200: openapi.Response('Детали уведомления', NotificationSerializer)},
        tags=['Notifications']
    )
    def get(self, request, notification_id):
        notification = self._get_notification_with_permissions(request, notification_id)
        serializer = NotificationSerializer(notification)
        return self.success_response(data=serializer.data, message='Детали уведомления получены успешно')

    @swagger_auto_schema(
        operation_description="Удалить уведомление",
        responses={200: openapi.Response('Уведомление удалено', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)}))},
        tags=['Notifications']
    )
    @transaction.atomic
    def delete(self, request, notification_id):
        notification = self._get_notification_with_permissions(request, notification_id)
        notification.mark_as_deleted()
        return self.success_response(data={'status': 'deleted'}, message='Уведомление удалено успешно')

    def _get_notification_with_permissions(self, request, notification_id):
        """Получить уведомление с проверкой прав доступа"""
        return Notification.objects.get(id=notification_id, user=request.user)


class NotificationMarkAsReadView(BaseAPIView):
    """View для отметки уведомления как прочитанного"""
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Отметить уведомление как прочитанное",
        responses={200: openapi.Response('Уведомление отмечено как прочитанное', NotificationSerializer)},
        tags=['Notifications']
    )
    @transaction.atomic
    def post(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        serializer = NotificationSerializer(notification)
        return self.success_response(data=serializer.data, message='Уведомление отмечено как прочитанное')


class NotificationMarkAllAsReadView(BaseAPIView):
    """View для отметки всех уведомлений как прочитанных"""
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Отметить все уведомления пользователя как прочитанные",
        responses={200: openapi.Response('Все уведомления отмечены как прочитанные', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'updated_count': openapi.Schema(type=openapi.TYPE_INTEGER)}))},
        tags=['Notifications']
    )
    @transaction.atomic
    def post(self, request):
        updated_count = Notification.objects.filter(
            user=request.user, 
            status='unread'
        ).update(
            status='read',
            read_at=timezone.now()
        )
        return self.success_response(
            data={'updated_count': updated_count}, 
            message=f'Отмечено как прочитанные: {updated_count} уведомлений'
        )


class NotificationDeleteAllView(BaseAPIView):
    """View для удаления всех уведомлений пользователя"""
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Удалить все уведомления пользователя",
        responses={200: openapi.Response('Все уведомления удалены', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'deleted_count': openapi.Schema(type=openapi.TYPE_INTEGER)}))},
        tags=['Notifications']
    )
    @transaction.atomic
    def delete(self, request):
        deleted_count = Notification.objects.filter(user=request.user).update(status='deleted')
        return self.success_response(
            data={'deleted_count': deleted_count}, 
            message=f'Удалено уведомлений: {deleted_count}'
        )


class NotificationCreateView(BaseAPIView):
    """View для создания уведомлений (внутренний API)"""
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создать новое уведомление и отправить через Firebase",
        request_body=CreateNotificationSerializer,
        responses={201: openapi.Response('Уведомление создано', NotificationSerializer)},
        tags=['Notifications']
    )
    @transaction.atomic
    def post(self, request):
        serializer = CreateNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        
        notification = serializer.save()
        
        # Отправляем push-уведомление через Firebase
        if notification.fcm_token:
            title = self._get_notification_title(notification.notification_type)
            body = self._get_notification_body(notification.notification_type, notification.data)
            
            firebase_service.send_notification(
                fcm_token=notification.fcm_token,
                title=title,
                body=body,
                data=notification.data
            )
        
        response_serializer = NotificationSerializer(notification)
        return self.success_response(
            data=response_serializer.data, 
            message='Уведомление создано и отправлено', 
            status_code=201
        )

    def _get_notification_title(self, notification_type):
        """Получить заголовок уведомления по типу"""
        titles = {
            'ClientSendBookingNotigicationToAdmin': 'Новое бронирование',
            'BookingConfirmed': 'Бронирование подтверждено',
            'BookingCancelled': 'Бронирование отменено',
            'PaymentReceived': 'Платеж получен',
            'PaymentFailed': 'Ошибка платежа',
            'ServiceUpdated': 'Услуга обновлена',
            'NewMessage': 'Новое сообщение',
            'SystemAlert': 'Системное уведомление',
        }
        return titles.get(notification_type, 'Новое уведомление')

    def _get_notification_body(self, notification_type, data):
        """Получить текст уведомления по типу и данным"""
        if notification_type == 'ClientSendBookingNotigicationToAdmin':
            return f"Новое бронирование от клиента"
        elif notification_type == 'BookingConfirmed':
            return f"Ваше бронирование подтверждено"
        elif notification_type == 'BookingCancelled':
            return f"Бронирование отменено"
        elif notification_type == 'PaymentReceived':
            return f"Платеж успешно получен"
        elif notification_type == 'PaymentFailed':
            return f"Ошибка при обработке платежа"
        elif notification_type == 'ServiceUpdated':
            return f"Информация об услуге обновлена"
        elif notification_type == 'NewMessage':
            return f"У вас новое сообщение"
        elif notification_type == 'SystemAlert':
            return f"Системное уведомление"
        else:
            return "У вас новое уведомление"
