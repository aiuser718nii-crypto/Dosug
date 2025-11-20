"""
Заполняет базу данных группами, связывает их с предметами 
и определяет учебную нагрузку (по новой модели LessonTypeLoad).
Запускать как модуль: python -m extras.seed_data
"""
from app import create_app, db
from app.models import Group, Subject, GroupSubject, LessonType, LessonTypeLoad

# --- НАСТРОЙКА ДАННЫХ ---
# Здесь мы определяем, какие группы существуют и какую нагрузку они имеют
GROUPS_DATA = [
    {
        "name": "ПИ-101", "course": 1, "student_count": 28,
        "subjects": [
            { "subject_code": "ВР", "loads": [{"type_code": "lecture", "hours": 2}, {"type_code": "seminar", "hours": 2}] },
            { "subject_code": "ВС", "loads": [{"type_code": "lecture", "hours": 2}, {"type_code": "lab", "hours": 2}] },
            { "subject_code": "ВО", "loads": [{"type_code": "practice", "hours": 4}] },
        ]
    },
    {
        "name": "ИБ-201", "course": 2, "student_count": 25,
        "subjects": [
            { "subject_code": "ГИС", "loads": [{"type_code": "lecture", "hours": 2}, {"type_code": "lab", "hours": 4}] },
            { "subject_code": "ДО", "loads": [{"type_code": "seminar", "hours": 2}] },
            { "subject_code": "ФП", "loads": [{"type_code": "practice", "hours": 2}] },
        ]
    }
    # Добавь сюда другие группы по аналогии
]

app = create_app()

def seed_database():
    """Заполняет базу данных группами и их нагрузкой."""
    with app.app_context():
        print("\n" + "="*70)
        print("🌱 ЗАПОЛНЕНИЕ УЧЕБНОЙ НАГРУЗКИ")
        print("="*70 + "\n")
        
        subjects_map = {s.code: s for s in Subject.query.all()}
        lesson_types_map = {lt.code.value: lt for lt in LessonType.query.all()}

        if not subjects_map:
            print("❌ ВНИМАНИЕ: В базе данных нет предметов. Запустите сначала extras/subjects.py.")
            return
        if not lesson_types_map:
            print("❌ ВНИМАНИЕ: В базе данных нет типов занятий. Запустите сначала extras/semester_data.py.")
            return

        for group_data in GROUPS_DATA:
            # Создаем или находим группу
            group = Group.query.filter_by(name=group_data["name"]).first()
            if not group:
                group = Group(name=group_data["name"], course=group_data["course"], student_count=group_data["student_count"], is_active=True)
                db.session.add(group)
                db.session.flush() # Нужно для получения ID
                print(f"✅ Создана группа: {group.name}")
            else:
                print(f"🔄 Найдена существующая группа: {group.name}")

            # Обрабатываем предметы и нагрузку
            for subject_data in group_data["subjects"]:
                subject = subjects_map.get(subject_data["subject_code"])
                if not subject:
                    print(f"  ❌ Предмет с кодом '{subject_data['subject_code']}' не найден. Пропуск.")
                    continue
                
                # Создаем или находим связь GroupSubject
                group_subject = GroupSubject.query.filter_by(group_id=group.id, subject_id=subject.id).first()
                if not group_subject:
                    group_subject = GroupSubject(group_id=group.id, subject_id=subject.id)
                    db.session.add(group_subject)
                    db.session.flush()
                
                # Очищаем старую нагрузку и создаем новую в LessonTypeLoad
                LessonTypeLoad.query.filter_by(group_subject_id=group_subject.id).delete()

                for load_data in subject_data["loads"]:
                    lesson_type = lesson_types_map.get(load_data["type_code"])
                    if not lesson_type:
                        print(f"    ❌ Тип занятия '{load_data['type_code']}' не найден. Пропуск.")
                        continue

                    new_load = LessonTypeLoad(
                        group_subject_id=group_subject.id,
                        lesson_type_id=lesson_type.id,
                        hours_per_week=load_data["hours"]
                    )
                    db.session.add(new_load)
                    print(f"    -> Для '{subject.name}' добавлена нагрузка: {lesson_type.name} - {load_data['hours']} ч/нед")

        try:
            db.session.commit()
            print("\n✅ База данных успешно заполнена учебной нагрузкой!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Произошла ошибка при сохранении данных: {e}")

if __name__ == '__main__':
    seed_database()