from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from message.models import Message


class Command(BaseCommand):
    help = 'Clean up notifications (messages) older than 2 months'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        try:
            # Calculate cutoff date (2 months ago)
            cutoff_date = timezone.now() - timedelta(days=60)
            
            # Get messages older than 2 months
            old_messages = Message.objects.filter(
                timestamp__lt=cutoff_date
            )
            
            count = old_messages.count()
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(
                        f'DRY RUN: Would delete {count} messages older than {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}'
                    )
                )
                
                # Show some examples of messages that would be deleted
                if count > 0:
                    self.stdout.write('Examples of messages that would be deleted:')
                    for msg in old_messages[:5]:
                        self.stdout.write(
                            f'  - ID: {msg.id}, Text: {msg.text[:50]}..., '
                            f'Timestamp: {msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
                        )
                    if count > 5:
                        self.stdout.write(f'  ... and {count - 5} more messages')
                return
            
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS('No old messages found to delete')
                )
                return
            
            # Delete old messages
            deleted_count = old_messages.delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} messages older than {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during notification cleanup: {str(e)}')
            ) 