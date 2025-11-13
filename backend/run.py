"""
Точка входа для запуска Flask приложения
"""

from app._init_ import create_app
import os

# Создаем приложение
app = create_app()

if __name__ == '__main__':
    # Получаем порт из переменных окружения или используем 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*70)
    print("🚀 ЗАПУСК СЕРВЕРА ГЕНЕРАТОРА РАСПИСАНИЯ")
    print("="*70)
    print(f"📍 Сервер запущен на: http://localhost:{port}")
    print(f"📊 API доступен на: http://localhost:{port}/api")
    print("="*70)
    print("\n📋 Доступные endpoints:")
    print("   GET  /api/teachers       - Список преподавателей")
    print("   POST /api/teachers       - Добавить преподавателя")
    print("   GET  /api/rooms          - Список аудиторий")
    print("   POST /api/rooms          - Добавить аудиторию")
    print("   GET  /api/subjects       - Список предметов")
    print("   POST /api/subjects       - Добавить предмет")
    print("   GET  /api/groups         - Список групп")
    print("   POST /api/groups         - Добавить группу")
    print("   GET  /api/schedules      - Список расписаний")
    print("   POST /api/schedules/generate - Генерация расписания")
    print("="*70 + "\n")
    
    # Запуск сервера
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )