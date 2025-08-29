# Django imports
from django.contrib.auth import authenticate
from django.db import models, transaction
from django.db.models import Q, F, Count, Sum, Avg, Max, Min
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.files.storage import default_storage

# DRF imports
from rest_framework import status, serializers
from rest_framework.decorators import permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView,
    ListCreateAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# Swagger imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Optimized imports
from core.base.optimized_views import (
    BaseAuthenticatedView, BaseAuthenticatedCreateView, BaseAuthenticatedListCreateView,
    BaseAuthenticatedDetailView, BaseAuthenticatedUpdateView, BaseAuthenticatedModelViewSet,
    OptimizedListCreateView, OptimizedRetrieveUpdateDestroyView, OptimizedRetrieveUpdateView,
    OptimizedCreateView, OptimizedModelViewSet, BaseAPIView, TransactionalMixin
)
from core.base.optimized_serializers import (
    BaseModelSerializer, TimestampedSerializer, UserSerializer, UserCreateSerializer,
    UserUpdateSerializer, SoftDeleteSerializer, OptimizedModelSerializer
)
from core.base.optimized_permissions import (
    BaseRolePermission, AdminOnlyPermission, SuperAdminOnlyPermission, ProviderPermission,
    CustomerPermission, StaffPermission, OptimizedPermissionMixin, BaseObjectPermission,
    OwnerPermission, OptimizedPermission, RoleBasedPermission
)
from core.base.optimized_models import (
    BaseModel, TimestampedModel, SoftDeleteModel, UserRelatedModel, CustomerProviderModel,
    StatusModel, OptimizedModel, OptimizedSoftDeleteModel, OptimizedUserModel,
    OptimizedCustomerProviderModel, OptimizedStatusModel, OptimizedFullModel,
    BaseManager, OptimizedManager
)
from drf_yasg import openapi

# Local imports
from .swagger_mixin import SwaggerMixin
from .permissions import BasePermissionsMixin, RoleBasedQuerysetMixin

# Legacy imports for backward compatibility
from rest_framework.permissions import IsAuthenticated
from .validation_mixins import EmailValidationMixin, PhoneValidationMixin, PasswordValidationMixin, CommonValidationMixin

# Error handling
from core.error_handling.enums import ErrorCode
from core.error_handling.utils import create_error_response, handle_validation_error
from core.error_handling.exceptions import CustomValidationError

# Swagger schemas
from core.swagger_schemas import *

# Logging
import logging
logger = logging.getLogger(__name__)
