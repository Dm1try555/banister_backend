# Cron jobs configuration
CRONJOBS = [
    ('0 0 * * *', 'cron_tasks.cron.database_backup_cron_job'),  # Daily at midnight
    ('0 0 * * *', 'cron_tasks.cron.minio_backup_cron_job'),     # Daily at midnight
    ('0 0 * * 0', 'cron_tasks.cron.notification_cleanup_cron_job'),  # Weekly on Sunday at midnight
]


def database_backup_cron_job():
    """Cron job function for database backup"""
    from django.core.management import call_command
    call_command('backup_database')


def minio_backup_cron_job():
    """Cron job function for MinIO backup"""
    from django.core.management import call_command
    call_command('backup_minio')


def notification_cleanup_cron_job():
    """Cron job function for notification cleanup"""
    from django.core.management import call_command
    call_command('cleanup_notifications') 