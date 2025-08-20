#!/usr/bin/env python3
import requests
import json
import os

BASE_URL = os.getenv('BASE_URL', "http://localhost:8000/api/v1")

def get_admin_token():
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testadmin",
        "password": "admin123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def test_notification_crud():
    print("🔔 ТЕСТ CRUD ОПЕРАЦИЙ УВЕДОМЛЕНИЙ")
    
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получаем ID текущего пользователя
    profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    if profile_response.status_code != 200:
        print("❌ Не удалось получить профиль")
        return
    
    user_id = profile_response.json()['id']
    
    # 1. Создание уведомления
    print("\n📝 СОЗДАНИЕ УВЕДОМЛЕНИЯ:")
    notification_data = {
        "user": user_id,
        "notification_type": "ClientSendBookingNotificationToAdmin",
        "data": {
            "booking_id": 123,
            "message": "New booking request"
        }
    }
    
    response = requests.post(f"{BASE_URL}/notifications/", 
                           json=notification_data, headers=headers)
    print(f"Создание: {response.status_code}")
    
    if response.status_code == 201:
        notification = response.json()
        notification_id = notification['id']
        print(f"✅ Уведомление создано: ID {notification_id}")
        print(f"   Тип: {notification['notification_type']}")
        
        # 2. Получение списка уведомлений
        print("\n📋 СПИСОК УВЕДОМЛЕНИЙ:")
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
        print(f"Список: {response.status_code}")
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Найдено уведомлений: {notifications['count']}")
        
        # 3. Пометить как прочитанное
        print("\n👁️ ПОМЕТИТЬ КАК ПРОЧИТАННОЕ:")
        response = requests.post(f"{BASE_URL}/notifications/{notification_id}/mark_read/", 
                               headers=headers)
        print(f"Пометить прочитанным: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Уведомление помечено как прочитанное")
        
        # 4. Удаление уведомления
        print("\n🗑️ УДАЛЕНИЕ УВЕДОМЛЕНИЯ:")
        response = requests.delete(f"{BASE_URL}/notifications/{notification_id}/", 
                                 headers=headers)
        print(f"Удаление: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ Уведомление удалено")
    
    else:
        print(f"❌ Ошибка создания: {response.text}")

def test_bulk_operations():
    print("\n📦 ТЕСТ МАССОВЫХ ОПЕРАЦИЙ")
    
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получаем ID текущего пользователя
    profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    user_id = profile_response.json()['id']
    
    # Создаем несколько уведомлений
    for i in range(3):
        notification_data = {
            "user": user_id,
            "notification_type": f"TestNotification{i+1}",
            "data": {"test": f"data{i+1}"}
        }
        
        response = requests.post(f"{BASE_URL}/notifications/", 
                               json=notification_data, headers=headers)
        print(f"Создание {i+1}: {response.status_code}")
    
    # Пометить все как прочитанные
    print("\n👁️ ПОМЕТИТЬ ВСЕ КАК ПРОЧИТАННЫЕ:")
    response = requests.post(f"{BASE_URL}/notifications/mark_all_read/", headers=headers)
    print(f"Пометить все: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Все уведомления помечены как прочитанные")
    
    # Удалить все уведомления
    print("\n🗑️ УДАЛИТЬ ВСЕ УВЕДОМЛЕНИЯ:")
    response = requests.delete(f"{BASE_URL}/notifications/delete_all/", headers=headers)
    print(f"Удалить все: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['status']}")

def test_pagination():
    print("\n📄 ТЕСТ ПАГИНАЦИИ")
    
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/notifications/?page=1", headers=headers)
    print(f"Пагинация: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Страница 1: {len(data.get('results', []))} результатов")
        print(f"   Всего: {data.get('count', 0)}")
        print(f"   Следующая страница: {'Да' if data.get('next') else 'Нет'}")

if __name__ == "__main__":
    print("🔔 ТЕСТИРОВАНИЕ СИСТЕМЫ УВЕДОМЛЕНИЙ")
    print("=" * 50)
    
    test_notification_crud()
    test_bulk_operations()
    test_pagination()
    
    print("\n🎯 ТЕСТИРОВАНИЕ УВЕДОМЛЕНИЙ ЗАВЕРШЕНО")