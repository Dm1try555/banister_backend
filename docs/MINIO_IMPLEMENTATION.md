# MinIO Интеграция Banister

## 📋 Обзор

MinIO используется для безопасного хранения файлов (фото профилей, документов) в системе Banister. Обеспечивает масштабируемое и надежное хранение данных.

## 🔧 Установка и настройка

### 1. Установка MinIO

```bash
# Скачивание MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio

# Создание директории для данных
sudo mkdir -p /opt/minio/data
sudo chown $USER:$USER /opt/minio/data
```

### 2. Запуск MinIO

```bash
# Запуск сервера
./minio server /opt/minio/data --console-address ":9001"

# Или в фоне
nohup ./minio server /opt/minio/data --console-address ":9001" > minio.log 2>&1 &
```

### 3. Настройка Django

```python
# settings.py
import os
from minio import Minio

# MinIO настройки
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'banister-files')
MINIO_USE_HTTPS = os.getenv('MINIO_USE_HTTPS', 'False').lower() == 'true'

# Инициализация MinIO клиента
MINIO_CLIENT = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_USE_HTTPS
)
```

### 4. Переменные окружения

```env
# .env файл
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=banister-files
MINIO_USE_HTTPS=False
```

## 📁 Структура хранения

### Buckets

```
banister-files/
├── profile-photos/          # Фото профилей
│   ├── user_1_photo.jpg
│   └── user_2_photo.png
├── documents/               # Документы
│   ├── user_1_doc.pdf
│   └── user_2_doc.docx
└── temp/                    # Временные файлы
    └── upload_12345.tmp
```

### Организация файлов

- **profile-photos/**: Фото профилей пользователей
- **documents/**: Загруженные документы
- **temp/**: Временные файлы для обработки

## 🔐 Безопасность

### Настройка доступа

```python
# utils/minio_utils.py
from minio import Minio
from django.conf import settings
import os

def get_minio_client():
    """Получение MinIO клиента"""
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_HTTPS
    )

def create_bucket_if_not_exists(bucket_name):
    """Создание bucket если не существует"""
    client = get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        # Настройка политики доступа
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        client.set_bucket_policy(bucket_name, json.dumps(policy))
```

### Валидация файлов

```python
# utils/file_validation.py
import os
from PIL import Image
from django.core.exceptions import ValidationError

def validate_image_file(file):
    """Валидация изображения"""
    # Проверка размера (максимум 5MB)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Файл слишком большой (максимум 5MB)")
    
    # Проверка формата
    allowed_formats = ['JPEG', 'PNG', 'GIF']
    try:
        with Image.open(file) as img:
            if img.format not in allowed_formats:
                raise ValidationError("Неподдерживаемый формат изображения")
    except Exception:
        raise ValidationError("Некорректный файл изображения")

def validate_document_file(file):
    """Валидация документа"""
    # Проверка размера (максимум 10MB)
    if file.size > 10 * 1024 * 1024:
        raise ValidationError("Файл слишком большой (максимум 10MB)")
    
    # Проверка расширения
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValidationError("Неподдерживаемый тип документа")
```

## 📝 API для работы с файлами

### Загрузка фото профиля

```python
# views.py
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from utils.minio_utils import upload_file_to_minio

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_profile_photo(request):
    """Загрузка фото профиля"""
    try:
        file = request.FILES.get('photo')
        if not file:
            return error_response('MISSING_FILE', 'Файл не предоставлен')
        
        # Валидация файла
        validate_image_file(file)
        
        # Генерация имени файла
        file_name = f"profile-photos/user_{request.user.id}_{int(time.time())}.{file.name.split('.')[-1]}"
        
        # Загрузка в MinIO
        file_url = upload_file_to_minio(
            file, 
            file_name, 
            'banister-files',
            content_type=file.content_type
        )
        
        # Обновление профиля пользователя
        request.user.profile_photo_url = file_url
        request.user.save()
        
        return success_response(
            data={'photo_url': file_url},
            message='Фото профиля загружено успешно'
        )
        
    except ValidationError as e:
        return error_response('VALIDATION_ERROR', str(e))
    except Exception as e:
        return error_response('UPLOAD_ERROR', 'Ошибка загрузки файла')
```

### Получение фото профиля

```python
@api_view(['GET'])
def get_profile_photo(request):
    """Получение фото профиля"""
    try:
        if not request.user.profile_photo_url:
            return error_response('NO_PHOTO', 'Фото профиля не найдено')
        
        return success_response(
            data={'photo_url': request.user.profile_photo_url},
            message='Фото профиля получено успешно'
        )
        
    except Exception as e:
        return error_response('RETRIEVE_ERROR', 'Ошибка получения фото')
```

### Удаление фото профиля

```python
@api_view(['DELETE'])
def delete_profile_photo(request):
    """Удаление фото профиля"""
    try:
        if not request.user.profile_photo_url:
            return error_response('NO_PHOTO', 'Фото профиля не найдено')
        
        # Удаление из MinIO
        file_name = request.user.profile_photo_url.split('/')[-1]
        delete_file_from_minio('banister-files', f"profile-photos/{file_name}")
        
        # Очистка URL в профиле
        request.user.profile_photo_url = None
        request.user.save()
        
        return success_response(message='Фото профиля удалено успешно')
        
    except Exception as e:
        return error_response('DELETE_ERROR', 'Ошибка удаления фото')
```

## 🔧 Утилиты для работы с MinIO

### Загрузка файла

```python
# utils/minio_utils.py
def upload_file_to_minio(file, file_name, bucket_name, content_type=None):
    """Загрузка файла в MinIO"""
    client = get_minio_client()
    
    # Создание bucket если не существует
    create_bucket_if_not_exists(bucket_name)
    
    # Загрузка файла
    client.put_object(
        bucket_name,
        file_name,
        file,
        file.size,
        content_type=content_type or 'application/octet-stream'
    )
    
    # Возврат URL файла
    return f"http://{settings.MINIO_ENDPOINT}/{bucket_name}/{file_name}"
```

### Удаление файла

```python
def delete_file_from_minio(bucket_name, file_name):
    """Удаление файла из MinIO"""
    client = get_minio_client()
    
    try:
        client.remove_object(bucket_name, file_name)
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления файла {file_name}: {e}")
        return False
```

### Получение URL файла

```python
def get_file_url(bucket_name, file_name, expires=3600):
    """Получение временного URL для файла"""
    client = get_minio_client()
    
    try:
        url = client.presigned_get_object(bucket_name, file_name, expires=expires)
        return url
    except Exception as e:
        logger.error(f"Ошибка получения URL для файла {file_name}: {e}")
        return None
```

## 📊 Мониторинг и логирование

### Логирование операций

```python
# utils/minio_utils.py
import logging

logger = logging.getLogger(__name__)

def log_minio_operation(operation, file_name, user_id, success=True):
    """Логирование операций с MinIO"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"MinIO {operation}: {file_name} by user {user_id} - {status}")
```

### Мониторинг использования

```python
def get_storage_stats():
    """Получение статистики использования хранилища"""
    client = get_minio_client()
    
    try:
        objects = client.list_objects('banister-files', recursive=True)
        total_size = 0
        file_count = 0
        
        for obj in objects:
            total_size += obj.size
            file_count += 1
        
        return {
            'total_size_mb': total_size / (1024 * 1024),
            'file_count': file_count,
            'bucket_name': 'banister-files'
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return None
```

## 🚨 Обработка ошибок

### Типичные ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `ConnectionError` | MinIO сервер недоступен | Проверить статус MinIO |
| `AccessDenied` | Неверные ключи доступа | Проверить ACCESS_KEY и SECRET_KEY |
| `NoSuchBucket` | Bucket не существует | Создать bucket автоматически |
| `InvalidObjectName` | Некорректное имя файла | Валидировать имя файла |

### Обработка исключений

```python
from minio.error import S3Error

def safe_minio_operation(operation_func, *args, **kwargs):
    """Безопасное выполнение операций с MinIO"""
    try:
        return operation_func(*args, **kwargs)
    except S3Error as e:
        logger.error(f"MinIO S3Error: {e}")
        raise ValidationError(f"Ошибка MinIO: {e}")
    except Exception as e:
        logger.error(f"MinIO Exception: {e}")
        raise ValidationError("Ошибка работы с файлами")
```

## 📝 Примеры использования

### Загрузка файла через API

```bash
curl -X POST /api/v1/files/profile-photo/upload/ \
  -H "Authorization: Bearer <access_token>" \
  -F "photo=@/path/to/photo.jpg"
```

### Получение файла

```bash
curl -X GET /api/v1/files/profile-photo/ \
  -H "Authorization: Bearer <access_token>"
```

### Удаление файла

```bash
curl -X DELETE /api/v1/files/profile-photo/delete/ \
  -H "Authorization: Bearer <access_token>"
```

## 🔒 Безопасность

### Рекомендации

1. **Используйте HTTPS** в продакшене
2. **Ограничьте размер файлов** на уровне приложения
3. **Валидируйте типы файлов** перед загрузкой
4. **Логируйте все операции** для аудита
5. **Регулярно очищайте временные файлы**

### Настройка CORS

```python
# Настройка CORS для MinIO
def setup_minio_cors():
    """Настройка CORS для MinIO"""
    client = get_minio_client()
    
    cors_rules = [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
            "AllowedHeaders": ["*"],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3000
        }
    ]
    
    client.set_bucket_cors('banister-files', cors_rules)
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте статус MinIO сервера
2. Убедитесь в правильности настроек в `.env`
3. Проверьте логи MinIO и Django
4. Убедитесь в доступности bucket и прав доступа 