#!/usr/bin/env python3
import requests
import random

BASE_URL = "http://localhost:8000/api/v1"

def test_smtp_email_sending():
    print("📧 ТЕСТ ОТПРАВКИ EMAIL")
    
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
    
    url = f"{BASE_URL}/auth/register/"
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print("✅ Пользователь создан")
        
        url = f"{BASE_URL}/auth/send-verification/"
        email_data = {"email": data['email']}
        response = requests.post(url, json=email_data)
        
        if response.status_code == 200:
            print("✅ Email отправлен через SMTP")
        else:
            print(f"❌ Ошибка отправки email: {response.text}")
    else:
        print(f"❌ Ошибка создания пользователя: {response.text}")

if __name__ == "__main__":
    test_smtp_email_sending()