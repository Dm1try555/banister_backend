# MinIO Implementation - Complete Documentation

## 📋 **Задание выполнено полностью**

### ✅ **1. MinIO подключен в docker-compose.yml**
- Сервис MinIO настроен и готов к работе
- Автоматическое создание бакетов при первой загрузке
- Консоль управления доступна на порту 9001

### ✅ **2. Эндпоинты для профильных фотографий созданы**
- `/api/file-storage/profile-photo/upload/` - загрузка новой фотографии
- `/api/file-storage/profile-photo/quick-change/` - быстрая смена фотографии
- `/api/file-storage/profile-photo/` - получение текущей фотографии
- `/api/file-storage/profile-photo/delete/` - удаление фотографии

### ✅ **3. Автоматическое создание бакетов**
- Бакеты создаются автоматически при первой загрузке файла
- Поддержка разных типов файлов (profile-photos, documents, images, misc)

### ✅ **4. Валидация обязательности для админов и провайдеров**
- Профильная фотография обязательна для ролей `admin` и `provider`
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
    """Проверка обязательности фото для админов и провайдеров"""
    if self.role in ['admin', 'provider']:
        return hasattr(self, 'profile_photo') and self.profile_photo.is_active
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

### **Загрузка профильной фотографии**
```http
POST /api/file-storage/profile-photo/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

{
  "photo": <file>
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user": {...},
    "file_storage": {
      "file_url": "https://minio:9000/profile-photos/...",
      "public_url": "/media/profile-photos/..."
    },
    "photo_url": "https://minio:9000/profile-photos/...",
    "is_active": true
  },
  "message": "Profile photo uploaded successfully"
}
```

### **Быстрая смена фотографии**
```http
POST /api/file-storage/profile-photo/quick-change/
Content-Type: multipart/form-data
Authorization: Bearer <token>

{
  "photo": <file>
}
```

### **Получение профильной фотографии**
```http
GET /api/file-storage/profile-photo/
Authorization: Bearer <token>
```

### **Удаление профильной фотографии**
```http
DELETE /api/file-storage/profile-photo/delete/
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

1. **Загрузка фотографии:**
```javascript
const formData = new FormData()
formData.append('photo', file)

const response = await $fetch('/api/file-storage/profile-photo/quick-change/', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

2. **Получение URL фотографии:**
```javascript
const profile = await $fetch('/api/authentication/profile/')
const photoUrl = profile.data.profile_photo_url
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
- ✅ Эндпоинты для загрузки фотографий созданы
- ✅ Автоматическое создание бакетов
- ✅ UI для быстрой смены фотографии
- ✅ Обязательность для админов и провайдеров
- ✅ Поддержка всех ролей пользователей
- ✅ Современный и удобный интерфейс
- ✅ Полная валидация и обработка ошибок 