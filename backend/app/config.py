import os
from datetime import timedelta

class Config:
    """Базовая конфигурация"""
    
    # Основные настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost:5432/schedule_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Файлы
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Алгоритм расписания
    GENETIC_POPULATION_SIZE = 100
    GENETIC_GENERATIONS = 500
    GENETIC_MUTATION_RATE = 0.01
    GENETIC_CROSSOVER_RATE = 0.7
    GENETIC_ELITE_SIZE = 10
    
    # Расписание
    DAYS_PER_WEEK = 5
    TIME_SLOTS_PER_DAY = 7
    DEFAULT_TIME_SLOTS = [
        "08:00-09:30", "09:40-11:10", "11:20-12:50",
        "13:30-15:00", "15:10-16:40", "16:50-18:20", "18:30-20:00"
    ]
    
    # Redis (для кэширования)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery (для фоновых задач)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    # Строка для подключения к PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/schedule_db'


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    # Используйте переменные окружения для продакшена


class TestingConfig(Config):
    """Конфигурация для тестов"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///schedule_test.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}