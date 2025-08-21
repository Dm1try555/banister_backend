from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SerializerClassViewSet(BaseModelViewSet):
    def get_serializer_class(self):
        return self.serializer_class


class RoleBasedViewSet(SerializerClassViewSet):
    admin_roles = ['super_admin', 'admin', 'hr', 'supervisor']
    allowed_roles = []
    
    def get_queryset(self):
        user = self.request.user
        if user.role in self.admin_roles:
            return self.queryset.model.objects.all()
        return self.get_user_records(user)
    
    def get_user_records(self, user):
        return self.queryset.model.objects.none()
    
    def check_role_permission(self):
        user = self.request.user
        if user.role in self.admin_roles:
            return True
        if user.role in self.allowed_roles:
            return True
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Access denied for your role")
    
    def create(self, request, *args, **kwargs):
        self.check_role_permission()
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_role_permission()
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        self.check_role_permission()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.check_role_permission()
        return super().destroy(request, *args, **kwargs)


class CustomerViewSet(RoleBasedViewSet):
    allowed_roles = ['customer']
    
    def get_user_records(self, user):
        if hasattr(self.queryset.model, 'customer'):
            return self.queryset.model.objects.filter(customer=user)
        return self.queryset.model.objects.none()
    
    def create(self, request, *args, **kwargs):
        self.check_role_permission()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data.copy()
        validated_data['customer'] = request.user
        
        if hasattr(self.queryset.model, 'provider') and 'service' in validated_data and validated_data['service']:
            validated_data['provider'] = validated_data['service'].provider
        
        instance = serializer.save(**validated_data)
        
        if hasattr(self, 'serializer_class'):
            full_serializer = self.serializer_class(instance)
        else:
            full_serializer = self.get_serializer(instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class ServiceProviderViewSet(RoleBasedViewSet):
    allowed_roles = ['service_provider']
    
    def get_user_records(self, user):
        if hasattr(self.queryset.model, 'provider'):
            return self.queryset.model.objects.filter(provider=user)
        return self.queryset.model.objects.none()
    
    def create(self, request, *args, **kwargs):
        self.check_role_permission()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(provider=request.user)
        
        if hasattr(self, 'serializer_class'):
            full_serializer = self.serializer_class(instance)
        else:
            full_serializer = self.get_serializer(instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class AdminViewSet(RoleBasedViewSet):
    allowed_roles = []


class NotificationMixin:
    def create_notification(self, user, notification_type, data, push_title=None, push_body=None):
        try:
            from apps.notifications.models import Notification
            from core.firebase.service import firebase_service
            
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                data=data
            )
            
            if user.firebase_token and push_title and push_body:
                firebase_service.send_notification(
                    user_token=user.firebase_token,
                    title=push_title,
                    body=push_body,
                    data=data
                )
        except Exception:
            pass