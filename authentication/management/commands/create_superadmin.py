from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a super admin user with profile'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email for super admin')
        parser.add_argument('--password', type=str, required=True, help='Password for super admin')
        parser.add_argument('--first-name', type=str, required=True, help='First name')
        parser.add_argument('--last-name', type=str, required=True, help='Last name')
        parser.add_argument('--phone', type=str, help='Phone number (optional)')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options.get('phone', '')

        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.ERROR(f'User with email {email} already exists!')
                )
                return

            # Create super admin user
            user = User.objects.create_user(
                email=email,
                password=password,
                role='super_admin',
                phone=phone,
                is_staff=True,
                is_superuser=True,
                is_active=True
            )

            # Create profile
            Profile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                is_email_confirmed=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Super admin created successfully!\n'
                    f'Email: {email}\n'
                    f'Name: {first_name} {last_name}\n'
                    f'Role: Super Admin'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating super admin: {str(e)}')
            ) 