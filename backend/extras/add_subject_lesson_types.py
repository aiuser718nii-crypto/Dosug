# backend/migrations/add_subject_lesson_types.py
"""
Добавление связи предметов с типами занятий

Запуск: 
python migrations/add_subject_lesson_types.py
"""

from app.__init__ import create_app, db
from app.models import LessonType, LessonTypeEnum, Subject
from datetime import datetime

def init_lesson_types():
    """Инициализация всех типов занятий"""
    
    app = create_app()
    with app.app_context():
        print("Инициализация типов занятий...")
        
        # Определение всех типов с их параметрами
        lesson_types_data = [
            {
                'code': LessonTypeEnum.LECTURE,
                'name': 'Лекция',
                'description': 'Теоретическое занятие',
                'duration_hours': 2,
                'requires_special_room': False,
                'can_be_online': True,
                'color': '#3B82F6'  # Синий
            },
            {
                'code': LessonTypeEnum.SEMINAR,
                'name': 'Семинар',
                'description': 'Практическое занятие с обсуждением',
                'duration_hours': 2,
                'requires_special_room': False,
                'can_be_online': True,
                'color': '#10B981'  # Зеленый
            },
            {
                'code': LessonTypeEnum.LAB,
                'name': 'Лабораторная работа',
                'description': 'Практическая работа в лаборатории',
                'duration_hours': 2,
                'requires_special_room': True,
                'can_be_online': False,
                'color': '#8B5CF6'  # Фиолетовый
            },
            {
                'code': LessonTypeEnum.PRACTICE,
                'name': 'Практика',
                'description': 'Практическое занятие',
                'duration_hours': 2,
                'requires_special_room': False,
                'can_be_online': True,
                'color': '#F59E0B'  # Оранжевый
            },
            {
                'code': LessonTypeEnum.FIELD_TRIP,
                'name': 'Выезд в поле',
                'description': 'Выездное занятие на местности',
                'duration_hours': 4,
                'requires_special_room': False,
                'can_be_online': False,
                'color': '#EF4444'  # Красный
            },
            {
                'code': LessonTypeEnum.TRAINING_CENTER,
                'name': 'Выезд в учебный центр',
                'description': 'Занятие в специализированном учебном центре',
                'duration_hours': 4,
                'requires_special_room': False,
                'can_be_online': False,
                'color': '#EC4899'  # Розовый
            },
            {
                'code': LessonTypeEnum.PRODUCTION_VISIT,
                'name': 'Выезд на производство',
                'description': 'Экскурсия на производство',
                'duration_hours': 4,
                'requires_special_room': False,
                'can_be_online': False,
                'color': '#14B8A6'  # Бирюзовый
            },
            {
                'code': LessonTypeEnum.EXERCISES,
                'name': 'Выезд на учения',
                'description': 'Практические военные учения',
                'duration_hours': 6,
                'requires_special_room': False,
                'can_be_online': False,
                'color': '#6366F1'  # Индиго
            },
            {
                'code': LessonTypeEnum.INDIVIDUAL,
                'name': 'Индивидуальное собеседование',
                'description': 'Индивидуальная работа со студентом',
                'duration_hours': 1,
                'requires_special_room': False,
                'can_be_online': True,
                'color': '#78716C'  # Серый
            },
            {
                'code': LessonTypeEnum.EXAM,
                'name': 'Экзамен',
                'description': 'Итоговая проверка знаний',
                'duration_hours': 3,
                'requires_special_room': False,
                'can_be_online': False,
                'color': '#DC2626'  # Темно-красный
            },
            {
                'code': LessonTypeEnum.TEST,
                'name': 'Зачёт',
                'description': 'Промежуточная проверка знаний',
                'duration_hours': 2,
                'requires_special_room': False,
                'can_be_online': False,
                'color': '#FBBF24'  # Желтый
            }
        ]
        
        for lt_data in lesson_types_data:
            existing = LessonType.query.filter_by(code=lt_data['code']).first()
            
            if existing:
                # Обновляем существующий
                for key, value in lt_data.items():
                    setattr(existing, key, value)
                print(f"  Обновлен: {lt_data['name']}")
            else:
                # Создаем новый
                lesson_type = LessonType(**lt_data)
                db.session.add(lesson_type)
                print(f"  Создан: {lt_data['name']}")
        
        db.session.commit()
        print("✅ Типы занятий инициализированы")
        
        # Добавляем типы по умолчанию для всех предметов
        print("\nДобавление типов по умолчанию для предметов...")
        add_default_lesson_types()

def add_default_lesson_types():
    """Добавить стандартные типы занятий для всех предметов"""
    
    # Получаем типы занятий
    lecture = LessonType.query.filter_by(code=LessonTypeEnum.LECTURE).first()
    seminar = LessonType.query.filter_by(code=LessonTypeEnum.SEMINAR).first()
    
    if not lecture or not seminar:
        print("❌ Не найдены базовые типы занятий")
        return
    
    # Для всех предметов добавляем лекции и семинары как доступные типы
    subjects = Subject.query.all()
    for subject in subjects:
        if lecture not in subject.allowed_lesson_types:
            subject.allowed_lesson_types.append(lecture)
        if seminar not in subject.allowed_lesson_types:
            subject.allowed_lesson_types.append(seminar)
        print(f"  ✓ {subject.name}: добавлены лекции и семинары")
    
    db.session.commit()
    print("✅ Типы по умолчанию добавлены")

if __name__ == '__main__':
    init_lesson_types()