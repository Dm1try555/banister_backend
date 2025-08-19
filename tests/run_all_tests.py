#!/usr/bin/env python3
"""
🧪 Запуск всех тестов Banister Backend API

Этот файл запускает все тесты и выводит сводный отчет.
"""

import subprocess
import sys
import time

def run_test(test_file, test_name):
    """Запустить отдельный тест и вернуть результат"""
    print(f"\n{'='*60}")
    print(f"🧪 ЗАПУСК: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            'python', f'/app/tests/{test_file}'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
            return True, result.stdout
        else:
            print(f"❌ ОШИБКА в {test_file}:")
            print(result.stderr)
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"❌ ТАЙМАУТ: {test_file} превысил 30 секунд")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ при запуске {test_file}: {e}")
        return False, str(e)

def main():
    """Основная функция запуска всех тестов"""
    print("🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ BANISTER BACKEND API")
    print("="*70)
    
    tests = [
        ("test_api.py", "Базовое API тестирование"),
        ("test_admin.py", "Админские функции"),
        ("test_permissions.py", "Система разрешений"),
        ("test_drf_classes.py", "DRF классы и архитектура"),
        ("test_pagination_minio.py", "Пагинация и MinIO"),
        ("test_cron_smtp.py", "Крон задачи и SMTP")
    ]
    
    results = []
    start_time = time.time()
    
    for test_file, test_name in tests:
        success, output = run_test(test_file, test_name)
        results.append((test_name, success, len(output.split('\n')) if success else 0))
        
        if not success:
            print(f"\n⚠️ ТЕСТ {test_name} ПРОВАЛЕН!")
        
        time.sleep(1)  # Небольшая пауза между тестами
    
    # Сводный отчет
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n{'='*70}")
    print("📊 СВОДНЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    print(f"{'='*70}")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, lines in results:
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{status:12} | {test_name:30} | {lines:3} строк вывода")
    
    print(f"\n🎯 ИТОГО:")
    print(f"   Пройдено: {passed}/{total}")
    print(f"   Время выполнения: {total_time:.1f} секунд")
    
    if passed == total:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"✅ Система готова к работе!")
        return 0
    else:
        print(f"\n⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        print(f"❌ Требуется исправление ошибок")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)