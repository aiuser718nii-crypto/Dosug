# Файл: backend/app/_init_.py

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # <--- 1. ДОБАВЛЯЕМ ИМПОРТ
import os

# Создаем экземпляры расширений ГЛОБАЛЬНО
db = SQLAlchemy()
migrate = Migrate()           # <--- 2. СОЗДАЕМ ЭКЗЕМПЛЯР MIGRATE

def create_app():
    """
    Фабрика приложений
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # --- Конфигурация ---
    app.config['SECRET_KEY'] = 'dev-secret-key-12345'
    
    # Указываем путь к базе данных в папке 'instance', которая будет создана рядом с 'app'
    db_path = os.path.join(app.instance_path, 'schedule.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Создаем папку instance, если ее нет
    os.makedirs(app.instance_path, exist_ok=True)
    
    # --- Инициализация расширений ---
    db.init_app(app)
    migrate.init_app(app, db) # <--- 3. ИНИЦИАЛИЗИРУЕМ MIGRATE

    # --- CORS ---
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # --- Регистрация Blueprints и импорт моделей ---
    with app.app_context():
        # Импортируем модели, чтобы Alembic (мигратор) их "увидел"
        from app import models
        
        # ‼️ ВАЖНО: Эту строку нужно закомментировать или удалить. 
        # ‼️ Теперь за создание и обновление БД отвечает Flask-Migrate.
        # db.create_all() 
        
        # РЕГИСТРИРУЕМ BLUEPRINT
        from app.api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        
    # Команда для вывода списка маршрутов в консоль
    @app.cli.command("list-routes")
    def list_routes():
        print("\n" + "="*70)
        print("📋 Зарегистрированные маршруты:")
        print("="*70)
        rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
        for rule in rules:
            methods = ','.join(sorted(rule.methods.difference({'HEAD', 'OPTIONS'})))
            print(f"   {rule.endpoint:35s} {methods:20s} {rule.rule}")
        print("="*70 + "\n")
    
    return app