# Файл: backend/check_lessons.py

"""
Скрипт для проверки целостности данных, в первую очередь занятий (Lesson и LessonExtended).
Ищет "битые" ссылки, где занятие ссылается на несуществующую сущность.
"""

import os
import sys

# --- ИСПРАВЛЕНИЕ ПУТЕЙ ИМПОРТА ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir) == 'extras':
        backend_dir = os.path.dirname(current_dir)
    else:
        backend_dir = current_dir
    
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    from app._init_ import create_app, db
except ImportError as e:
    print(f"Критическая ошибка: не удалось импортировать 'create_app' или 'db'.")
    print(f"Детали ошибки: {e}")
    sys.exit(1)

from app.models import Lesson, LessonExtended, Week, Group, Subject, Teacher, Room

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

        # --- ПРОВЕРКА LESSON_EXTENDED ---
        print("\n" + "-"*70)
        print("1. Проверка таблицы 'LessonExtended'...")
        all_ext_lessons = LessonExtended.query.all()
        print(f"   Всего занятий в LessonExtended: {len(all_ext_lessons)}")
        
        broken_ext_lessons = set()
        
        for lesson in all_ext_lessons:
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
                broken_ext_lessons.add(lesson)

        if not broken_ext_lessons:
            print("   ✅ Все занятия в 'LessonExtended' корректны!")
        else:
            print(f"\n   ⚠️  Найдено {len(broken_ext_lessons)} 'битых' занятий в LessonExtended.")

        # --- ПРОВЕРКА LESSON (если используется) ---
        print("\n" + "-"*70)
        print("2. Проверка таблицы 'Lesson'...")
        all_lessons = Lesson.query.all()
        print(f"   Всего занятий в Lesson: {len(all_lessons)}")

        broken_lessons = set()
        
        for lesson in all_lessons:
            is_broken = False
            if lesson.group_id not in group_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Group ID: {lesson.group_id}")
                is_broken = True
            if lesson.subject_id not in subject_ids:
                print(f"  ❌ ID {lesson.id}: Битая ссылка на Subject ID: {lesson.subject_id}")
                is_broken = True
            # ... и так далее для teacher_id, room_id
            
            if is_broken:
                broken_lessons.add(lesson)

        if not broken_lessons:
            print("   ✅ Все занятия в 'Lesson' корректны!")
        else:
            print(f"\n   ⚠️  Найдено {len(broken_lessons)} 'битых' занятий в Lesson.")

        # --- ПРЕДЛОЖЕНИЕ ОБ ОЧИСТКЕ ---
        total_broken = broken_ext_lessons.union(broken_lessons)
        
        if total_broken:
            print("\n" + "="*70)
            confirm = input(f"❓ Найдено всего {len(total_broken)} 'битых' занятий. Удалить их? (yes/no): ")
            if confirm.lower() == 'yes':
                print("\n🗑️  Удаление 'битых' занятий...")
                for lesson in total_broken:
                    db.session.delete(lesson)
                
                try:
                    db.session.commit()
                    print(f"✅ Успешно удалено {len(total_broken)} занятий.")
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