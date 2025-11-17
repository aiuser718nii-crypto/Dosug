"""
Проверка целостности данных занятий
"""

from app._init_ import create_app, db
from app.models import LessonExtended, Week

app = create_app()

with app.app_context():
    print("\n🔍 Проверка целостности занятий...\n")
    
    # Получаем все занятия
    all_lessons = LessonExtended.query.all()
    print(f"Всего занятий: {len(all_lessons)}")
    
    # Получаем все недели
    all_weeks = Week.query.all()
    week_ids = {week.id for week in all_weeks}
    print(f"Всего недель: {len(all_weeks)}")
    
    # Проверяем битые ссылки
    broken_lessons = []
    for lesson in all_lessons:
        if lesson.week_id not in week_ids:
            broken_lessons.append(lesson)
            print(f"❌ Занятие ID={lesson.id} ссылается на несуществующую неделю week_id={lesson.week_id}")
    
    if broken_lessons:
        print(f"\n⚠️ Найдено {len(broken_lessons)} занятий с битыми ссылками")
        
        answer = input("\nУдалить битые занятия? (yes/no): ")
        if answer.lower() == 'yes':
            for lesson in broken_lessons:
                db.session.delete(lesson)
            db.session.commit()
            print(f"✅ Удалено {len(broken_lessons)} битых занятий")
        else:
            print("Операция отменена")
    else:
        print("\n✅ Все занятия корректны!")
    
    # Проверяем связь
    print("\n🔗 Проверка связи week...")
    for lesson in all_lessons[:5]:  # Первые 5 для примера
        if lesson.week:
            print(f"✅ Занятие ID={lesson.id}: week.week_number={lesson.week.week_number}")
        else:
            print(f"❌ Занятие ID={lesson.id}: week=None (week_id={lesson.week_id})")