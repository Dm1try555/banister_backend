
import requests
import io

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Получить токен админа"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testadmin",
        "password": "admin123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def test_pagination():
    """Тест пагинации списка пользователей"""
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен админа")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Тест с параметрами пагинации
    url = f"{BASE_URL}/users/?page=1&page_size=3"
    response = requests.get(url, headers=headers)
    
    print(f"📄 ПАГИНАЦИЯ ПОЛЬЗОВАТЕЛЕЙ: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Общее количество: {result['count']}")
        print(f"✅ Результатов на странице: {len(result['results'])}")
        print(f"✅ Следующая страница: {'Да' if result['next'] else 'Нет'}")
        print(f"✅ Предыдущая страница: {'Да' if result['previous'] else 'Нет'}")
        
        if result['results']:
            user = result['results'][0]
            print(f"✅ Первый пользователь: {user['username']}")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_upload_profile_photo():
    """Тест загрузки профильной фотографии"""
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен админа")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем фейковое изображение
    fake_image = io.BytesIO()
    fake_image.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x1b[\x1d\x00\x00\x00\x00IEND\xaeB`\x82')
    fake_image.seek(0)
    
    url = f"{BASE_URL}/auth/upload-photo/"
    files = {"photo": ("test.png", fake_image, "image/png")}
    
    response = requests.post(url, files=files, headers=headers)
    
    print(f"📸 ЗАГРУЗКА ФОТО: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Сообщение: {result['message']}")
        print(f"✅ URL фото: {result['photo_url'][:50]}...")
    else:
        print(f"❌ Ошибка: {response.text}")

def test_upload_invalid_file():
    """Тест загрузки неправильного файла"""
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен админа")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем текстовый файл вместо изображения
    fake_file = io.BytesIO(b"This is not an image")
    
    url = f"{BASE_URL}/auth/upload-photo/"
    files = {"photo": ("test.txt", fake_file, "text/plain")}
    
    response = requests.post(url, files=files, headers=headers)
    
    print(f"🚫 НЕПРАВИЛЬНЫЙ ФАЙЛ: {response.status_code}")
    if response.status_code == 400:
        print("✅ Неправильный тип файла корректно отклонен")
    else:
        print(f"❌ Неожиданный ответ: {response.text}")

def test_no_photo_upload():
    """Тест без файла"""
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен админа")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{BASE_URL}/auth/upload-photo/"
    response = requests.post(url, headers=headers)
    
    print(f"📭 БЕЗ ФАЙЛА: {response.status_code}")
    if response.status_code == 400:
        print("✅ Отсутствие файла корректно обработано")
    else:
        print(f"❌ Неожиданный ответ: {response.text}")

if __name__ == "__main__":
    print("🔄 ТЕСТИРОВАНИЕ ПАГИНАЦИИ И MINIO\n")
    
    # Тест пагинации
    test_pagination()
    print()
    
    # Тест загрузки фото
    test_upload_profile_photo()
    print()
    
    # Тест неправильного файла
    test_upload_invalid_file()
    print()
    
    # Тест без файла
    test_no_photo_upload()
    print()
    
    print("🎯 ТЕСТИРОВАНИЕ ПАГИНАЦИИ И MINIO ЗАВЕРШЕНО")