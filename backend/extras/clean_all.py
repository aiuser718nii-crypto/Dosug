# backend/clean_all.py
from app._init_ import create_app, db
from app.models import Schedule
from app.models import LessonExtended

app = create_app()

with app.app_context():
    print("\n🗑️ Очистка всех расписаний...\n")
    
    # Удаляем все занятия
    deleted_lessons = LessonExtended.query.delete()
    print(f"✅ Удалено занятий: {deleted_lessons}")
    
    # Удаляем все расписания
    deleted_schedules = Schedule.query.delete()
    print(f"✅ Удалено расписаний: {deleted_schedules}")
    
    db.session.commit()
    
    print("\n✅ База данных очищена!")