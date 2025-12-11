# bad_code.py
# Демонстрационный файл с уязвимостями для тестирования CI/CD

# Уязвимость 1: debug=True в production
debug = True  # ❌ ЭТО ПЛОХО! Pipeline должен блокировать    это

# Уязвимость 2: SQL инъекция
def vulnerable_login(username, password):
    """Уязвимая функция с SQL инъекцией"""
    import sqlite3
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # ❌ ОПАСНО: конкатенация строк!
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    
    return cursor.fetchone()

# Уязвимость 3: Хардкод секретов
SECRET_KEY = "my_super_secret_key_12345"  # ❌ Не храните секреты в коде!
DATABASE_PASSWORD = "admin123"  # ❌ Это плохая практика

# Уязвимость 4: Небезопасная десериализация
import pickle

def load_data(data):
    """Небезопасная загрузка данных"""
    # ❌ ОПАСНО: может выполнить произвольный код
    return pickle.loads(data)

print("⚠️ Этот код содержит преднамеренные уязвимости для тестирования CI/CD!")
