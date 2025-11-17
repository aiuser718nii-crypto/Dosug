# backend/semester_data.py
"""
Инициализация базовых данных для семестровой системы
"""

from app._init_ import create_app, db
from app.models import (
    AcademicYear, Semester, SemesterEnum, 
    LessonType, LessonTypeEnum, LessonTypeConstraint
)
from datetime import date

app = create_app()

with app.app_context():
    print("🎓 Инициализация системы семестрового планирования...\n")
    
    # Очистка старых данных (опционально)
    confirm = input("⚠️  Очистить существующие данные? (yes/no): ")
    if confirm.lower() == 'yes':
        print("🗑️  Очистка...")
        LessonTypeConstraint.query.delete()
        LessonType.query.delete()
        Semester.query.delete()
        AcademicYear.query.delete()
        db.session.commit()
        print("   ✅ Очищено\n")
    
    # 1. Создание учебного года
    print("📅 Создание учебного года 2025/2026...")
    academic_year = AcademicYear(
        name="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 6, 30),
        is_current=True
    )
    db.session.add(academic_year)
    db.session.commit()
    print(f"   ✅ Создан: {academic_year.name}")
    
    # 2. Создание семестров
    print("\n📆 Создание семестров...")
    
    # Осенний семестр (сентябрь - январь)
    fall_semester = Semester(
        academic_year_id=academic_year.id,
        type=SemesterEnum.FALL,
        start_date=date(2025, 9, 1),
        end_date=date(2026, 1, 31)
    )
    db.session.add(fall_semester)
    
    # Весенний семестр (февраль - июнь)
    spring_semester = Semester(
        academic_year_id=academic_year.id,
        type=SemesterEnum.SPRING,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 6, 30)
    )
    db.session.add(spring_semester)
    db.session.commit()
    
    print(f"   ✅ Осенний: {fall_semester.start_date} - {fall_semester.end_date}")
    print(f"   ✅ Весенний: {spring_semester.start_date} - {spring_semester.end_date}")
    
    # 3. Генерация недель
    print("\n📊 Генерация недель...")
    fall_semester.generate_weeks()
    spring_semester.generate_weeks()
    print(f"   ✅ Осенний: {fall_semester.total_weeks} недель")
    print(f"   ✅ Весенний: {spring_semester.total_weeks} недель")
    
    # 4. Создание типов занятий
    print("\n📝 Создание типов занятий...")
    
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
        lesson_type = LessonType(
            code=code,
            name=name,
            duration_hours=duration,
            requires_special_room=special_room,
            color=color
        )
        db.session.add(lesson_type)
        print(f"   ✅ {name}")
    
    db.session.commit()
    
    # 5. Создание ограничений между типами занятий
    print("\n🔗 Создание ограничений...")
    
    # Загружаем типы занятий
    lecture = LessonType.query.filter_by(code=LessonTypeEnum.LECTURE).first()
    seminar = LessonType.query.filter_by(code=LessonTypeEnum.SEMINAR).first()
    lab = LessonType.query.filter_by(code=LessonTypeEnum.LAB).first()
    practice = LessonType.query.filter_by(code=LessonTypeEnum.PRACTICE).first()
    
    # Проверка
    if not all([lecture, seminar, lab, practice]):
        print("   ❌ ОШИБКА: Не все типы занятий найдены!")
        exit(1)
    
    # Создаём ограничения
    constraints_data = [
        (lecture, seminar, 3, 7, "Лекция → Семинар"),
        (lecture, lab, 2, 7, "Лекция → Лабораторная"),
        (lecture, practice, 1, 5, "Лекция → Практика"),
        (seminar, lab, 1, 5, "Семинар → Лабораторная"),
    ]
    
    for type_from, type_to, min_days, max_days, description in constraints_data:
        constraint = LessonTypeConstraint(
            type_from_id=type_from.id,
            type_to_id=type_to.id,
            min_days_between=min_days,
            max_days_between=max_days,
            same_subject_only=True
        )
        db.session.add(constraint)
        print(f"   ✅ {description}: мин. {min_days} дней, макс. {max_days} дней")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА!")
    print("="*60)
    print(f"📅 Учебный год: {academic_year.name}")
    print(f"📆 Семестров: 2")
    print(f"📊 Недель: {fall_semester.total_weeks + spring_semester.total_weeks}")
    print(f"📝 Типов занятий: {LessonType.query.count()}")
    print(f"🔗 Ограничений: {LessonTypeConstraint.query.count()}")
    print("="*60)