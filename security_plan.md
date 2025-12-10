# План обеспечения безопасности веб-приложения

## 1. Цели и требования безопасности

### 1.1 Цели
- Защита от OWASP Top 10 уязвимостей
- Обеспечение конфиденциальности пользовательских данных
- Предотвращение несанкционированного доступа
- Соответствие принципам DevSecOps

### 1.2 Требования
- **Аутентификация**: Защита от SQL-инъекций, brute-force атак
- **Авторизация**: Проверка прав доступа (IDOR защита)
- **Ввод данных**: Валидация и санитизация всех входных данных
- **Сессии**: Безопасное хранение, ограниченное время жизни
- **Транспорт**: Использование HTTPS (в production)

## 2. Оценка угроз (на основе тестов ПР №4)

### 2.1 Выявленные уязвимости (до исправления)
1. **SQL-инъекции** в эндпоинтах аутентификации
   - Обход аутентификации: `' OR '1'='1' --`
   - Извлечение данных: `' UNION SELECT ... --`
   - Time-based атаки: `' OR (SELECT CASE ...)`

2. **IDOR (Insecure Direct Object References)**
   - Доступ к чужим заметкам через прямой URL

### 2.2 Угрозы модели STRIDE
- **Spoofing** (подмена): SQL-инъекции, CSRF
- **Tampering** (изменение): Изменение чужих заметок
- **Repudiation** (отказ): Отсутствие логов
- **Information Disclosure** (раскрытие): SQL-инъекции, IDOR
- **Denial of Service** (отказ): Отсутствие rate limiting
- **Elevation of Privilege** (повышение): Обход аутентификации

## 3. Реализованные меры защиты

### 3.1 Защита на уровне приложения (ПР №4)
- ✅ **Параметризованные запросы** через SQLAlchemy ORM
- ✅ **Валидация входных данных** с помощью Flask-WTF
- ✅ **Защита от CSRF** токенами
- ✅ **IDOR защита** через сессии пользователя
- ✅ **HTTP security headers**:
  - Content-Security-Policy
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - Strict-Transport-Security

### 3.2 Защита на уровне инфраструктуры (ПР №5)
- ✅ **PostgreSQL SSL шифрование**
- ✅ **Ограничение доступа** через pg_hba.conf
- ✅ **Брандмауэр** Windows Firewall
- ✅ **Пользователь с минимальными правами** (app_user)

### 3.3 Конфигурация безопасности
```python
# Настройки Flask
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # True в production
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 1800  # 30 минут

# Отключение debug mode в production
if __name__ == '__main__':
    app.run(debug=False)  # Важно для production!