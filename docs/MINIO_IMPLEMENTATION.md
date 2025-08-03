# MinIO Implementation - Complete Documentation

## 📋 **Задание выполнено полностью**

### ✅ **1. MinIO подключен в docker-compose.yml**
- Сервис MinIO настроен и готов к работе
- Автоматическое создание бакетов при первой загрузке
- Консоль управления доступна на порту 9001

### ✅ **2. Эндпоинты для профильных фотографий созданы**
- `/api/v1/files/profile-photo/upload/` - универсальная загрузка/смена фотографии
- `/api/v1/files/profile-photo/` - получение текущей фотографии
- `/api/v1/files/profile-photo/delete/` - удаление фотографии

### ✅ **3. Автоматическое создание бакетов**
- Бакеты создаются автоматически при первой загрузке файла
- Поддержка разных типов файлов (profile-photos, documents, images, misc)

### ✅ **4. Валидация обязательности для провайдеров и менеджеров**
- Профильная фотография обязательна для ролей `provider` и `management`
- Проверка при обновлении профиля
- Уведомления в UI о необходимости загрузки

### ✅ **5. UI компонент для быстрой смены фотографии**
- Drag & Drop загрузка
- Предварительный просмотр
- Валидация форматов и размера файла
- Красивый интерфейс с подтверждением

---

## 🚀 **Техническая реализация**

### **Backend (Django REST API)**

#### **Модели:**
```python
# file_storage/models.py
class FileStorage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    bucket_name = models.CharField(max_length=100)
    object_key = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)

class ProfilePhoto(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file_storage = models.OneToOneField(FileStorage, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
```

#### **Утилиты MinIO:**
```python
# file_storage/utils.py
def create_bucket_if_not_exists(bucket_name):
    """Автоматическое создание бакета"""
    client = get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

def upload_file_to_minio(file_obj, bucket_name, object_key, content_type):
    """Загрузка файла в MinIO"""
    client = get_minio_client()
    create_bucket_if_not_exists(bucket_name)  # Автоматическое создание
    client.put_object(bucket_name, object_key, file_obj, content_type=content_type)
```

#### **Валидация обязательности:**
```python
# authentication/models.py
def has_required_profile_photo(self):
    """Проверка обязательности фото для провайдеров и менеджеров"""
    if self.role in ['provider', 'management']:
        try:
            from file_storage.models import ProfilePhoto
            return ProfilePhoto.objects.filter(user=self, is_active=True).exists()
        except Exception:
            return False
    return True  # Клиенты могут не иметь фото
```

### **Frontend (Nuxt3)**

#### **Компонент загрузки:**
```vue
<!-- frontend/components/ProfilePhotoUploader.vue -->
<template>
  <div class="profile-photo-uploader">
    <!-- Текущая фотография -->
    <div class="current-photo" v-if="currentPhotoUrl">
      <img :src="currentPhotoUrl" alt="Current profile photo" />
    </div>
    
    <!-- Область загрузки -->
    <div class="upload-area" @click="triggerFileInput" @drop="handleDrop">
      <!-- Drag & Drop интерфейс -->
    </div>
    
    <!-- Предварительный просмотр -->
    <div v-if="previewImage" class="preview-container">
      <img :src="previewImage" alt="Preview" />
      <div class="preview-overlay">
        <button @click="confirmUpload">Confirm</button>
        <button @click="cancelUpload">Cancel</button>
      </div>
    </div>
  </div>
</template>
```

#### **Страница профиля:**
```vue
<!-- frontend/pages/profile.vue -->
<template>
  <div class="profile-page">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Секция фотографии -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2>Profile Photo</h2>
        <ProfilePhotoUploader
          :current-photo-url="user?.profile_photo_url"
          :is-required="isPhotoRequired"
          @photo-uploaded="handlePhotoUploaded"
        />
        
        <!-- Уведомление об обязательности -->
        <div v-if="isPhotoRequired" class="mt-4 p-3 bg-blue-50">
          <p><strong>Note:</strong> Profile photo is required for {{ user?.role }} accounts.</p>
        </div>
      </div>
      
      <!-- Информация профиля -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2>Profile Information</h2>
        <form @submit.prevent="updateProfile">
          <!-- Поля формы -->
        </form>
      </div>
    </div>
  </div>
</template>
```

---

## 🔧 **API Endpoints**

### **Загрузка/смена профильной фотографии**
```http
POST /api/v1/files/profile-photo/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

{
  "photo": <file>
}
```

**Ответ (первая загрузка):**
```json
{
  "success": true,
  "message": "Profile photo uploaded successfully",
  "timestamp": "2025-01-31T19:36:59.900765+00:00",
  "data": {
    "id": "1df4cf9b-ef49-42b5-8bb9-5bc03052600c",
    "user": {
      "id": 112,
      "email": "provider@example.com",
      "phone": "1234567890",
      "role": "provider",
      "profile": {
        "first_name": "John",
        "last_name": "Doe",
        "bio": ""
      },
      "provider_profile": {
        "experience_years": 0,
        "hourly_rate": "0.00"
      },
      "profile_photo_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg",
      "has_required_profile_photo": true
    },
    "file_storage": {
      "id": "300917b4-91dd-4abc-bb9e-504fadd38461",
      "file_name": "profile_photo_112",
      "original_name": "profile.jpg",
      "file_type": "profile_photo",
      "bucket_name": "profile-photos",
      "object_key": "112/profile_photo/20250131_193659_e1f2b717.jpg",
      "file_size": 107236,
      "content_type": "image/jpeg",
      "is_public": true,
      "created_at": "2025-01-31T19:36:59.444490Z",
      "updated_at": "2025-01-31T19:36:59.444508Z",
      "file_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg",
      "public_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg"
    },
    "is_active": true,
    "created_at": "2025-01-31T19:36:59.453362Z",
    "updated_at": "2025-01-31T19:36:59.453418Z",
    "photo_url": "http://localhost:9000/profile-photos/112/profile_photo/20250131_193659_e1f2b717.jpg"
  }
}
```

**Ответ (смена фото):**
```json
{
  "success": true,
  "message": "Profile photo changed successfully",
  "timestamp": "2025-01-31T19:36:59.900765+00:00",
  "data": {
    // Same structure as above
  }
}
```

**Особенности:**
- ✅ **Универсальный эндпоинт** - работает для первой загрузки и замены
- ✅ **Автоматическое удаление** старых файлов при замене
- ✅ **Валидация файлов** - формат, размер, тип
- ✅ **Обработка ошибок** - подробные сообщения об ошибках

### **Получение профильной фотографии**
```http
GET /api/v1/files/profile-photo/
Authorization: Bearer <token>
```

### **Удаление профильной фотографии**
```http
DELETE /api/v1/files/profile-photo/delete/
Authorization: Bearer <token>
```

---

## 🎨 **UI Features**

### **Функциональность:**
- ✅ Drag & Drop загрузка файлов
- ✅ Предварительный просмотр изображения
- ✅ Валидация форматов (JPG, PNG, GIF)
- ✅ Ограничение размера файла (5MB)
- ✅ Автоматическое изменение размера изображения
- ✅ Подтверждение/отмена загрузки
- ✅ Индикатор загрузки
- ✅ Обработка ошибок
- ✅ Уведомления об успехе/ошибке

### **Дизайн:**
- ✅ Современный и отзывчивый интерфейс
- ✅ Круглые профильные фотографии
- ✅ Hover эффекты
- ✅ Анимации загрузки
- ✅ Адаптивная верстка
- ✅ Цветовая схема в стиле Tailwind CSS

---

## 🔒 **Безопасность**

### **Валидация файлов:**
- Проверка MIME-типа
- Ограничение размера файла
- Проверка расширения файла
- Автоматическое изменение размера изображения

### **Права доступа:**
- Только авторизованные пользователи
- Пользователи могут загружать только свои фотографии
- Проверка ролей для обязательности фото

### **Хранение:**
- Файлы хранятся в MinIO (S3-совместимое хранилище)
- Автоматическое создание бакетов
- Уникальные ключи для файлов
- Поддержка публичных и приватных файлов

---

## 📊 **Производительность**

### **Оптимизация изображений:**
- Автоматическое изменение размера до 800x800px
- Сжатие JPEG с качеством 85%
- Конвертация в RGB формат

### **Кэширование:**
- Presigned URLs для быстрого доступа
- Время жизни ссылок: 1 час

### **Масштабируемость:**
- MinIO поддерживает горизонтальное масштабирование
- Возможность добавления реплик
- Поддержка CDN

---

## 🚀 **Развертывание**

### **Docker Compose:**
```yaml
minio:
  image: minio/minio:latest
  container_name: minio_banister
  command: server /data --console-address ":9001"
  environment:
    - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
    - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
  volumes:
    - minio_data:/data
  ports:
    - "9000:9000"
    - "9001:9001"
```

### **Переменные окружения:**
```env
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_ENDPOINT=minio:9000
```

---

## 📝 **Использование**

### **Для разработчиков:**

1. **Загрузка/смена фотографии:**
```javascript
const formData = new FormData()
formData.append('photo', file)

const response = await $fetch('/api/v1/files/profile-photo/upload/', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

2. **Получение URL фотографии:**
```javascript
const profile = await $fetch('/api/v1/auth/profile/')
const photoUrl = profile.profile_photo_url
```

### **Для пользователей:**

1. Перейти на страницу профиля
2. Нажать на область загрузки или перетащить файл
3. Выбрать изображение (JPG, PNG, GIF до 5MB)
4. Предварительный просмотр
5. Подтвердить загрузку
6. Фотография автоматически обновится

---

## ✅ **Готово к продакшену**

Все требования заказчика выполнены:
- ✅ MinIO подключен в docker-compose
- ✅ Универсальный эндпоинт для загрузки/смены фотографий
- ✅ Автоматическое создание бакетов
- ✅ UI для загрузки фотографий
- ✅ Обязательность для провайдеров и менеджеров
- ✅ Поддержка всех ролей пользователей
- ✅ Современный и удобный интерфейс
- ✅ Полная валидация и обработка ошибок
- ✅ Автоматическое удаление старых файлов при замене
- ✅ Безопасность: запрет изменения ролей через профиль 