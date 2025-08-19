from django.core.management.base import BaseCommand
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Create superadmin user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--password', type=str, help='Password')
        parser.add_argument('--first-name', type=str, help='First name')
        parser.add_argument('--last-name', type=str, help='Last name')

    def handle(self, *args, **options):
        username = options.get('username') or input('Username: ')
        email = options.get('email') or input('Email: ')
        password = options.get('password') or input('Password: ')
        first_name = options.get('first_name') or input('First name: ')
        last_name = options.get('last_name') or input('Last name: ')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User {username} already exists'))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='super_admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Superadmin {username} created successfully')
        )