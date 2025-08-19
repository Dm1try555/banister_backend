from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
import string
from ..models import User, AdminPermission
from ..serializers import UserSerializer, AdminPermissionSerializer
from core.error_handling.exceptions import AuthenticationError
from core.error_handling.enums import ErrorCode