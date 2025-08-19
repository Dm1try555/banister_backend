#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_token():
    """Получить токен пользователя"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser456",
        "password": "testpass123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def test_refresh_token():
    """Тест RefreshTokenView (APIView)"""
    # Сначала логинимся для получения refresh токена
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser456",
        "password": "testpass123"
    }
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        refresh_token = response.json()['tokens']['refresh']
        
        # Тестируем refresh
        url = f"{BASE_URL}/auth/refresh/"
        data = {"refresh": refresh_token}
        response = requests.post(url, json=data)
        
        print(f"🔄 REFRESH TOKEN (APIView): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Новый access токен получен: {result['access'][:20]}...")
        else:
            print(f"❌ Ошибка: {response.text}")
    else:
        print("❌ Не удалось получить refresh токен")

def test_profile_retrieve(token):
    """Тест ProfileView (RetrieveAPIView)"""
    url = f"{BASE_URL}/auth/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"👤 PROFILE (RetrieveAPIView): {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Профиль получен: {result['username']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_user_viewset_crud(token):
    """Тест UserViewSet (ModelViewSet)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET (list) - ListAPIView функционал
    url = f"{BASE_URL}/users/"
    response = requests.get(url, headers=headers)
    print(f"📋 USERS LIST (ModelViewSet): {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Пользователей в списке: {result['count']}")
        
        if result['results']:
            user_id = result['results'][0]['id']
            
            # GET (retrieve) - RetrieveAPIView функционал  
            url = f"{BASE_URL}/users/{user_id}/"
            response = requests.get(url, headers=headers)
            print(f"👤 USER DETAIL (ModelViewSet): {response.status_code}")
            if response.status_code == 200:
                user = response.json()
                print(f"✅ Детали пользователя: {user['username']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_registration_create():
    """Тест RegisterView (CreateAPIView)"""
    import random
    user_id = random.randint(1000, 9999)
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": f"testcreate{user_id}",
        "first_name": "Create",
        "last_name": "Test", 
        "email": f"create{user_id}@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "role": "provider",
        "location": "Test City"
    }
    
    response = requests.post(url, json=data)
    print(f"✨ REGISTER (CreateAPIView): {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Пользователь создан: {result['user']['username']}")
        print(f"🎭 Роль: {result['user']['role']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_swagger_api():
    """Тест доступности Swagger"""
    url = "http://localhost:8000/swagger/"
    response = requests.get(url)
    print(f"📚 SWAGGER UI: {response.status_code}")
    if response.status_code == 200:
        print("✅ Swagger UI доступен")
    else:
        print(f"❌ Swagger недоступен: {response.status_code}")

if __name__ == "__main__":
    print("🏗️ ТЕСТИРОВАНИЕ DRF КЛАССОВ И АРХИТЕКТУРЫ\n")
    
    # Получаем токен
    token = get_token()
    if not token:
        print("❌ Не удалось получить токен")
        exit()
    
    # Тестируем различные DRF классы
    test_registration_create()  # CreateAPIView
    print()
    
    test_profile_retrieve(token)  # RetrieveAPIView  
    print()
    
    test_refresh_token()  # APIView
    print()
    
    test_user_viewset_crud(token)  # ModelViewSet
    print()
    
    test_swagger_api()  # Swagger доступность
    print()
    
    print("🎯 ТЕСТИРОВАНИЕ DRF КЛАССОВ ЗАВЕРШЕНО")