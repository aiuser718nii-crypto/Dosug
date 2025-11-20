"""
Скрипт для проверки целостности данных, в первую очередь занятий (Lesson).
Ищет "битые" ссылки, где занятие ссылается на несуществующую сущность.
Запускать как модуль: python -m extras.check_lessons
"""
from app import create_app, db
from app.models import Lesson, Week, Group, Subject, Teacher, Room

app = create_app()

def check_data_integrity():
    """
    Проверяет целостность ссылок в занятиях.
    """
    with app.app_context():
        print("\n" + "="*70)
        print("🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ РАСПИСАНИЯ")
        print("="*70)

        # --- ЗАГРУЗКА СПРАВОЧНИКОВ ID ---
        print("\nЗагрузка справочников ID...")
        week_ids = {w.id for w in Week.query.all()}
        group_ids = {g.id for g in Group.query.all()}
        subject_ids = {s.id for s in Subject.query.all()}
        teacher_ids = {t.id for t in Teacher.query.all()}
        room_ids = {r.id for r in Room.query.all()}
        print("✅ Справочники загружены.")

        # --- ПРОВЕРКА LESSON ---
        print("\n" + "-"*70)
        print("Проверка таблицы 'Lesson'...")
        all_lessons = Lesson.query.all()
        print(f"   Всего занятий: {len(all_lessons)}")
        
        broken_lessons = set()
        
        for lesson in all_lessons:
            is_broken = False
            if lesson.week_id not in week_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Week ID: {lesson.week_id}")
                is_broken = True
            if lesson.group_id not in group_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Group ID: {lesson.group_id}")
                is_broken = True
            if lesson.subject_id not in subject_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Subject ID: {lesson.subject_id}")
                is_broken = True
            if lesson.teacher_id not in teacher_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Teacher ID: {lesson.teacher_id}")
                is_broken = True
            if lesson.room_id not in room_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Room ID: {lesson.room_id}")
                is_broken = True
            
            if is_broken:
                broken_lessons.add(lesson)

        if not broken_lessons:
            print("   ✅ Все занятия корректны!")
        else:
            print(f"\n   ⚠️  Найдено {len(broken_lessons)} 'битых' занятий.")

        # --- ПРЕДЛОЖЕНИЕ ОБ ОЧИСТКЕ ---
        if broken_lessons:
            print("\n" + "="*70)
            confirm = input(f"❓ Найдено {len(broken_lessons)} 'битых' занятий. Удалить их? (yes/no): ")
            if confirm.lower() == 'yes':
                print("\n🗑️  Удаление 'битых' занятий...")
                for lesson in broken_lessons:
                    db.session.delete(lesson)
                
                try:
                    db.session.commit()
                    print(f"✅ Успешно удалено {len(broken_lessons)} занятий.")
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Ошибка при удалении: {e}")
            else:
                print("Операция отменена.")
        else:
            print("\n" + "="*70)
            print("🎉 Все ссылки в занятиях корректны!")
            print("="*70)

if __name__ == '__main__':
    check_data_integrity()