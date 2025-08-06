from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.authentication.models import AdminPermission, User
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a super admin user with full permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address for the super admin'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the super admin'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Super',
            help='First name for the super admin'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Admin',
            help='Last name for the super admin'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='',
            help='Phone number for the super admin'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options['phone']

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists')
                    )
                    return

                # Create super admin user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='super_admin',
                    phone=phone,
                    is_staff=True,
                    is_superuser=True
                )

                # Create profile
                from core.authentication.models import Profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )

                # Grant all permissions to super admin
                all_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
                
                for permission in all_permissions:
                    AdminPermission.objects.create(
                        admin_user=user,
                        permission=permission,
                        is_active=True,
                        granted_by=user  # Self-granted for super admin
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Super admin created successfully:\n'
                        f'Email: {email}\n'
                        f'Role: super_admin\n'
                        f'Permissions granted: {len(all_permissions)}\n'
                        f'Permissions: {", ".join(all_permissions)}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating super admin: {str(e)}')
            )
            raise 