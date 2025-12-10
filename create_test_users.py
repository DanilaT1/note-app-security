from app import app, db
from models import User

with app.app_context():
    # Создаем тестовых пользователей
    test_users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'user1', 'password': 'password1'},
        {'username': 'test', 'password': 'test123'}
    ]
    
    for user_data in test_users:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(username=user_data['username'], password=user_data['password'])
            db.session.add(user)
    
    db.session.commit()
    print("Тестовые пользователи созданы!")