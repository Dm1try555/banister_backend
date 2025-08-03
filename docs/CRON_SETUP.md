# Крон задачи для Banister Backend

## ✅ Что готово

Все три крон задачи реализованы и настроены:

1. **Бэкап базы данных** - ежедневно в 00:00
2. **Бэкап MinIO** - ежедневно в 00:00  
3. **Очистка уведомлений** - еженедельно в воскресенье в 00:00

## 📁 Структура файлов

```
cron_tasks/
├── __init__.py
├── apps.py
├── cron.py                    # Конфигурация крон задач
└── management/
    └── commands/
        ├── __init__.py
        ├── backup_database.py    # Бэкап БД
        ├── backup_minio.py       # Бэкап MinIO
        └── cleanup_notifications.py  # Очистка уведомлений
```

## 🔧 Что нужно сделать

### 1. Установить зависимости
```bash
pip install django-crontab google-cloud-storage
```

### 2. Настроить Google Cloud Storage
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Cloud Storage API
3. Создайте Service Account с правами "Storage Object Admin"
4. Создайте bucket `banister-backups` в Google Cloud Storage
5. Скачайте JSON ключ и поместите в `cron_tasks/banister-backup-1700feef3b7a.json` (файл не будет в репозитории)

### 3. Добавить в .env файл
```env
# Google Cloud Storage
GOOGLE_CLOUD_BUCKET_NAME=banister-backups


### 4. Установить крон задачи
```bash
python manage.py crontab add
```

## 🧪 Тестирование

### Проверка команд
```bash
# Бэкап базы данных
python manage.py backup_database

# Бэкап MinIO
python manage.py backup_minio

# Очистка уведомлений (предварительный просмотр)
python manage.py cleanup_notifications --dry-run

# Очистка уведомлений (реальное удаление)
python manage.py cleanup_notifications
```

### Проверка установленных задач
```bash
python manage.py crontab show
```

## 📅 Расписание выполнения

| Задача | Расписание | Cron выражение |
|--------|------------|----------------|
| Бэкап БД | Ежедневно в 00:00 | `0 0 * * *` |
| Бэкап MinIO | Ежедневно в 00:00 | `0 0 * * *` |
| Очистка уведомлений | Еженедельно в воскресенье в 00:00 | `0 0 * * 0` |

## 📁 Структура бэкапов в Google Drive

```
banister-backups/
├── database_backups/
│   ├── database_backup_20241201_000000.sql
│   └── database_backup_20241202_000000.sql
└── minio_backups/
    ├── minio_backup_20241201_000000.tar.gz
    └── minio_backup_20241202_000000.tar.gz
```

## 🔍 Мониторинг

### Просмотр логов
```bash
# Django логи
tail -f debug.log

# Системные логи cron (Linux)
tail -f /var/log/cron
```

### Проверка статуса
```bash
# Просмотр активных крон задач
crontab -l
```

## 🛠️ Управление крон задачами

```bash
# Установить крон задачи
python manage.py crontab add

# Показать установленные задачи
python manage.py crontab show

# Удалить крон задачи
python manage.py crontab remove
```

## ⚠️ Устранение неполадок

### Проблема: Команды не найдены
```bash
python manage.py check
```

### Проблема: Ошибки Google Cloud
- Проверьте, что bucket `banister-backups` существует
- Убедитесь, что ключ в `cron_tasks/banister-backup-1700feef3b7a.json` корректный (файл не в репозитории)


## ✅ Статус готовности

- ✅ Приложение `cron_tasks` добавлено в `INSTALLED_APPS`
- ✅ Команды созданы и готовы к использованию
- ✅ Крон задачи настроены в `settings.py`
- ✅ Ключ Google Cloud будет добавлен локально (не в репозитории)
- ✅ Зависимости добавлены в `requirements.txt`

**Система готова к использованию!** 