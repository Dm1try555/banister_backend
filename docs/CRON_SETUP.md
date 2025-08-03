# Настройка Cron Задач Banister

## 📋 Обзор

Система использует cron задачи для автоматического резервного копирования и очистки данных. Все задачи настроены для работы с Google Drive.

## 🔧 Установка и настройка

### 1. Установка зависимостей

```bash
pip install django-crontab google-cloud-storage
```

### 2. Настройка Google Cloud Storage

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Cloud Storage API
3. Создайте Service Account с правами "Storage Object Admin"
4. Создайте bucket `banister-backups` в Google Cloud Storage
5. Скачайте JSON ключ и поместите в `cron_tasks/banister-backup-1700feef3b7a.json`

### 3. Добавление в .env файл

```env
# Google Cloud Storage
GOOGLE_CLOUD_BUCKET_NAME=banister-backups
GOOGLE_CLOUD_CREDENTIALS_FILE=cron_tasks/banister-backup-1700feef3b7a.json
```

### 4. Настройка в settings.py

```python
INSTALLED_APPS = [
    # ... другие приложения
    'django_crontab',
]

# Настройки cron задач
CRONJOBS = [
    # Бэкап базы данных - ежедневно в 00:00
    ('0 0 * * *', 'django.core.management.call_command', ['backup_database']),
    
    # Бэкап MinIO - ежедневно в 00:00
    ('0 0 * * *', 'django.core.management.call_command', ['backup_minio']),
    
    # Очистка уведомлений - еженедельно в воскресенье в 00:00
    ('0 0 * * 0', 'django.core.management.call_command', ['cleanup_notifications']),
]
```

### 5. Установка cron задач

```bash
# Добавление задач в crontab
python manage.py crontab add

# Просмотр установленных задач
python manage.py crontab show

# Удаление всех задач
python manage.py crontab remove
```

## 📝 Доступные команды

### Бэкап базы данных
```bash
python manage.py backup_database
```
**Описание:** Создает резервную копию PostgreSQL базы данных и загружает в Google Drive
**Частота:** Ежедневно в 00:00
**Расположение в Google Drive:** `banister-backups/database_backups/`

### Бэкап MinIO
```bash
python manage.py backup_minio
```
**Описание:** Создает архив всех файлов из MinIO и загружает в Google Drive
**Частота:** Ежедневно в 00:00
**Расположение в Google Drive:** `banister-backups/minio_backups/`

### Очистка уведомлений
```bash
python manage.py cleanup_notifications
```
**Описание:** Удаляет уведомления старше 2 месяцев
**Частота:** Еженедельно в воскресенье в 00:00

## 📁 Структура бэкапов в Google Drive

```
banister-backups/
├── database_backups/
│   ├── database_backup_20241201_000000.sql
│   ├── database_backup_20241202_000000.sql
│   └── ...
└── minio_backups/
    ├── minio_backup_20241201_000000.tar.gz
    ├── minio_backup_20241202_000000.tar.gz
    └── ...
```

## 🔍 Мониторинг

### Проверка статуса cron
```bash
# Проверка активных задач
crontab -l

# Просмотр логов cron
tail -f /var/log/cron

# Проверка выполнения задач
grep CRON /var/log/syslog
```

### Логирование выполнения

Все команды логируют свое выполнение:

```python
# Пример лога
2025-08-03 00:00:01 - INFO - backup_database: Бэкап БД создан успешно
2025-08-03 00:00:05 - INFO - backup_minio: Бэкап MinIO создан успешно
2025-08-03 00:00:10 - INFO - cleanup_notifications: Удалено 45 уведомлений
```

## 🚨 Устранение неполадок

### Частые проблемы

1. **Cron задачи не выполняются**
   ```bash
   # Проверка службы cron
   sudo systemctl status cron
   
   # Перезапуск службы
   sudo systemctl restart cron
   ```

2. **Проблемы с Google Cloud**
   - Проверьте, что bucket `banister-backups` существует
   - Убедитесь, что ключ в `cron_tasks/banister-backup-1700feef3b7a.json` корректный
   - Проверьте права доступа Service Account

3. **Проблемы с правами доступа**
   ```bash
   # Проверка прав на файлы
   ls -la /path/to/project
   
   # Установка правильных прав
   chmod +x manage.py
   ```

### Отладка

```bash
# Проверка выполнения команды вручную
python manage.py backup_database --verbosity=2
python manage.py backup_minio --verbosity=2
python manage.py cleanup_notifications --dry-run
```

## 📊 Настройка для продакшена

### Продакшн конфигурация

```python
# settings.py
CRONJOBS = [
    # Бэкап базы данных - ежедневно в 00:00
    ('0 0 * * *', 'django.core.management.call_command', ['backup_database']),
    
    # Бэкап MinIO - ежедневно в 00:00
    ('0 0 * * *', 'django.core.management.call_command', ['backup_minio']),
    
    # Очистка уведомлений - еженедельно в воскресенье в 00:00
    ('0 0 * * 0', 'django.core.management.call_command', ['cleanup_notifications']),
]

# Настройки логирования для cron
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'cron_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/cron.log',
        },
    },
    'loggers': {
        'django_crontab': {
            'handlers': ['cron_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Мониторинг в продакшене

```bash
# Создание скрипта мониторинга
cat > /usr/local/bin/cron_monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/cron_monitor.log"
CRON_LOG="/var/log/cron.log"

# Проверка выполнения задач
if ! grep -q "$(date '+%b %d %H:')" "$CRON_LOG"; then
    echo "$(date): Cron tasks not running properly" >> "$LOG_FILE"
    # Отправка уведомления администратору
    echo "Cron tasks failed" | mail -s "Cron Alert" admin@example.com
fi
EOF

chmod +x /usr/local/bin/cron_monitor.sh

# Добавление в crontab для мониторинга
echo "*/5 * * * * /usr/local/bin/cron_monitor.sh" | crontab -
```

## 🔒 Безопасность

### Рекомендации

1. **Ограничение прав доступа**
   ```bash
   # Создание отдельного пользователя для cron
   sudo useradd -r -s /bin/false cronuser
   
   # Установка прав
   sudo chown -R cronuser:cronuser /path/to/project
   ```

2. **Логирование всех операций**
   ```python
   # Добавление в команды
   logger.info(f'Task started: {command_name}')
   logger.info(f'Task completed: {command_name}')
   ```

3. **Проверка целостности**
   ```bash
   # Проверка выполнения задач
   python manage.py check_cron_health
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в `logs/cron.log`
2. Убедитесь, что служба cron запущена
3. Проверьте права доступа к файлам
4. Запустите команды вручную для отладки 