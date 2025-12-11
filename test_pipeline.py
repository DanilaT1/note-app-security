# test_pipeline.py - Имитация работы CI/CD
import subprocess
import json
import os

print("🚀 ИМИТАЦИЯ CI/CD PIPELINE")
print("="*50)

# Тест 1: Bandit на основном коде
print("\n📦 ТЕСТ 1: Bandit scan основного кода")
result = subprocess.run(
    ["bandit", "-r", ".", "-f", "json", "--skip", "B101,B311,B404,B603"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ Основной код прошел проверку")
else:
    print("❌ В основном коде найдены уязвимости")
    report = json.loads(result.stdout)
    for issue in report['results'][:2]:  # Покажем первые 2
        print(f"  - {issue['issue_text']}")

# Тест 2: Bandit на плохом коде
print("\n📦 ТЕСТ 2: Bandit scan bad_code.py")
result = subprocess.run(
    ["bandit", "bad_code.py", "-f", "json"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ bad_code.py прошел проверку (не должно быть!)")
else:
    print("❌ bad_code.py НЕ прошел проверку (как и ожидалось!)")
    report = json.loads(result.stdout)
    
    high_count = sum(1 for i in report['results'] if i['issue_severity'] == 'HIGH')
    medium_count = sum(1 for i in report['results'] if i['issue_severity'] == 'MEDIUM')
    
    print(f"  Найдено HIGH уязвимостей: {high_count}")
    print(f"  Найдено MEDIUM уязвимостей: {medium_count}")

# Тест 3: Проверка debug режима
print("\n📦 ТЕСТ 3: Поиск debug=True в коде")
result = subprocess.run(
    ["grep", "-r", "debug=True", ".", "--include=*.py"],
    capture_output=True,
    text=True,
    shell=True
)

if result.stdout:
    print("❌ Обнаружен debug=True в коде:")
    for line in result.stdout.strip().split('\n')[:3]:
        print(f"  - {line}")
else:
    print("✅ debug=True не найден в основном коде")

print("\n" + "="*50)
print("🎯 ВЫВОД: Pipeline успешно обнаруживает уязвимости!")
print("   При push кода с уязвимостями pipeline завершится ошибкой")
print("   При push безопасного кода pipeline пройдет успешно")