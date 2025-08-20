#!/usr/bin/env python3
import sys
sys.path.append('/app')
from core.backup.local_service import local_backup_service
from datetime import datetime
import os

def test_database_backup():
    print("💾 ТЕСТ БЕКАПА БАЗЫ ДАННЫХ")
    
    try:
        print("Создание бекапа БД...")
        backup_file = local_backup_service.backup_database()
        
        if os.path.exists(backup_file):
            size = os.path.getsize(backup_file)
            print(f"✅ Database backup создан: {os.path.basename(backup_file)}")
            print(f"📁 Размер файла: {size} bytes")
        else:
            print("❌ Файл бекапа не найден")
        
    except Exception as e:
        print(f"❌ Ошибка database backup: {e}")

def test_minio_backup():
    print("\n📦 ТЕСТ БЕКАПА MINIO")
    
    try:
        print("Создание бекапа MinIO...")
        backup_file = local_backup_service.backup_minio()
        
        if os.path.exists(backup_file):
            size = os.path.getsize(backup_file)
            print(f"✅ MinIO backup создан: {os.path.basename(backup_file)}")
            print(f"📁 Размер файла: {size} bytes")
        else:
            print("❌ Файл бекапа не найден")
        
    except Exception as e:
        print(f"❌ Ошибка MinIO backup: {e}")

def test_backup_directory():
    print("\n📁 ТЕСТ ПАПКИ БЕКАПОВ")
    
    try:
        backup_dir = local_backup_service.backup_dir
        print(f"📍 Папка бекапов: {backup_dir}")
        
        if os.path.exists(backup_dir):
            print(f"✅ Папка существует")
            files = os.listdir(backup_dir)
            print(f"📊 Файлов в папке: {len(files)}")
        else:
            print("❌ Папка не найдена")
        
    except Exception as e:
        print(f"❌ Ошибка проверки папки: {e}")

if __name__ == "__main__":
    test_backup_directory()
    test_database_backup()
    test_minio_backup()
    
    print("\n📋 РЕЗЮМЕ:")
    print("Все бекапы сохраняются локально в /app/backups")
    print("Автоматическая ротация: сохраняются последние 7 файлов")