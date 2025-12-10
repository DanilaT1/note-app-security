from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from models import db, Note, User
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройки безопасности для кук
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, # Защита от краж сессии через XSS
    SESSION_COOKIE_SECURE=False,  # True в production с HTTPS
    SESSION_COOKIE_SAMESITE='Lax',  # Защита от CSRF
    PERMANENT_SESSION_LIFETIME=1800  # 30 минут
)

# Middleware для HTTP-заголовков безопасности
@app.after_request
def set_security_headers(response):
    """Устанавливает заголовки безопасности"""
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;"
    
    # Защита от clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Защита от MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # HSTS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# Инициализация расширений
db.init_app(app)
csrf = CSRFProtect(app)

# Формы с CSRF защитой
class NoteForm(FlaskForm):
    """Форма для добавления новой заметки"""
    title = StringField('Заголовок', validators=[
        DataRequired(message='Заголовок обязателен'),
        Length(max=100, message='Заголовок не должен превышать 100 символов')
    ])
    content = TextAreaField('Содержание', validators=[
        DataRequired(message='Содержание обязательно')
    ])
    submit = SubmitField('Добавить заметку')

class EditNoteForm(FlaskForm):
    """Форма для редактирования заметки"""
    title = StringField('Заголовок', validators=[
        DataRequired(message='Заголовок обязателен'),
        Length(max=100, message='Заголовок не должен превышать 100 символов')
    ])
    content = TextAreaField('Содержание', validators=[
        DataRequired(message='Содержание обязательно')
    ])
    submit = SubmitField('Сохранить изменения')

# Формы для аутентификации
class LoginForm(FlaskForm):
    """Форма для входа"""
    username = StringField('Логин', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    """Форма для регистрации"""
    username = StringField('Логин', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

# ========== УЯЗВИМАЯ АУТЕНТИФИКАЦИЯ (SQL-ИНЪЕКЦИИ) ==========

@app.route('/register-vulnerable', methods=['GET', 'POST'])
def register_vulnerable():
    """УЯЗВИМАЯ регистрация - SQL инъекции возможны"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # УЯЗВИМЫЙ запрос - конкатенация строк
        db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # УЯЗВИМЫЙ КОД - SQL ИНЪЕКЦИИ ВОЗМОЖНЫ
            cursor.execute(f"INSERT INTO user (username, password) VALUES ('{username}', '{password}')")
            conn.commit()
            flash('Регистрация успешна!', 'success')
            return redirect(url_for('login_vulnerable'))
        except sqlite3.IntegrityError:
            flash('Пользователь уже существует!', 'error')
        except Exception as e:
            flash(f'Ошибка регистрации: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('register.html', form=form, vulnerable=True)

@app.route('/sqlmap-test', methods=['GET', 'POST'])
@csrf.exempt
def sqlmap_test():
    """Специальный endpoint для SQLMap - возвращает четкие ответы"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # УЯЗВИМЫЙ КОД
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ОЧЕНЬ УЯЗВИМЫЙ ЗАПРОС
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # ЧЕТКИЙ ОТВЕТ для SQLMap
                return f"SUCCESS: User ID={user[0]}, Username={user[1]}, Password={user[2]}"
            else:
                return "FAIL: Invalid credentials"
                
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    # Простая форма без лишних элементов
    return '''
    <h2>SQLMap Test Endpoint</h2>
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Test">
    </form>
    '''

@app.route('/login-vulnerable', methods=['GET', 'POST'])
#@csrf.exempt  # ОТКЛЮЧАЕМ CSRF ДЛЯ ТЕСТИРОВАНИЯ
def login_vulnerable():
    """УЯЗВИМЫЙ вход - SQL инъекции возможны"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # УЯЗВИМЫЙ запрос - конкатенация строк
        db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # УЯЗВИМЫЙ КОД - SQL ИНЪЕКЦИИ ВОЗМОЖНЫ
            query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash(f'Успешный вход как {user[1]}! ID: {user[0]}', 'success')
                conn.close()
                return redirect(url_for('index'))
            else:
                flash('Неверный логин или пароль!', 'error')
        except Exception as e:
            flash(f'Ошибка входа: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('login.html', form=form, vulnerable=True)

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('index'))

# ========== БЕЗОПАСНАЯ АУТЕНТИФИКАЦИЯ ==========

@app.route('/register-secure', methods=['GET', 'POST'])
def register_secure():
    """БЕЗОПАСНАЯ регистрация - SQLAlchemy"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        try:
            # БЕЗОПАСНЫЙ КОД - SQLAlchemy ORM
            if User.query.filter_by(username=username).first():
                flash('Пользователь уже существует!', 'error')
            else:
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                flash('Регистрация успешна!', 'success')
                return redirect(url_for('login_secure'))
        except Exception as e:
            flash(f'Ошибка регистрации: {str(e)}', 'error')
    
    return render_template('register.html', form=form, vulnerable=False)

@app.route('/login-secure', methods=['GET', 'POST'])
def login_secure():
    """БЕЗОПАСНЫЙ вход - SQLAlchemy"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        try:
            # БЕЗОПАСНЫЙ КОД - SQLAlchemy ORM
            user = User.query.filter_by(username=username, password=password).first()
            
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f'Успешный вход как {user.username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный логин или пароль!', 'error')
        except Exception as e:
            flash(f'Ошибка входа: {str(e)}', 'error')
    
    return render_template('login.html', form=form, vulnerable=False)

# ========== СУЩЕСТВУЮЩИЙ ФУНКЦИОНАЛ ЗАМЕТОК ==========

# Инициализация сессии для хранения ID заметок (защита от IDOR)
@app.before_request
def init_session():
    """Инициализация сессии для хранения ID созданных заметок"""
    if 'note_ids' not in session:
        session['note_ids'] = []

# Создание таблиц в базе данных
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Главная страница со списком всех заметок"""
    notes = Note.query.all()  # Безопасный запрос через ORM
    form = NoteForm()
    username = session.get('username', None)
    return render_template('index.html', notes=notes, form=form, username=username)

@app.route('/add', methods=['POST'])
def add_note():
    """Добавление новой заметки с валидацией и санитизацией"""
    form = NoteForm()
    if form.validate_on_submit():
        # Санитизация ввода - удаление лишних пробелов
        title = form.title.data.strip()
        content = form.content.data.strip()
        
        # Проверка на пустые значения
        if title and content:
            new_note = Note(title=title, content=content)
            db.session.add(new_note)
            db.session.commit()
            
            # Добавляем ID новой заметки в сессию пользователя (защита от IDOR)
            if 'note_ids' not in session:
                session['note_ids'] = []
            session['note_ids'].append(new_note.id)
            session.modified = True  # Важно: помечаем сессию как измененную
            
            flash('Заметка успешно добавлена!', 'success')
        else:
            flash('Заголовок и содержание не могут быть пустыми', 'error')
    else:
        # Если форма не прошла валидацию
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('index'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    """
    Редактирование заметки с проверкой прав доступа через сессии
    Защита от IDOR (Insecure Direct Object References)
    """
    note = Note.query.get_or_404(note_id)
    
    # Проверка прав доступа через сессию (защита от IDOR)
    if note_id not in session.get('note_ids', []):
        flash('У вас нет прав для редактирования этой заметки! Ошибка IDOR защиты.', 'error')
        return redirect(url_for('index'))
    
    form = EditNoteForm(obj=note)
    
    if form.validate_on_submit():
        # Санитизация и обновление данных
        note.title = form.title.data.strip()
        note.content = form.content.data.strip()
        
        if note.title and note.content:
            db.session.commit()
            flash('Заметка успешно обновлена!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Заголовок и содержание не могут быть пустыми', 'error')
    
    return render_template('edit.html', form=form, note=note)

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    """Удаление заметки с проверкой прав доступа через сессии"""
    note = Note.query.get_or_404(note_id)
    
    # Проверка прав доступа через сессию (защита от IDOR)
    if note_id not in session.get('note_ids', []):
        flash('У вас нет прав для удаления этой заметки! Ошибка IDOR защиты.', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(note)
    db.session.commit()
    
    # Удаляем ID из сессии
    if note_id in session.get('note_ids', []):
        session['note_ids'].remove(note_id)
        session.modified = True
    
    flash('Заметка успешно удалена!', 'success')
    return redirect(url_for('index'))

@app.route('/debug')
def debug():
    """
    Отладочная страница для проверки работы защиты от IDOR
    Показывает все заметки и права доступа текущего пользователя
    """
    notes = Note.query.all()
    user_notes = session.get('note_ids', [])
    
    result = "<h2>Отладочная информация - Проверка IDOR защиты</h2>"
    result += f"<p><strong>Ваши права доступа (note_ids в сессии):</strong> {user_notes}</p>"
    result += "<h3>Все заметки в базе данных:</h3>"
    result += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
    result += "<tr><th>ID</th><th>Заголовок</th><th>Дата создания</th><th>Доступ</th><th>Действия</th></tr>"
    
    for note in notes:
        has_access = note.id in user_notes
        access_status = "✅ ЕСТЬ" if has_access else "❌ НЕТ"
        action_links = f"<a href='/edit/{note.id}'>Редакт.</a> <a href='/delete/{note.id}' onclick='return confirm(\"Удалить?\")'>Удалить</a>" if has_access else "Нет прав"
        
        result += f"<tr><td>{note.id}</td><td>{note.title}</td><td>{note.created_at.strftime('%d.%m.%Y %H:%M')}</td><td>{access_status}</td><td>{action_links}</td></tr>"
    
    result += "</table>"
    result += "<br><a href='/'>Вернуться на главную</a>"
    
    return result

@app.route('/clear-session')
def clear_session():
    """Очистка сессии (для тестирования)"""
    session.clear()
    flash('Сессия очищена! Все права доступа сброшены.', 'info')
    return redirect(url_for('index'))

@app.route('/test-headers')
def test_headers():
    """Страница для проверки заголовков"""
    return "Проверка заголовков безопасности"

# БЕЗОПАСНЫЙ ЗАПУСК
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')  
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    app.run(
        debug=debug_mode,
        host=host,
        port=port
    )