# Файл: backend/clean_all.py

"""
Скрипт для ПОЛНОЙ ОЧИСТКИ данных, связанных с расписаниями, группами и нагрузкой.
ИСПОЛЬЗОВАТЬ С ОСТОРОЖНОСТЬЮ!
"""

import os
import sys

# --- ИСПРАВЛЕНИЕ ПУТЕЙ ИМПОРТА ---
try:
    # Определение пути к папке 'backend'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Если скрипт в папке extras, поднимаемся на уровень выше
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

# Импортируем все модели, которые будем очищать
from app.models import Schedule, Lesson, LessonExtended, Group, GroupSubject, LessonTypeLoad

app = create_app()

def clean_all_schedule_data():
    """
    Удаляет все данные о расписаниях, занятиях, группах и их нагрузке.
    """
    with app.app_context():
        print("\n" + "="*70)
        print("🗑️  ОПАСНАЯ ОПЕРАЦИЯ: ПОЛНАЯ ОЧИСТКА ДАННЫХ О РАСПИСАНИЯХ")
        print("="*70)
        print("Будут удалены:")
        print("  - Все сгенерированные Расписания (Schedule)")
        print("  - Все Занятия (Lesson, LessonExtended)")
        print("  - Вся Учебная нагрузка (LessonTypeLoad)")
        print("  - Все связи Групп с Предметами (GroupSubject)")
        print("  - Все Группы (Group)")
        print("\n" + "-"*70)

        # --- ЗАПРОС НА ПОДТВЕРЖДЕНИЕ ---
        confirm = input("⚠️  Вы уверены, что хотите продолжить? Введите 'YES' для подтверждения: ")
        
        if confirm != 'YES':
            print("\n❌ Операция отменена пользователем.")
            return

        print("\nНачинаем очистку...\n")

        try:
            # Удаляем в правильном порядке, чтобы избежать ошибок внешних ключей
            
            # 1. Занятия
            deleted_lessons_ext = LessonExtended.query.delete()
            print(f"  - Удалено расширенных занятий (LessonExtended): {deleted_lessons_ext}")
            
            deleted_lessons = Lesson.query.delete()
            print(f"  - Удалено базовых занятий (Lesson): {deleted_lessons}")
            
            # 2. Расписания
            deleted_schedules = Schedule.query.delete()
            print(f"  - Удалено расписаний (Schedule): {deleted_schedules}")

            # 3. Учебная нагрузка
            deleted_loads = LessonTypeLoad.query.delete()
            print(f"  - Удалено записей о нагрузке (LessonTypeLoad): {deleted_loads}")

            # 4. Связи групп и предметов
            deleted_group_subjects = GroupSubject.query.delete()
            print(f"  - Удалено связей групп с предметами (GroupSubject): {deleted_group_subjects}")

            # 5. Группы
            deleted_groups = Group.query.delete()
            print(f"  - Удалено групп (Group): {deleted_groups}")

            db.session.commit()
            
            print("\n" + "="*70)
            print("✅ Все указанные данные успешно очищены!")
            print("="*70)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Произошла ошибка во время очистки: {e}")

if __name__ == '__main__':
    clean_all_schedule_data()