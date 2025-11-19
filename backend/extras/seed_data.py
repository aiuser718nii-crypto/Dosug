# Файл: backend/seed_data.py

import os
import sys
from datetime import datetime

# --- НАЧАЛО ИСПРАВЛЕНИЯ ПУТЕЙ ИМПОРТА (НАДЕЖНАЯ ВЕРСИЯ) ---
try:
    # Получаем абсолютный путь к текущему файлу
    current_file_path = os.path.abspath(__file__)
    # Поднимаемся вверх по дереву каталогов, пока не найдем папку 'backend'
    backend_dir = current_file_path
    while os.path.basename(backend_dir) != 'backend':
        backend_dir = os.path.dirname(backend_dir)
        if backend_dir == os.path.dirname(backend_dir): # Достигли корня диска
            raise FileNotFoundError("Не удалось найти корневую папку 'backend'.")

    # Добавляем папку 'backend' в путь поиска Python
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # Теперь импорт должен сработать
    from app._init_ import create_app, db
except (ImportError, FileNotFoundError) as e:
    print(f"Критическая ошибка: не удалось настроить пути и импортировать 'create_app' или 'db'.")
    print(f"Детали ошибки: {e}")
    print("Убедитесь, что скрипт находится внутри структуры проекта '.../backend/...'")
    sys.exit(1)
# --- КОНЕЦ ИСПРАВЛЕНИЯ ПУТЕЙ ---


from app.models import Group, Subject, GroupSubject, LessonType, LessonTypeLoad

# --- НАСТРОЙКА ДАННЫХ ---
# Здесь мы определяем, какие группы существуют и какую нагрузку они имеют

GROUPS_DATA = []

app = create_app()

def seed_database():
    """
    Заполняет базу данных группами, связывает их с предметами и определяет учебную нагрузку.
    """
    with app.app_context():
        print("\n" + "="*70)
        print("🌱 ЗАПОЛНЕНИЕ УЧЕБНОЙ НАГРУЗКИ")
        print("="*70 + "\n")
        
        # Получаем словари для быстрого доступа
        subjects_map = {s.code: s for s in Subject.query.all()}
        lesson_types_map = {lt.code.value: lt for lt in LessonType.query.all()}

        if not subjects_map:
            print("❌ ВНИМАНИЕ: В базе данных нет предметов. Запустите сначала скрипт subjects.py.")
            return
        if not lesson_types_map:
            print("❌ ВНИМАНИЕ: В базе данных нет типов занятий. Запустите сначала скрипт semester_data.py.")
            return

        for group_data in GROUPS_DATA:
            # --- 1. Создаем или находим группу ---
            group = Group.query.filter_by(name=group_data["name"]).first()
            if not group:
                group = Group(
                    name=group_data["name"],
                    course=group_data["course"],
                    student_count=group_data["student_count"],
                    is_active=True
                )
                db.session.add(group)
                # Нужно закоммитить, чтобы получить group.id для следующего шага
                db.session.flush()
                print(f"✅ Создана группа: {group.name} (ID: {group.id})")
            else:
                print(f"🔄 Найдена существующая группа: {group.name} (ID: {group.id})")

            # --- 2. Обрабатываем предметы и нагрузку для этой группы ---
            for subject_data in group_data["subjects"]:
                subject_code = subject_data["subject_code"]
                subject = subjects_map.get(subject_code)

                if not subject:
                    print(f"  ❌ ВНИМАНИЕ: Предмет с кодом '{subject_code}' не найден в базе. Пропускаем.")
                    continue
                
                # --- 3. Создаем или находим связь GroupSubject ---
                group_subject = GroupSubject.query.filter_by(group_id=group.id, subject_id=subject.id).first()
                if not group_subject:
                    group_subject = GroupSubject(group_id=group.id, subject_id=subject.id)
                    db.session.add(group_subject)
                    db.session.flush() # Получаем ID для group_subject
                    print(f"  ✅ Создана связь: '{group.name}' -> '{subject.name}' (GS_ID: {group_subject.id})")
                
                # --- 4. Очищаем старую нагрузку и создаем новую в LessonTypeLoad ---
                LessonTypeLoad.query.filter_by(group_subject_id=group_subject.id).delete()
                # db.session.flush() # Применяем удаление немедленно

                for load_data in subject_data["loads"]:
                    load_type_code = load_data["type_code"]
                    load_hours = load_data["hours"]
                    lesson_type = lesson_types_map.get(load_type_code)

                    if not lesson_type:
                        print(f"    ❌ ВНИМАНИЕ: Тип занятия '{load_type_code}' не найден. Пропускаем.")
                        continue

                    new_load = LessonTypeLoad(
                        group_subject_id=group_subject.id,
                        lesson_type_id=lesson_type.id,
                        hours_per_week=load_hours
                    )
                    db.session.add(new_load)
                    print(f"    -> Добавлена нагрузка: {lesson_type.name} - {load_hours} ч/нед")

        try:
            db.session.commit()
            print("\n✅ База данных успешно заполнена учебной нагрузкой!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Произошла ошибка при сохранении данных: {e}")

if __name__ == '__main__':
    seed_database()