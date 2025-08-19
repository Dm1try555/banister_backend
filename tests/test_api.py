#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    """Тест регистрации пользователя"""
    import random
    user_id = random.randint(1000, 9999)
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": f"testuser{user_id}",
        "first_name": "Test",
        "last_name": "User",
        "email": f"test{user_id}@example.com", 
        "password": "testpass123",
        "password_confirm": "testpass123",
        "role": "customer",
        "location": "New York"
    }
    
    response = requests.post(url, json=data)
    print(f"📝 РЕГИСТРАЦИЯ: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Пользователь создан: {result['user']['username']}")
        print(f"🔑 Access token получен: {result['tokens']['access'][:20]}...")
        return result['tokens']['access']
    else:
        print(f"❌ Ошибка: {response.text}")
        return None

def test_login():
    """Тест логина"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testadmin", 
        "password": "admin123"
    }
    
    response = requests.post(url, json=data)
    print(f"🔐 ЛОГИН: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Логин успешен: {result['user']['username']}")
        print(f"🔑 Access token: {result['tokens']['access'][:20]}...")
        return result['tokens']['access']
    else:
        print(f"❌ Ошибка: {response.text}")
        return None

def test_profile(token):
    """Тест получения профиля"""
    url = f"{BASE_URL}/auth/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"👤 ПРОФИЛЬ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Профиль получен: {result['first_name']} {result['last_name']}")
        print(f"📧 Email: {result['email']}")
        print(f"🎭 Роль: {result['role']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_email_verification():
    """Тест отправки кода верификации"""
    url = f"{BASE_URL}/auth/send-verification/"
    data = {"email": "test456@example.com"}
    
    response = requests.post(url, json=data)
    print(f"📧 ОТПРАВКА КОДА: {response.status_code}")
    if response.status_code == 200:
        print("✅ Код отправлен на email")
    else:
        print(f"❌ Ошибка: {response.text}")

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ API ФУНКЦИОНАЛА\n")
    
    # Тест регистрации
    token = test_registration()
    print()
    
    # Тест логина
    if not token:
        token = test_login()
    print()
    
    # Тест профиля
    if token:
        test_profile(token)
    print()
    
    # Тест email верификации
    test_email_verification()
    print()
    
    print("🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")