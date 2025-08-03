# API Услуг Banister

## 📋 Обзор

API услуг предоставляет полный CRUD функционал для управления услугами на платформе Banister. Только поставщики (providers) могут создавать и управлять услугами.

## 🔐 Аутентификация

Все эндпоинты требуют JWT аутентификации:
```
Authorization: Bearer <access_token>
```

## 📝 CRUD операции

### Получение списка услуг

```http
GET /api/v1/services/
```

**Параметры запроса:**
- `search` - Поиск по названию или описанию
- `ordering` - Сортировка (price, created_at, -price, -created_at)
- `page` - Номер страницы для пагинации

**Ответ:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "title": "Web Development",
        "description": "Professional web development services",
        "price": 100.00,
        "provider": {
          "id": 2,
          "email": "provider@example.com",
          "profile": {
            "first_name": "Jane",
            "last_name": "Smith"
          }
        },
        "created_at": "2025-08-03T18:40:50.547748+00:00",
        "updated_at": "2025-08-03T18:40:50.547748+00:00"
      }
    ],
    "count": 1,
    "next": null,
    "previous": null
  }
}
```

### Создание услуги (только для Providers)

```http
POST /api/v1/services/
```

**Тело запроса:**
```json
{
  "title": "Web Development",
  "description": "Professional web development services",
  "price": 100.00
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Service created successfully",
  "data": {
    "id": 1,
    "title": "Web Development",
    "description": "Professional web development services",
    "price": 100.00,
    "provider": {
      "id": 2,
      "email": "provider@example.com"
    },
    "created_at": "2025-08-03T18:40:50.547748+00:00",
    "updated_at": "2025-08-03T18:40:50.547748+00:00"
  }
}
```

### Получение услуги по ID

```http
GET /api/v1/services/{id}/
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Web Development",
    "description": "Professional web development services",
    "price": 100.00,
    "provider": {
      "id": 2,
      "email": "provider@example.com",
      "profile": {
        "first_name": "Jane",
        "last_name": "Smith"
      }
    },
    "created_at": "2025-08-03T18:40:50.547748+00:00",
    "updated_at": "2025-08-03T18:40:50.547748+00:00"
  }
}
```

### Обновление услуги (только владелец)

```http
PUT /api/v1/services/{id}/
```

**Тело запроса:**
```json
{
  "title": "Advanced Web Development",
  "description": "Updated description",
  "price": 150.00
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Service updated successfully",
  "data": {
    "id": 1,
    "title": "Advanced Web Development",
    "description": "Updated description",
    "price": 150.00,
    "provider": {
      "id": 2,
      "email": "provider@example.com"
    },
    "created_at": "2025-08-03T18:40:50.547748+00:00",
    "updated_at": "2025-08-03T18:40:50.547748+00:00"
  }
}
```

### Удаление услуги (только владелец)

```http
DELETE /api/v1/services/{id}/
```

**Ответ:**
```json
{
  "success": true,
  "message": "Service deleted successfully"
}
```

## 🌐 Публичные эндпоинты

### Публичный список услуг (без аутентификации)

```http
GET /api/v1/public/services/
```

**Параметры запроса:**
- `search` - Поиск по названию или описанию
- `ordering` - Сортировка (price, created_at, -price, -created_at)
- `page` - Номер страницы для пагинации

**Ответ:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "title": "Web Development",
        "description": "Professional web development services",
        "price": 100.00,
        "provider": {
          "id": 2,
          "email": "provider@example.com",
          "profile": {
            "first_name": "Jane",
            "last_name": "Smith"
          }
        },
        "created_at": "2025-08-03T18:40:50.547748+00:00"
      }
    ],
    "count": 1,
    "next": null,
    "previous": null
  }
}
```

## 🚨 Обработка ошибок

### Стандартный формат ошибок

```json
{
  "success": false,
  "error_number": "ERROR_CODE",
  "error_message": "Описание ошибки",
  "timestamp": "2025-08-03T18:40:50.547748+00:00"
}
```

### Коды ошибок

| Код | HTTP Статус | Описание |
|-----|-------------|----------|
| `ACCESS_DENIED` | 403 | Отказано в доступе (не provider) |
| `SERVICE_NOT_FOUND` | 404 | Услуга не найдена |
| `NOT_OWNER` | 403 | Не владелец услуги |
| `VALIDATION_ERROR` | 400 | Ошибка валидации данных |
| `MISSING_FIELD` | 400 | Отсутствует обязательное поле |
| `INVALID_PRICE` | 400 | Неверная цена |
| `SERVER_ERROR` | 500 | Ошибка сервера |

## 📊 Валидация данных

### Обязательные поля
- `title` - Название услуги (максимум 200 символов)
- `description` - Описание услуги (максимум 1000 символов)
- `price` - Цена услуги (положительное число)

### Ограничения
- Только пользователи с ролью `provider` могут создавать услуги
- Владелец услуги может редактировать и удалять только свои услуги
- Цена должна быть положительным числом
- Название и описание не могут быть пустыми

## 🔒 Безопасность

### Проверки доступа
- Создание услуг: только `provider` роль
- Редактирование/удаление: только владелец услуги
- Просмотр: все авторизованные пользователи
- Публичный доступ: без аутентификации

### Валидация
- Проверка роли пользователя
- Валидация входных данных
- Проверка владения услугой
- Санитизация данных

## 📝 Примеры использования

### Создание услуги
```bash
curl -X POST /api/v1/services/ \
  -H "Authorization: Bearer <provider_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Web Development",
    "description": "Professional web development services",
    "price": 100.00
  }'
```

### Получение списка услуг
```bash
curl -X GET "/api/v1/services/?search=web&ordering=price" \
  -H "Authorization: Bearer <access_token>"
```

### Обновление услуги
```bash
curl -X PUT /api/v1/services/1/ \
  -H "Authorization: Bearer <provider_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Web Development",
    "description": "Updated description",
    "price": 150.00
  }'
```

### Удаление услуги
```bash
curl -X DELETE /api/v1/services/1/ \
  -H "Authorization: Bearer <provider_token>"
```

### Публичный доступ
```bash
curl -X GET "/api/v1/public/services/?ordering=-created_at"
```

## 📊 Статус разработки

### ✅ Реализовано
- [x] CRUD операции для услуг
- [x] Публичный доступ к услугам
- [x] Поиск и фильтрация
- [x] Пагинация
- [x] Валидация данных
- [x] Контроль доступа
- [x] Обработка ошибок

### 🔄 В разработке
- [ ] Категории услуг
- [ ] Теги и метки
- [ ] Рейтинги и отзывы
- [ ] Изображения услуг
- [ ] Расписание доступности

### 📋 Планируется
- [ ] Продвижение услуг
- [ ] Статистика просмотров
- [ ] Рекомендации
- [ ] Уведомления о новых услугах 