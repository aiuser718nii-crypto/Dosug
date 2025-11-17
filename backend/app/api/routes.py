from flask import Blueprint, request, jsonify, send_file
from app._init_ import db
from app.models import Teacher, Room, Group, Subject, Schedule, Lesson, GroupSubject
from app.schedulers.genetic import GeneticScheduler
from app.exporter import ExcelExporter
import tempfile
import os

api_bp = Blueprint('api', __name__)

# ==================== TEACHERS ====================
@api_bp.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([t.to_dict() for t in teachers])

@api_bp.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.json
    teacher = Teacher(
        name=data['name'],
        email=data.get('email'),
        max_hours_per_week=data.get('max_hours_per_week', 20)
    )
    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.to_dict()), 201

# ==================== ROOMS ====================
@api_bp.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([r.to_dict() for r in rooms])

@api_bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.json
    room = Room(
        name=data['name'],
        capacity=data['capacity'],
        building=data.get('building')
    )
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201

# ==================== SUBJECTS ====================
@api_bp.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([s.to_dict() for s in subjects])

@api_bp.route('/subjects', methods=['POST'])
def create_subject():
    data = request.json
    subject = Subject(
        name=data['name'],
        code=data.get('code')
    )
    db.session.add(subject)
    db.session.commit()
    return jsonify(subject.to_dict()), 201

# ==================== GROUPS ====================
@api_bp.route('/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    return jsonify([g.to_dict() for g in groups])

@api_bp.route('/groups', methods=['POST'])
def create_group():
    data = request.json
    group = Group(
        name=data['name'],
        course=data.get('course'),
        student_count=data['student_count']
    )
    db.session.add(group)
    db.session.commit()
    
    # Добавляем предметы для группы
    if 'subjects' in data:
        for subj_data in data['subjects']:
            gs = GroupSubject(
                group_id=group.id,
                subject_id=subj_data['subject_id'],
                hours_per_week=subj_data['hours_per_week']
            )
            db.session.add(gs)
        db.session.commit()
    
    return jsonify(group.to_dict()), 201

# ==================== SCHEDULES ====================
@api_bp.route('/schedules', methods=['GET'])
def get_schedules():
    schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()
    return jsonify([s.to_dict() for s in schedules])

@api_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    return jsonify({
        **schedule.to_dict(),
        'lessons': [l.to_dict() for l in schedule.lessons]
    })

@api_bp.route('/schedules/generate', methods=['POST'])
def generate_schedule():
    try:
        print("=" * 50)
        print("НАЧАЛО ГЕНЕРАЦИИ РАСПИСАНИЯ")
        print("=" * 50)
        
        data = request.json
        print(f"Получены данные: {data}")
        
        # Создаем запись расписания
        print("Создание записи расписания...")
        schedule = Schedule(
            name=data.get('name', 'Новое расписание'),
            semester=data.get('semester'),
            academic_year=data.get('academic_year')
        )
        db.session.add(schedule)
        db.session.commit()  # ← Теперь это работает
        print(f"✓ Расписание создано: ID={schedule.id}")
        
        # Получаем данные
        print("Загрузка данных из БД...")
        teachers = Teacher.query.all()
        print(f"✓ Загружено преподавателей: {len(teachers)}")
        
        rooms = Room.query.all()
        print(f"✓ Загружено аудиторий: {len(rooms)}")
        
        groups = Group.query.all()
        print(f"✓ Загружено групп: {len(groups)}")
        
        # Проверка данных
        if not teachers:
            raise ValueError("В базе нет преподавателей!")
        if not rooms:
            raise ValueError("В базе нет аудиторий!")
        if not groups:
            raise ValueError("В базе нет групп!")
        
        # Генерируем расписание
        print("\nЗапуск генератора расписания...")
        scheduler = GeneticScheduler(teachers, rooms, groups)
        result = scheduler.generate()
        print(f"✓ Расписание сгенерировано: {len(result.get('lessons', []))} занятий")
        
        # Сохраняем занятия
        print("Сохранение занятий...")
        for i, lesson_data in enumerate(result['lessons'], 1):
            lesson = Lesson(
                schedule_id=schedule.id,
                group_id=lesson_data['group_id'],
                subject_id=lesson_data['subject_id'],
                teacher_id=lesson_data['teacher_id'],
                room_id=lesson_data['room_id'],
                day=lesson_data['day'],
                time_slot=lesson_data['time_slot']
            )
            db.session.add(lesson)
        
        schedule.fitness_score = result['fitness']
        

        db.session.commit()
        print("✓ Все занятия сохранены")

        print("Подсчёт конфликтов...")
        conflicts = schedule.get_conflicts()
        schedule.conflicts_count = len(conflicts)
        db.session.commit()
        print(f"✓ Найдено конфликтов: {len(conflicts)}")
        
        print("=" * 50)
        print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("=" * 50)
        
        return jsonify({
            'success': True,
            'schedule': schedule.to_dict(),
            'conflicts': conflicts  # result['conflicts'] or conflicts
        })
        
    except Exception as e:
        print("=" * 50)
        print("ОШИБКА ПРИ ГЕНЕРАЦИИ")
        print("=" * 50)
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        
        import traceback
        print("\nПолный traceback:")
        traceback.print_exc()
        print("=" * 50)
        
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/schedules/<int:schedule_id>/extended', methods=['GET'])
def get_extended_schedule(schedule_id):
    """Получить расширенное расписание с занятиями по неделям"""
    try:
        from app.models import LessonExtended
        
        schedule = Schedule.query.get_or_404(schedule_id)
        
        # Получаем все занятия
        lessons = LessonExtended.query.filter_by(schedule_id=schedule_id).all()
        
        if not lessons:
            # Нет занятий
            return jsonify({
                'id': schedule.id,
                'name': schedule.name,
                'semester': schedule.semester,
                'academic_year': schedule.academic_year,
                'fitness_score': schedule.fitness_score,
                'conflicts_count': schedule.conflicts_count,
                'weeks': []
            })
        
        # Группируем по неделям
        weeks_data = {}
        skipped_lessons = 0
        
        for lesson in lessons:
            # ДОБАВЛЕНА ПРОВЕРКА: Пропускаем занятия без недели
            if not lesson.week:
                skipped_lessons += 1
                print(f"⚠️ Занятие ID={lesson.id} не имеет недели (week_id={lesson.week_id})")
                continue
            
            week_num = lesson.week.week_number
            
            if week_num not in weeks_data:
                weeks_data[week_num] = {
                    'week_number': week_num,
                    'start_date': lesson.week.start_date.isoformat(),
                    'end_date': lesson.week.end_date.isoformat(),
                    'lessons': []
                }
            
            weeks_data[week_num]['lessons'].append(lesson.to_dict())
        
        if skipped_lessons > 0:
            print(f"⚠️ Пропущено {skipped_lessons} занятий без недели")
        
        return jsonify({
            'id': schedule.id,
            'name': schedule.name,
            'semester': schedule.semester,
            'academic_year': schedule.academic_year,
            'fitness_score': schedule.fitness_score,
            'conflicts_count': schedule.conflicts_count,
            'generation_method': schedule.generation_method,
            'generation_time': schedule.generation_time,
            'weeks': sorted(weeks_data.values(), key=lambda x: x['week_number']),
            'skipped_lessons': skipped_lessons  # Для отладки
        })
        
    except ImportError:
        # Модель LessonExtended не существует, используем старую
        print("⚠️ LessonExtended не найден, используем Lesson")
        
        schedule = Schedule.query.get_or_404(schedule_id)
        lessons = Lesson.query.filter_by(schedule_id=schedule_id).all()
        
        return jsonify({
            'id': schedule.id,
            'name': schedule.name,
            'fitness_score': schedule.fitness_score,
            'conflicts_count': schedule.conflicts_count,
            'weeks': [{
                'week_number': 1,
                'start_date': '2024-09-01',
                'end_date': '2025-01-31',
                'lessons': [l.to_dict() for l in lessons]
            }]
        })
        
    except Exception as e:
        print(f"Ошибка в get_extended_schedule: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# ДОБАВЬТЕ ЭТОТ ЭНДПОИНТ:
@api_bp.route('/schedules/<int:schedule_id>/week/<int:week_number>', methods=['GET'])
def get_schedule_week(schedule_id, week_number):
    """Получить расписание на конкретную неделю"""
    try:
        from app.models import LessonExtended, Week, Semester, AcademicYear
        
        schedule = Schedule.query.get_or_404(schedule_id)
        
        # Находим неделю
        # Предполагаем, что используется текущий учебный год
        current_year = AcademicYear.query.filter_by(is_current=True).first()
        
        if not current_year:
            # Если нет текущего года, берём любой
            current_year = AcademicYear.query.first()
        
        if not current_year:
            return jsonify({'error': 'Не найден учебный год'}), 404
        
        # Ищем неделю по номеру
        week = Week.query.join(Semester).filter(
            Semester.academic_year_id == current_year.id,
            Week.week_number == week_number
        ).first()
        
        if not week:
            return jsonify({'error': f'Неделя {week_number} не найдена'}), 404
        
        # Получаем занятия этой недели
        lessons = LessonExtended.query.filter_by(
            schedule_id=schedule_id,
            week_id=week.id
        ).all()
        
        # Группируем по дням и времени
        timetable = {}
        for day in range(5):  # Пн-Пт
            timetable[day] = {}
            for slot in range(7):  # 7 пар
                timetable[day][slot] = []
        
        for lesson in lessons:
            day = lesson.day_of_week
            slot = lesson.time_slot
            
            if day in timetable and slot in timetable[day]:
                timetable[day][slot].append(lesson.to_dict())
        
        return jsonify({
            'week_number': week_number,
            'start_date': week.start_date.isoformat(),
            'end_date': week.end_date.isoformat(),
            'timetable': timetable
        })
        
    except Exception as e:
        print(f"Ошибка в get_schedule_week: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# # ==================== GROUPS ====================

@api_bp.route('/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """Обновить группу"""
    group = Group.query.get_or_404(group_id)
    data = request.json
    
    # Обновляем основные поля
    if 'name' in data:
        group.name = data['name']
    if 'course' in data:
        group.course = data['course']
    if 'student_count' in data:
        group.student_count = data['student_count']
    if 'specialization' in data:
        group.specialization = data['specialization']
    if 'faculty' in data:
        group.faculty = data['faculty']
    if 'start_year' in data:
        group.start_year = data['start_year']
    if 'max_lessons_per_day' in data:
        group.max_lessons_per_day = data['max_lessons_per_day']
    if 'prefer_morning' in data:
        group.prefer_morning = data['prefer_morning']
    if 'notes' in data:
        group.notes = data['notes']
    if 'is_active' in data:
        group.is_active = data['is_active']
    
    # Обновляем предметы, если переданы
    if 'subjects' in data:
        # Удаляем старые связи
        GroupSubject.query.filter_by(group_id=group.id).delete()
        
        # Добавляем новые
        for subj_data in data['subjects']:
            gs = GroupSubject(
                group_id=group.id,
                subject_id=subj_data['subject_id'],
                hours_per_week=subj_data['hours_per_week'],
                lesson_type=subj_data.get('lesson_type', 'mixed'),
                semester=subj_data.get('semester'),
                requires_split=subj_data.get('requires_split', False),
                subgroup_count=subj_data.get('subgroup_count', 1)
            )
            db.session.add(gs)
    
    db.session.commit()
    return jsonify(group.to_dict())

@api_bp.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Удалить группу"""
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Группа {group.name} удалена'})


# ==================== TEACHERS ====================

@api_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return jsonify(teacher.to_dict(include_details=True))

@api_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    data = request.json
    
    # Обновляем поля
    for field in ['name', 'email', 'phone', 'max_hours_per_week', 'min_hours_per_week', 
                  'department', 'position', 'academic_degree', 'is_active', 'notes']:
        if field in data:
            setattr(teacher, field, data[field])
    
    # Обновляем предметы
    if 'subject_ids' in data:
        # Очищаем старые связи
        teacher.subjects = []
        # Добавляем новые
        for subject_id in data['subject_ids']:
            subject = Subject.query.get(subject_id)
            if subject:
                teacher.subjects.append(subject)
    
    db.session.commit()
    return jsonify(teacher.to_dict())

@api_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Преподаватель {teacher.name} удалён'})

# ==================== ROOMS ====================

@api_bp.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict(include_details=True))

@api_bp.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.json
    
    for field in ['name', 'capacity', 'building', 'floor', 'room_type', 'is_active', 'notes']:
        if field in data:
            setattr(room, field, data[field])
    
    db.session.commit()
    return jsonify(room.to_dict())

@api_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Аудитория {room.name} удалена'})

# ==================== SUBJECTS ====================

@api_bp.route('/subjects/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify(subject.to_dict(include_details=True))

@api_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.json
    
    for field in ['name', 'code', 'short_name', 'description', 'difficulty_level',
                  'lecture_hours', 'practice_hours', 'lab_hours', 'is_active']:
        if field in data:
            setattr(subject, field, data[field])
    
    db.session.commit()
    return jsonify(subject.to_dict())

@api_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Предмет {subject.name} удалён'})

# ==================== SEMESTER MANAGEMENT ====================


@api_bp.route('/semesters', methods=['GET'])
def get_semesters():
    """Получить все семестры"""
    from app.models import Semester
    year_id = request.args.get('academic_year_id')
    
    query = Semester.query
    if year_id:
        query = query.filter_by(academic_year_id=year_id)
    
    semesters = query.all()
    return jsonify([s.to_dict() for s in semesters])

@api_bp.route('/semesters/<int:semester_id>/weeks', methods=['GET'])
def get_semester_weeks(semester_id):
    """Получить недели семестра"""
    from app.models import Semester
    semester = Semester.query.get_or_404(semester_id)
    weeks = semester.weeks.all()
    return jsonify([w.to_dict() for w in weeks])

@api_bp.route('/lesson-types', methods=['GET'])
def get_lesson_types():
    """Получить все типы занятий"""
    from app.models import LessonType
    types = LessonType.query.all()
    return jsonify([t.to_dict() for t in types])

@api_bp.route('/lesson-type-constraints', methods=['GET'])
def get_lesson_type_constraints():
    """Получить ограничения между типами занятий"""
    from app.models import LessonTypeConstraint
    constraints = LessonTypeConstraint.query.all()
    return jsonify([c.to_dict() for c in constraints])

# ==================== SEMESTER MANAGEMENT ====================

@api_bp.route('/academic-years', methods=['GET'])
def get_academic_years():
    """Получить все учебные годы"""
    from app.models import AcademicYear
    
    years = AcademicYear.query.order_by(AcademicYear.start_date.desc()).all()
    return jsonify([{
        'id': y.id,
        'name': y.name,
        'start_date': y.start_date.isoformat(),
        'end_date': y.end_date.isoformat(),
        'is_current': y.is_current,
        'semesters_count': len(y.semesters)
    } for y in years])

@api_bp.route('/academic-years', methods=['POST'])
def create_academic_year():
    """Создать новый учебный год"""
    from app.models import AcademicYear
    from datetime import datetime
    
    data = request.json
    
    # Парсинг дат
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    year = AcademicYear(
        name=data['name'],
        start_date=start_date,
        end_date=end_date,
        is_current=data.get('is_current', False)
    )
    
    db.session.add(year)
    db.session.commit()
    
    return jsonify({
        'id': year.id,
        'name': year.name,
        'start_date': year.start_date.isoformat(),
        'end_date': year.end_date.isoformat()
    }), 201

@api_bp.route('/academic-years/<int:year_id>/set-current', methods=['POST'])
def set_current_year(year_id):
    """Установить текущий учебный год"""
    from app.models import AcademicYear
    
    # Сбросить все текущие
    AcademicYear.query.update({'is_current': False})
    
    # Установить новый
    year = AcademicYear.query.get_or_404(year_id)
    year.is_current = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Учебный год {year.name} установлен как текущий'})

# ==================== SEMESTERS ====================

@api_bp.route('/semesters/<int:semester_id>', methods=['GET'])
def get_semester(semester_id):
    """Получить семестр по ID"""
    from app.models import Semester
    
    semester = Semester.query.get_or_404(semester_id)
    return jsonify({
        **semester.to_dict(),
        'weeks': [w.to_dict() for w in semester.weeks.all()]
    })

@api_bp.route('/semesters', methods=['POST'])
def create_semester():
    """Создать новый семестр"""
    from app.models import Semester, SemesterEnum
    from datetime import datetime
    
    data = request.json
    
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    semester = Semester(
        academic_year_id=data['academic_year_id'],
        type=SemesterEnum(data['type']),
        start_date=start_date,
        end_date=end_date
    )
    
    db.session.add(semester)
    db.session.commit()
    
    # Генерация недель
    semester.generate_weeks()
    
    return jsonify(semester.to_dict()), 201

@api_bp.route('/semesters/<int:semester_id>/regenerate-weeks', methods=['POST'])
def regenerate_weeks(semester_id):
    """Пересоздать недели семестра"""
    from app.models import Semester
    
    semester = Semester.query.get_or_404(semester_id)
    count = semester.generate_weeks(force_regenerate=True)
    
    return jsonify({
        'success': True,
        'weeks_count': count,
        'message': f'Создано {count} недель'
    })

# ==================== LESSON TYPES ====================

@api_bp.route('/lesson-types/<int:type_id>', methods=['GET'])
def get_lesson_type(type_id):
    """Получить тип занятия по ID"""
    from app.models import LessonType
    
    lesson_type = LessonType.query.get_or_404(type_id)
    return jsonify(lesson_type.to_dict())

@api_bp.route('/lesson-types', methods=['POST'])
def create_lesson_type():
    """Создать новый тип занятия"""
    from app.models import LessonType, LessonTypeEnum
    
    data = request.json
    
    lesson_type = LessonType(
        code=LessonTypeEnum(data['code']),
        name=data['name'],
        description=data.get('description'),
        duration_hours=data.get('duration_hours', 2),
        requires_special_room=data.get('requires_special_room', False),
        can_be_online=data.get('can_be_online', False),
        color=data.get('color', '#3B82F6')
    )
    
    db.session.add(lesson_type)
    db.session.commit()
    
    return jsonify(lesson_type.to_dict()), 201

@api_bp.route('/lesson-types/<int:type_id>', methods=['PUT'])
def update_lesson_type(type_id):
    """Обновить тип занятия"""
    from app.models import LessonType
    
    lesson_type = LessonType.query.get_or_404(type_id)
    data = request.json
    
    for field in ['name', 'description', 'duration_hours', 'requires_special_room', 
                  'can_be_online', 'color']:
        if field in data:
            setattr(lesson_type, field, data[field])
    
    db.session.commit()
    return jsonify(lesson_type.to_dict())

@api_bp.route('/lesson-types/<int:type_id>', methods=['DELETE'])
def delete_lesson_type(type_id):
    """Удалить тип занятия"""
    from app.models import LessonType
    
    lesson_type = LessonType.query.get_or_404(type_id)
    name = lesson_type.name
    
    db.session.delete(lesson_type)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Тип занятия "{name}" удалён'})

# ==================== LESSON TYPE CONSTRAINTS ====================

@api_bp.route('/lesson-type-constraints', methods=['POST'])
def create_lesson_type_constraint():
    """Создать новое ограничение"""
    from app.models import LessonTypeConstraint
    
    data = request.json
    
    constraint = LessonTypeConstraint(
        type_from_id=data['type_from_id'],
        type_to_id=data['type_to_id'],
        min_days_between=data.get('min_days_between', 0),
        max_days_between=data.get('max_days_between'),
        same_subject_only=data.get('same_subject_only', True)
    )
    
    db.session.add(constraint)
    db.session.commit()
    
    return jsonify(constraint.to_dict()), 201

@api_bp.route('/lesson-type-constraints/<int:constraint_id>', methods=['PUT'])
def update_lesson_type_constraint(constraint_id):
    """Обновить ограничение"""
    from app.models import LessonTypeConstraint
    
    constraint = LessonTypeConstraint.query.get_or_404(constraint_id)
    data = request.json
    
    for field in ['min_days_between', 'max_days_between', 'same_subject_only']:
        if field in data:
            setattr(constraint, field, data[field])
    
    db.session.commit()
    return jsonify(constraint.to_dict())

@api_bp.route('/lesson-type-constraints/<int:constraint_id>', methods=['DELETE'])
def delete_lesson_type_constraint(constraint_id):
    """Удалить ограничение"""
    from app.models import LessonTypeConstraint
    
    constraint = LessonTypeConstraint.query.get_or_404(constraint_id)
    db.session.delete(constraint)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== EXTENDED SCHEDULE GENERATION ====================

@api_bp.route('/schedules/generate-semester', methods=['POST'])
def generate_semester_schedule():
    """Генерация расписания на семестр с использованием CSP"""
    try:
        data = request.json
        
        print("=" * 70)
        print("НАЧАЛО ГЕНЕРАЦИИ СЕМЕСТРОВОГО РАСПИСАНИЯ (CSP)")
        print("=" * 70)
        
        semester_id = data.get('semester_id')
        if not semester_id:
            return jsonify({'error': 'semester_id обязателен'}), 400
        
        # Создаём запись расписания
        schedule = Schedule(
            name=data.get('name', f'Расписание на семестр'),
            semester=data.get('semester_label', 'Семестр'),
            academic_year=data.get('academic_year', '2024/2025'),
            generation_method='csp_backtracking'
        )
        db.session.add(schedule)
        db.session.commit()
        print(f"✅ Создана запись расписания: ID={schedule.id}")
        
        # ИЗМЕНЕНИЕ: Используем CSP планировщик вместо генетического
        from app.schedulers.csp_scheduler import CSPScheduler
        
        # Параметры (для CSP они не так важны, но можно передать max_iterations)
        max_iterations = data.get('max_iterations', 100000)
        max_iterations = data.get('max_iterations', 100000)
        min_lessons_per_day = data.get('min_lessons_per_day', 2)  # Минимум пар в день
        max_lessons_per_day = data.get('max_lessons_per_day', 4)

        scheduler = CSPScheduler(
            semester_id=semester_id,
            max_iterations=max_iterations,
            min_lessons_per_day=min_lessons_per_day,
            max_lessons_per_day=max_lessons_per_day
        )
        
        result = scheduler.generate()
        
        # Сохранение занятий
        print("\n💾 Сохранение занятий в базу данных...")
        from app.models import LessonExtended
        
        for i, lesson_data in enumerate(result['lessons'], 1):
            lesson = LessonExtended(
                schedule_id=schedule.id,
                week_id=lesson_data['week_id'],
                group_id=lesson_data['group_id'],
                subject_id=lesson_data['subject_id'],
                teacher_id=lesson_data['teacher_id'],
                room_id=lesson_data['room_id'],
                lesson_type_id=lesson_data['lesson_type_id'],
                day_of_week=lesson_data['day'],
                time_slot=lesson_data['time_slot']
            )
            db.session.add(lesson)
            
            if i % 100 == 0:
                print(f"   Сохранено {i}/{len(result['lessons'])}...")
        
        schedule.fitness_score = result['fitness']
        schedule.conflicts_count = len(result['conflicts'])
        schedule.generation_time = result.get('time', 0)
        
        db.session.commit()
        print(f"✅ Сохранено {len(result['lessons'])} занятий")
        
        print("=" * 70)
        print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("=" * 70)
        
        return jsonify({
            'success': True,
            'schedule_id': schedule.id,
            'lessons_count': len(result['lessons']),
            'fitness': result['fitness'],
            'conflicts_count': len(result['conflicts']),
            'conflicts': result['conflicts'],
            'method': result.get('method', 'csp'),
            'iterations': result.get('iterations', 0),
            'time': result.get('time', 0)
        })
        
    except Exception as e:
        print("=" * 70)
        print("ОШИБКА ПРИ ГЕНЕРАЦИИ")
        print("=" * 70)
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        
        import traceback
        traceback.print_exc()
        
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    



# ==================== GROUP SUBJECT EXTENDED ====================

@api_bp.route('/groups/<int:group_id>/subjects-extended', methods=['PUT'])
def update_group_subjects_extended(group_id):
    """
    Обновить распределение часов по типам занятий для предметов группы
    
    Ожидаемый формат:
    {
        "subjects": [
            {
                "subject_id": 1,
                "lecture_hours": 2,
                "seminar_hours": 2,
                "lab_hours": 4,
                "practice_hours": 0,
                ...
            }
        ]
    }
    """
    group = Group.query.get_or_404(group_id)
    data = request.json
    
    for subj_data in data.get('subjects', []):
        gs = GroupSubject.query.filter_by(
            group_id=group_id,
            subject_id=subj_data['subject_id']
        ).first()
        
        if gs:
            # Обновляем часы по типам
            gs.lecture_hours = subj_data.get('lecture_hours', 0)
            gs.seminar_hours = subj_data.get('seminar_hours', 0)
            gs.lab_hours = subj_data.get('lab_hours', 0)
            gs.practice_hours = subj_data.get('practice_hours', 0)
            gs.field_trip_hours = subj_data.get('field_trip_hours', 0)
            gs.exercises_hours = subj_data.get('exercises_hours', 0)
            gs.individual_hours = subj_data.get('individual_hours', 0)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Распределение часов обновлено'
    })

@api_bp.route('/groups/<int:group_id>/set-default-room', methods=['POST'])
def set_group_default_room(group_id):
    """Установить стандартную аудиторию для группы"""
    group = Group.query.get_or_404(group_id)
    data = request.json
    
    room_id = data.get('room_id')
    if room_id:
        room = Room.query.get_or_404(room_id)
        group.default_room_id = room_id
    else:
        group.default_room_id = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'default_room': room.to_dict() if room_id else None
    })

# ==================== STATISTICS ====================

@api_bp.route('/statistics/semester/<int:semester_id>', methods=['GET'])
def get_semester_statistics(semester_id):
    """Получить статистику по семестру"""
    from app.models import Semester, LessonExtended, LessonType, Week
    
    semester = Semester.query.get_or_404(semester_id)
    
    # Подсчёт занятий по типам
    lesson_types_stats = db.session.query(
        LessonType.name,
        db.func.count(LessonExtended.id)
    ).join(
        LessonExtended, LessonExtended.lesson_type_id == LessonType.id
    ).join(
        Week, LessonExtended.week_id == Week.id
    ).filter(
        Week.semester_id == semester_id
    ).group_by(LessonType.name).all()
    
    # Нагрузка по преподавателям
    teacher_load = db.session.query(
        Teacher.name,
        db.func.count(LessonExtended.id)
    ).join(
        LessonExtended, LessonExtended.teacher_id == Teacher.id
    ).join(
        Week, LessonExtended.week_id == Week.id
    ).filter(
        Week.semester_id == semester_id
    ).group_by(Teacher.name).all()
    
    # Использование аудиторий
    room_usage = db.session.query(
        Room.name,
        db.func.count(LessonExtended.id)
    ).join(
        LessonExtended, LessonExtended.room_id == Room.id
    ).join(
        Week, LessonExtended.week_id == Week.id
    ).filter(
        Week.semester_id == semester_id
    ).group_by(Room.name).all()
    
    return jsonify({
        'semester': semester.to_dict(),
        'lesson_types': [{'name': name, 'count': count} for name, count in lesson_types_stats],
        'teacher_load': [{'name': name, 'lessons': count} for name, count in teacher_load],
        'room_usage': [{'name': name, 'lessons': count} for name, count in room_usage]
    })