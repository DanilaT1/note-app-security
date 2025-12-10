# custom_server.py
import os
from app import app
from models import db
from werkzeug.serving import WSGIRequestHandler

class CustomWSGIRequestHandler(WSGIRequestHandler):
    """Кастомный обработчик запросов для скрытия Server header"""
    def make_environ(self):
        environ = super().make_environ()
        return environ
    
    def send_response(self, *args, **kwargs):
        super().send_response(*args, **kwargs)
        # Переопределяем Server header
        self.send_header('Server', 'CustomProtectedServer/1.0')
    
    def version_string(self):
        """Возвращает кастомную строку версии сервера"""
        return 'CustomProtectedServer/1.0'

def run_production():
    """Запуск production сервера с кастомным server_name"""
    with app.app_context():
        db.create_all()
    
    from werkzeug.serving import run_simple
    
    print("Custom Production Server запущен")
    print("http://127.0.0.1:5000")
    print("Server header: CustomProtectedServer/1.0")
    print("Security headers активны")
    
    # Запуск с кастомным обработчиком
    run_simple(
        hostname='127.0.0.1',
        port=5000,
        application=app,
        request_handler=CustomWSGIRequestHandler,
        use_reloader=False,
        use_debugger=False,
        use_evalex=False
    )

if __name__ == '__main__':
    run_production()