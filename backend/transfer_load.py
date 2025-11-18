# Файл: backend/transfer_load.py

import os
import sys

# --- НАЧАЛО ИСПРАВЛЕНИЯ ---
# Добавляем корневую папку проекта в путь поиска модулей
# Это позволит Python найти папку 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app._init_ import create_app, db # Импортируем напрямую из файла
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---

from app.models import GroupSubject, LessonTypeLoad, LessonType

app = create_app()

def transfer_data():
    """
    Этот скрипт переносит данные из старых полей (lecture_hours и т.д.)
    в новую таблицу lesson_type_load.
    Запускать его нужно ТОЛЬКО ОДИН РАЗ после миграции.
    """
    with app.app_context():
        # Сначала получаем все типы занятий для удобного доступа
        lesson_types = {lt.code.value: lt.id for lt in LessonType.query.all()}
        
        # Получаем все связи "группа-предмет"
        all_group_subjects = GroupSubject.query.all()
        
        if not all_group_subjects:
            print("Не найдено связей GroupSubject. Нечего переносить.")
            return

        print(f"Найдено {len(all_group_subjects)} записей GroupSubject. Начинаем перенос...")
        
        for gs in all_group_subjects:
            # Проверяем, существует ли группа и предмет, чтобы избежать ошибок
            if not gs.group or not gs.subject:
                print(f"Пропуск записи с ID={gs.id}, т.к. отсутствует группа или предмет.")
                continue
            
            print(f"\nОбработка: Группа '{gs.group.name}', Предмет '{gs.subject.name}'")
            
            # Словарь со старыми полями и их соответствием типам
            load_map = {
                'lecture': getattr(gs, 'lecture_hours', 0),
                'seminar': getattr(gs, 'seminar_hours', 0),
                'lab': getattr(gs, 'lab_hours', 0),
                'practice': getattr(gs, 'practice_hours', 0),
                # Добавь другие твои поля, если они есть
            }
            
            for type_code, hours in load_map.items():
                if hours and hours > 0:
                    lesson_type_id = lesson_types.get(type_code)
                    if lesson_type_id:
                        # Проверяем, нет ли уже такой записи
                        existing_load = LessonTypeLoad.query.filter_by(
                            group_subject_id=gs.id,
                            lesson_type_id=lesson_type_id
                        ).first()
                        
                        if not existing_load:
                            new_load = LessonTypeLoad(
                                group_subject_id=gs.id,
                                lesson_type_id=lesson_type_id,
                                hours_per_week=hours
                            )
                            db.session.add(new_load)
                            print(f"  -> Создана запись: Тип='{type_code}', Часы={hours}")
                        else:
                            print(f"  -- Запись для типа '{type_code}' уже существует. Пропускаем.")
                    else:
                        print(f"  !! ВНИМАНИЕ: Тип занятия '{type_code}' не найден в базе. Пропускаем.")

        # Сохраняем все изменения в базе
        try:
            db.session.commit()
            print("\nПеренос данных завершен!")
        except Exception as e:
            db.session.rollback()
            print(f"\nПроизошла ошибка при сохранении данных: {e}")


if __name__ == '__main__':
    transfer_data()