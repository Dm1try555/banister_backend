#!/usr/bin/env python3
import requests
import json

import os
BASE_URL = os.getenv('BASE_URL', "http://localhost:8000/api/v1")

def test_admin_login():
    """Тест логина суперадмина"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testadmin",
        "password": "admin123"
    }
    
    response = requests.post(url, json=data)
    print(f"🔐 АДМИН ЛОГИН: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Админ залогинен: {result['user']['username']}")
        print(f"🎭 Роль: {result['user']['role']}")
        print(f"🔑 Access token: {result['tokens']['access'][:20]}...")
        return result['tokens']['access']
    else:
        print(f"❌ Ошибка: {response.text}")
        return None

def test_admin_profile_update(token):
    """Тест обновления профиля админа"""
    url = f"{BASE_URL}/auth/admin/update-profile/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "first_name": "Super",
        "last_name": "Administrator"
    }
    
    response = requests.patch(url, json=data, headers=headers)
    print(f"✏️ ОБНОВЛЕНИЕ ПРОФИЛЯ АДМИНА: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Профиль обновлен: {result['user']['first_name']} {result['user']['last_name']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_admin_permissions(token):
    """Тест получения разрешений админа"""
    url = f"{BASE_URL}/auth/admin/permissions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"🔑 ПОЛУЧЕНИЕ РАЗРЕШЕНИЙ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Разрешений найдено: {len(result)}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_user_viewset(token):
    """Тест UserViewSet"""
    url = f"{BASE_URL}/users/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Пользователей найдено: {result['count']}")
        if result['results']:
            user = result['results'][0]
            print(f"📋 Первый пользователь: {user['username']} ({user['role']})")
    else:
        print(f"❌ Ошибка: {response.text}")

if __name__ == "__main__":
    print("🛡️ ТЕСТИРОВАНИЕ АДМИН ФУНКЦИЙ\n")
    
    # Тест логина админа
    token = test_admin_login()
    print()
    
    if token:
        # Тест обновления профиля
        test_admin_profile_update(token)
        print()
        
        # Тест разрешений
        test_admin_permissions(token)
        print()
        
        # Тест списка пользователей
        test_user_viewset(token)
        print()
    
    print("🎯 ТЕСТИРОВАНИЕ АДМИН ФУНКЦИЙ ЗАВЕРШЕНО")