#!/usr/bin/env python3
import sys
sys.path.append('/app')
from core.backup.local_service import local_backup_service
import os

def check_local_backup_files():
    print("💾 ПРОВЕРКА ЛОКАЛЬНЫХ ФАЙЛОВ БЕКАПОВ")
    print("=" * 50)
    
    try:
        backup_dir = local_backup_service.backup_dir
        print(f"📍 Папка бекапов: {backup_dir}")
        
        if not os.path.exists(backup_dir):
            print("❌ Папка бекапов не найдена")
            print("💡 Запустите тест бекапов для создания файлов")
            return
        
        # Получаем список всех бекапов
        backups = local_backup_service.list_backups()
        
        total_files = len(backups['database_backups']) + len(backups['minio_backups'])
        print(f"📊 Всего файлов бекапов: {total_files}")
        
        if total_files > 0:
            print(f"\n📁 ФАЙЛЫ БЕКАПОВ:")
            print("-" * 80)
            
            # Показываем бекапы БД
            if backups['database_backups']:
                print("💾 БЕКАПЫ БАЗЫ ДАННЫХ:")
                for backup in backups['database_backups']:
                    size_mb = round(backup['size'] / 1024 / 1024, 2)
                    created = backup['created'][:19].replace('T', ' ')
                    print(f"   📄 {backup['name']}")
                    print(f"      Создан: {created}")
                    print(f"      Размер: {size_mb} MB")
                    print(f"      Путь: {backup['path']}")
                    print()
            
            # Показываем бекапы MinIO
            if backups['minio_backups']:
                print("📦 БЕКАПЫ MINIO:")
                for backup in backups['minio_backups']:
                    size_mb = round(backup['size'] / 1024 / 1024, 2)
                    created = backup['created'][:19].replace('T', ' ')
                    print(f"   📄 {backup['name']}")
                    print(f"      Создан: {created}")
                    print(f"      Размер: {size_mb} MB")
                    print(f"      Путь: {backup['path']}")
                    print()
            
            print("📂 ДОСТУП К ФАЙЛАМ:")
            print("=" * 50)
            print(f"🐳 В Docker: docker-compose exec web ls -la /app/backups")
            print(f"💻 На хосте: найдите Docker volume 'backup_data'")
                
        else:
            print("❌ Файлы бекапов не найдены")
            print("💡 Запустите тест бекапов для создания файлов")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке бекапов: {e}")

if __name__ == "__main__":
    check_local_backup_files()