
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Получить токен суперадмина"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testadmin",
        "password": "admin123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def create_regular_admin():
    """Создать обычного админа"""
    import random
    admin_id = random.randint(1000, 9999)
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": f"regularadmin{admin_id}",
        "first_name": "Regular", 
        "last_name": "Admin",
        "email": f"admin{admin_id}@regular.com",
        "password": "admin123",
        "password_confirm": "admin123",
        "role": "admin",
        "location": "Office"
    }
    
    response = requests.post(url, json=data)
    print(f"👤 СОЗДАНИЕ ОБЫЧНОГО АДМИНА: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Админ создан: {result['user']['username']} ({result['user']['role']})")
        return result['user']['id']
    else:
        print(f"❌ Ошибка: {response.text}")
        return None

def test_manage_permissions(token, admin_id):
    """Тест управления разрешениями"""
    url = f"{BASE_URL}/auth/admin/manage-permissions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "admin_id": admin_id,
        "permission_name": "users_management", 
        "can_access": True
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"🔐 ВЫДАЧА РАЗРЕШЕНИЯ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Ошибка: {response.text}")
    
    data['can_access'] = False
    response = requests.post(url, json=data, headers=headers)
    print(f"🚫 ОТЗЫВ РАЗРЕШЕНИЯ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_email_verification():
    """Тест верификации email"""
    url = f"{BASE_URL}/auth/send-verification/"
    data = {"email": "admin@regular.com"}
    
    response = requests.post(url, json=data)
    print(f"📧 ОТПРАВКА КОДА ВЕРИФИКАЦИИ: {response.status_code}")
    if response.status_code == 200:
        print("✅ Код верификации отправлен")
    else:
        print(f"❌ Ошибка: {response.text}")
    
    url = f"{BASE_URL}/auth/verify-email/"
    data = {
        "email": "admin@regular.com",
        "code": "123456"
    }
    
    response = requests.post(url, json=data)
    print(f"🔍 ВЕРИФИКАЦИЯ EMAIL: {response.status_code}")
    if response.status_code == 400:
        print("✅ Неправильный код корректно отклонен")
    else:
        print(f"❌ Неожиданный ответ: {response.text}")

if __name__ == "__main__":
    print("🔑 ТЕСТИРОВАНИЕ СИСТЕМЫ РАЗРЕШЕНИЙ\n")
    
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен суперадмина")
        exit()
    
    # Создаем обычного админа
    admin_id = create_regular_admin()
    print()
    
    if admin_id:
        # Тестируем управление разрешениями
        test_manage_permissions(token, admin_id)
        print()
    
    # Тестируем email верификацию
    test_email_verification()
    print()
    
    print("🎯 ТЕСТИРОВАНИЕ СИСТЕМЫ РАЗРЕШЕНИЙ ЗАВЕРШЕНО")