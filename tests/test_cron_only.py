#!/usr/bin/env python3
import sys
import os
sys.path.append('/app')

def test_celery_beat_schedule():
    print("⏰ ТЕСТ РАСПИСАНИЯ CRON ЗАДАЧ")
    
    try:
        from banister_backend.celery import app
        
        schedule = app.conf.beat_schedule
        
        expected_tasks = {
            'database-backup': 'каждый день в полночь',
            'minio-backup': 'каждый день в полночь', 
            'cleanup-old-notifications': 'каждое воскресенье в полночь'
        }
        
        for task_name, description in expected_tasks.items():
            if task_name in schedule:
                task_info = schedule[task_name]
                print(f"✅ {task_name}: {description}")
                print(f"   Task: {task_info['task']}")
                print(f"   Schedule: {task_info['schedule']}")
            else:
                print(f"❌ {task_name}: не найдена в расписании")
                
    except Exception as e:
        print(f"❌ Ошибка проверки расписания: {e}")

def test_cleanup_notifications():
    print("\n🗑️ ТЕСТ ОЧИСТКИ УВЕДОМЛЕНИЙ")
    
    try:
        from core.backup.local_service import local_backup_service
        deleted_count = local_backup_service.cleanup_old_notifications()
        print(f"✅ Удалено {deleted_count} старых уведомлений (старше 2 месяцев)")
    except Exception as e:
        print(f"❌ Ошибка очистки уведомлений: {e}")

if __name__ == "__main__":
    test_celery_beat_schedule()
    test_cleanup_notifications()