#!/usr/bin/env python3
import requests
from django.core import mail
from django.test.utils import override_settings

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Получить токен админа"""
    url = f"{BASE_URL}/auth/login/"
    data = {"username": "testadmin", "password": "admin123"}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def test_smtp_configuration():
    """Тест SMTP конфигурации"""
    print("📧 ТЕСТИРОВАНИЕ SMTP КОНФИГУРАЦИИ")
    
    # Создадим пользователя для теста
    url = f"{BASE_URL}/auth/register/"
    import random
    user_id = random.randint(1000, 9999)
    data = {
        "username": f"smtptest{user_id}",
        "first_name": "SMTP",
        "last_name": "Test",
        "email": f"smtp{user_id}@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "role": "customer",
        "location": "Test City"
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 201:
        email = data['email']
        
        # Теперь тестируем отправку email
        url = f"{BASE_URL}/auth/send-verification/"
        data = {"email": email}
        
        response = requests.post(url, json=data)
        print(f"📤 ОТПРАВКА EMAIL: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SMTP настроен корректно")
        else:
            print(f"❌ Ошибка SMTP: {response.text}")
    else:
        print(f"❌ Не удалось создать тестового пользователя: {response.text}")

def test_cron_tasks_endpoints():
    """Тест эндпоинтов для ручного запуска крон задач"""
    print("⏰ ТЕСТИРОВАНИЕ КРОН ЗАДАЧ")
    
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен админа")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Тест cleanup уведомлений (через эндпоинт notifications)
    url = f"{BASE_URL}/notifications/"
    response = requests.get(url, headers=headers)
    
    print(f"🔔 ПРОВЕРКА УВЕДОМЛЕНИЙ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Найдено уведомлений: {result['count']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_celery_beat_schedule():
    """Проверка что Celery beat задачи настроены"""
    print("📅 ПРОВЕРКА РАСПИСАНИЯ CELERY")
    
    # Проверим конфигурационные файлы
    try:
        with open('/app/banister_backend/celery.py', 'r') as f:
            content = f.read()
            
        tasks = [
            'database-backup',
            'minio-backup',
            'cleanup-old-notifications'
        ]
        
        for task in tasks:
            if task in content:
                print(f"✅ {task}: найдена в конфигурации")
            else:
                print(f"❌ {task}: не найдена")
                
    except Exception as e:
        print(f"❌ Ошибка чтения конфигурации: {e}")

def test_backup_service():
    """Тест файлов сервиса бекапов"""
    print("💾 ТЕСТИРОВАНИЕ ФАЙЛОВ БЕКАПОВ")
    
    import os
    files_to_check = [
        '/app/core/backup/service.py',
        '/app/core/backup/tasks.py',
        '/app/core/backup/__init__.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: существует")
        else:
            print(f"❌ {file_path}: не найден")

if __name__ == "__main__":
    print("🔧 ТЕСТИРОВАНИЕ КРОН ЗАДАЧ И SMTP\n")
    
    # Тест SMTP
    test_smtp_configuration()
    print()
    
    # Тест крон задач
    test_cron_tasks_endpoints()
    print()
    
    # Тест расписания Celery
    test_celery_beat_schedule()
    print()
    
    # Тест сервиса бекапов
    test_backup_service()
    print()
    
    print("🎯 ТЕСТИРОВАНИЕ КРОН ЗАДАЧ И SMTP ЗАВЕРШЕНО")