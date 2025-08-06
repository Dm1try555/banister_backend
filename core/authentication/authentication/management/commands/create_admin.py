from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.authentication.models import AdminPermission, User
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an admin user with specified permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address for the admin'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the admin'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='First name for the admin'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the admin'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='',
            help='Phone number for the admin'
        )
        parser.add_argument(
            '--permissions',
            nargs='+',
            type=str,
            default=['user_management', 'service_management'],
            help='List of permissions to grant (space-separated)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options['phone']
        permissions = options['permissions']

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists')
                    )
                    return

                # Validate permissions
                valid_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
                invalid_permissions = [p for p in permissions if p not in valid_permissions]
                
                if invalid_permissions:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Invalid permissions: {", ".join(invalid_permissions)}\n'
                            f'Valid permissions: {", ".join(valid_permissions)}'
                        )
                    )
                    return

                # Create admin user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='admin',
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

                # Grant specified permissions to admin
                for permission in permissions:
                    AdminPermission.objects.create(
                        admin_user=user,
                        permission=permission,
                        is_active=True,
                        granted_by=None  # Will be set by super admin later
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Admin user created successfully:\n'
                        f'Email: {email}\n'
                        f'Role: admin\n'
                        f'Permissions granted: {len(permissions)}\n'
                        f'Permissions: {", ".join(permissions)}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
            raise 