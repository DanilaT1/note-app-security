# Исправленная версия - убраны все уязвимости
debug = False  # ✅ Исправлено

def safe_login(username, password):
    """Безопасная функция"""
    import sqlite3
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # ✅ Безопасно: параметризованный запрос
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    
    return cursor.fetchone()