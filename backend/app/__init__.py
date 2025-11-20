import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import config  # Импортируем настройки из config.py

# 1. Создаем экземпляры расширений ГЛОБАЛЬНО
# Это позволяет моделям импортировать db (from app import db) без циклической ошибки
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """
    Фабрика приложений Flask.
    Создает и настраивает экземпляр приложения.
    """
    # Определяем среду окружения (development/production)
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)

    # 2. Загрузка конфигурации
    # Берем класс конфигурации из словаря в config.py
    if config_name not in config:
        print(f"⚠️  Конфигурация '{config_name}' не найдена, используется 'default'")
        config_name = 'default'
    
    app.config.from_object(config[config_name])

    # 3. Инициализация расширений с конкретным приложением
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Настройка CORS (разрешаем запросы с фронтенда к /api/*)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 4. Контекст приложения
    with app.app_context():
        # Импортируем модели ЗДЕСЬ, чтобы они зарегистрировались в SQLAlchemy/Migrate
        # но не вызывали ошибок импорта при старте
        from app import models

        # Регистрация Blueprint'ов (Маршрутов)
        # Если ты разобьешь routes.py на части, здесь нужно будет импортировать их все
        from app.api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

    # 5. CLI Команды (сохранил твою полезную команду)
    @app.cli.command("list-routes")
    def list_routes():
        """Вывести список всех зарегистрированных маршрутов"""
        print("\n" + "="*80)
        print(f"{'ENDPOINT':<40} {'METHODS':<20} {'RULE'}")
        print("="*80)
        rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
        for rule in rules:
            methods = ', '.join(sorted(rule.methods.difference({'HEAD', 'OPTIONS'})))
            print(f"{rule.endpoint:<40} {methods:<20} {rule.rule}")
        print("="*80 + "\n")

    return app