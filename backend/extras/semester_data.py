"""
Инициализация базовых данных для семестровой системы:
- Учебные годы
- Семестры и недели
- Типы занятий
- Ограничения между типами занятий
Запускать как модуль: python -m extras.semester_data
"""

from datetime import date
from app import create_app, db
from app.models import (
    AcademicYear, Semester, SemesterEnum, 
    LessonType, LessonTypeEnum, LessonTypeConstraint, Week
)

app = create_app()

def initialize_semester_data():
    """Основная функция для инициализации данных"""
    with app.app_context():
        print("\n" + "="*70)
        print("🎓 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ СЕМЕСТРОВОГО ПЛАНИРОВАНИЯ")
        print("="*70)
        
        confirm = input("\n⚠️  Хотите полностью очистить и пересоздать данные о семестрах и типах занятий? (yes/no): ")
        if confirm.lower() == 'yes':
            print("\n🗑️  Очистка старых данных...")
            LessonTypeConstraint.query.delete()
            Week.query.delete()
            Semester.query.delete()
            AcademicYear.query.delete()
            LessonType.query.delete()
            db.session.commit()
            print("   ✅ Данные о семестрах, неделях и типах занятий очищены.\n")
        else:
            print("\nПропуск очистки. Данные будут добавлены или обновлены.\n")
        
        # --- 1. СОЗДАНИЕ УЧЕБНОГО ГОДА ---
        print("="*70)
        print("📅 1. Создание учебного года 2025/2026...")
        year_name = "2025/2026"
        academic_year = AcademicYear.query.filter_by(name=year_name).first()
        if not academic_year:
            academic_year = AcademicYear(
                name=year_name,
                start_date=date(2025, 9, 1),
                end_date=date(2026, 6, 30),
                is_current=True
            )
            db.session.add(academic_year)
            db.session.commit()
            print(f"   ✅ Создан новый учебный год: {academic_year.name}")
        else:
            print(f"   🔄 Учебный год '{year_name}' уже существует.")

        # --- 2. СОЗДАНИЕ СЕМЕСТРОВ ---
        print("\n" + "="*70)
        print("📆 2. Создание семестров...")
        fall_semester = Semester.query.filter_by(academic_year_id=academic_year.id, type=SemesterEnum.FALL).first()
        if not fall_semester:
            fall_semester = Semester(
                academic_year_id=academic_year.id,
                type=SemesterEnum.FALL,
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 31)
            )
            db.session.add(fall_semester)
            print("   ✅ Создан осенний семестр")
        else:
            print("   🔄 Осенний семестр уже существует.")
        
        spring_semester = Semester.query.filter_by(academic_year_id=academic_year.id, type=SemesterEnum.SPRING).first()
        if not spring_semester:
            spring_semester = Semester(
                academic_year_id=academic_year.id,
                type=SemesterEnum.SPRING,
                start_date=date(2026, 2, 1),
                end_date=date(2026, 6, 30)
            )
            db.session.add(spring_semester)
            print("   ✅ Создан весенний семестр")
        else:
            print("   🔄 Весенний семестр уже существует.")
        db.session.commit()

        # --- 3. ГЕНЕРАЦИЯ НЕДЕЛЬ ---
        print("\n" + "="*70)
        print("📊 3. Генерация недель для семестров...")
        if not fall_semester.weeks.first():
            fall_semester.generate_weeks()
            print(f"   ✅ Осенний: сгенерировано {fall_semester.total_weeks} недель")
        else:
            print(f"   🔄 Недели для осеннего семестра уже существуют ({fall_semester.total_weeks} шт.)")

        if not spring_semester.weeks.first():
            spring_semester.generate_weeks()
            print(f"   ✅ Весенний: сгенерировано {spring_semester.total_weeks} недель")
        else:
            print(f"   🔄 Недели для весеннего семестра уже существуют ({spring_semester.total_weeks} шт.)")

        # --- 4. СОЗДАНИЕ ТИПОВ ЗАНЯТИЙ ---
        print("\n" + "="*70)
        print("📝 4. Создание типов занятий...")
        lesson_types_data = [
            (LessonTypeEnum.LECTURE, "Лекция", 2, False, '#3B82F6'),
            (LessonTypeEnum.SEMINAR, "Семинар", 2, False, '#10B981'),
            (LessonTypeEnum.LAB, "Лабораторная работа", 2, True, '#8B5CF6'),
            (LessonTypeEnum.PRACTICE, "Практическое занятие", 2, False, '#F59E0B'),
            (LessonTypeEnum.FIELD_TRIP, "Выезд в поле", 8, True, '#EF4444'),
            (LessonTypeEnum.TRAINING_CENTER, "Выезд в учебный центр", 8, True, '#EC4899'),
            (LessonTypeEnum.PRODUCTION_VISIT, "Выезд на производство", 8, True, '#F97316'),
            (LessonTypeEnum.EXERCISES, "Выезд на учения", 8, True, '#DC2626'),
            (LessonTypeEnum.INDIVIDUAL, "Индивидуальное собеседование", 1, False, '#6366F1'),
            (LessonTypeEnum.EXAM, "Экзамен", 4, False, '#DC2626'),
            (LessonTypeEnum.TEST, "Зачёт", 2, False, '#F59E0B'),
        ]
        
        for code, name, duration, special_room, color in lesson_types_data:
            if not LessonType.query.filter_by(code=code).first():
                lesson_type = LessonType(code=code, name=name, duration_hours=duration, requires_special_room=special_room, color=color)
                db.session.add(lesson_type)
                print(f"   ✅ Создан тип: {name}")
        db.session.commit()
        print("   🔄 Проверка типов занятий завершена.")
        
        # --- 5. СОЗДАНИЕ ОГРАНИЧЕНИЙ МЕЖДУ ТИПАМИ ---
        print("\n" + "="*70)
        print("🔗 5. Создание ограничений между типами занятий...")
        lecture = LessonType.query.filter_by(code=LessonTypeEnum.LECTURE).first()
        seminar = LessonType.query.filter_by(code=LessonTypeEnum.SEMINAR).first()
        lab = LessonType.query.filter_by(code=LessonTypeEnum.LAB).first()
        practice = LessonType.query.filter_by(code=LessonTypeEnum.PRACTICE).first()
        
        if not all([lecture, seminar, lab, practice]):
            print("   ❌ ОШИБКА: Не все базовые типы занятий найдены! Невозможно создать ограничения.")
        else:
            constraints_data = [
                (lecture, seminar, 3, 7, "Лекция → Семинар"),
                (lecture, lab, 2, 7, "Лекция → Лабораторная"),
                (lecture, practice, 1, 5, "Лекция → Практика"),
                (seminar, lab, 1, 5, "Семинар → Лабораторная"),
            ]
            for type_from, type_to, min_days, max_days, desc in constraints_data:
                if not LessonTypeConstraint.query.filter_by(type_from_id=type_from.id, type_to_id=type_to.id).first():
                    constraint = LessonTypeConstraint(type_from_id=type_from.id, type_to_id=type_to.id, min_days_between=min_days, max_days_between=max_days, same_subject_only=True)
                    db.session.add(constraint)
                    print(f"   ✅ Создано ограничение: {desc}")
            db.session.commit()
            print("   🔄 Проверка ограничений завершена.")

        print("\n" + "="*70)
        print("✅ ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ЗАВЕРШЕНА!")
        print("="*70)

if __name__ == '__main__':
    initialize_semester_data()