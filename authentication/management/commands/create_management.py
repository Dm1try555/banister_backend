from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import User
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a support manager user for customer support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address for the support manager'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the support manager'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Support',
            help='First name for the support manager'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Manager',
            help='Last name for the support manager'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='',
            help='Phone number for the support manager'
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

                # Create support manager user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='management',
                    phone=phone,
                    is_staff=True,
                    is_superuser=False
                )

                # Create profile
                from authentication.models import Profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Support Manager created successfully:\n'
                        f'Email: {email}\n'
                        f'Role: management (Support Manager)\n'
                        f'Name: {first_name} {last_name}\n'
                        f'Responsibilities: Customer support, booking assistance, general inquiries'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating support manager: {str(e)}')
            )
            raise 