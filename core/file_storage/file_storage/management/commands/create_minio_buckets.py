from django.core.management.base import BaseCommand
from core.file_storage.utils import create_bucket_if_not_exists, get_bucket_name_for_file_type

class Command(BaseCommand):
    help = 'Creates necessary buckets in MinIO'

    def handle(self, *args, **options):
        """Creating buckets in MinIO"""
        self.stdout.write('Creating buckets in MinIO...')
        
        # List of all file types and their buckets
        file_types = ['profile_photo', 'document', 'image', 'other']
        
        created_buckets = []
        failed_buckets = []
        
        for file_type in file_types:
            bucket_name = get_bucket_name_for_file_type(file_type)
            
            if create_bucket_if_not_exists(bucket_name):
                created_buckets.append(bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Bucket "{bucket_name}" created successfully')
                )
            else:
                failed_buckets.append(bucket_name)
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating bucket "{bucket_name}"')
                )
        
        # Final report
        self.stdout.write('\n' + '='*50)
        self.stdout.write('BUCKET CREATION SUMMARY:')
        self.stdout.write('='*50)
        
        if created_buckets:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully created: {len(created_buckets)} buckets')
            )
            for bucket in created_buckets:
                self.stdout.write(f'  - {bucket}')
        
        if failed_buckets:
            self.stdout.write(
                self.style.ERROR(f'✗ Creation errors: {len(failed_buckets)} buckets')
            )
            for bucket in failed_buckets:
                self.stdout.write(f'  - {bucket}')
        
        if not failed_buckets:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 All buckets created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Some buckets were not created. Check MinIO connection.')
            ) 