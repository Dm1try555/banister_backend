from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.authentication.models import AdminPermission, User
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an accountant user with financial permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address for the accountant'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the accountant'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Accountant',
            help='First name for the accountant'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the accountant'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='',
            help='Phone number for the accountant'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options['phone']

        # Default financial permissions for accountants
        permissions = [
            'payment_management',
            'withdrawal_management', 
            'financial_reports',
            'document_management'
        ]

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists')
                    )
                    return

                # Create accountant user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='accountant',
                    phone=phone,
                    is_staff=True,
                    is_superuser=False
                )

                # Create profile
                from core.authentication.models import Profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )

                # Grant financial permissions to accountant
                for permission in permissions:
                    AdminPermission.objects.create(
                        admin_user=user,
                        permission=permission,
                        is_active=True,
                        granted_by=None  # Will be set by super admin later
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Accountant user created successfully:\n'
                        f'Email: {email}\n'
                        f'Role: accountant\n'
                        f'Permissions granted: {len(permissions)}\n'
                        f'Permissions: {", ".join(permissions)}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating accountant user: {str(e)}')
            )
            raise 