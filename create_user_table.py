import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Создаем таблицу user если её нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Добавляем тестовых пользователей
test_users = [
    ('admin', 'admin123'),
    ('user1', 'password1'),
    ('test', 'test123')
]

for username, password in test_users:
    try:
        cursor.execute("INSERT OR IGNORE INTO user (username, password) VALUES (?, ?)", (username, password))
    except Exception as e:
        print(f"Ошибка при добавлении {username}: {e}")

conn.commit()

# Проверяем
cursor.execute("SELECT * FROM user")
users = cursor.fetchall()
print("Пользователи в базе:", users)

conn.close()