# bad_code.py - Пример кода, который будет заблокирован Bandit

from flask import Flask

app = Flask(__name__)

# ❌ КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: debug=True в production коде
app.config['DEBUG'] = True  # Bandit: B201

# ❌ УЯЗВИМОСТЬ: SQL инъекция
def vulnerable_query(user_input):
    import sqlite3
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # ⚠️ Bandit: B608 - возможна SQL инъекция
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)  # Опасный вызов!
    
    return cursor.fetchall()

# ❌ УЯЗВИМОСТЬ: Хардкод секрета
SECRET_KEY = "my_super_secret_key_12345"  # Bandit: B105

# ❌ УЯЗВИМОСТЬ: Потенциальная команда инъекция
import os
def unsafe_command(filename):
    # Bandit: B602, B607
    os.system(f"rm {filename}")  # Опасно!

if __name__ == '__main__':
    app.run(debug=True)  # ❌ Еще один debug=True
    print("🚫 Этот код полон уязвимостей!")