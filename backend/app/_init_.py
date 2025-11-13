from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = 'dev-secret-key-12345'
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.dirname(basedir), 'instance', 'schedule.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Создаем папки
    instance_dir = os.path.join(os.path.dirname(basedir), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    # Инициализация
    db.init_app(app)
    
    # CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type","Authorization" ]
        }
    })
    
    with app.app_context():
        # Импортируем модели
        from app import models
        
        # Создаем таблицы
        db.create_all()
        
        # РЕГИСТРИРУЕМ BLUEPRINT
        from app.api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # Выводим список маршрутов для отладки
        print("\n" + "="*70)
        print("📋 Зарегистрированные маршруты:")
        print("="*70)
        for rule in app.url_map.iter_rules():
            print(f"   {rule.endpoint:30s} {rule.rule}")
        print("="*70 + "\n")
    
    return app