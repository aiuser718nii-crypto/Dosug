from flask import Blueprint, request, jsonify
from app import db
from app.models import AcademicYear, Semester, LessonType, LessonTypeConstraint, SemesterEnum
from datetime import datetime

semesters_bp = Blueprint('semesters', __name__)

# ==================== ACADEMIC YEARS ====================
@semesters_bp.route('/academic-years', methods=['GET'])
def get_academic_years():
    """Получить все учебные годы"""
    years = AcademicYear.query.order_by(AcademicYear.start_date.desc()).all()
    return jsonify([{
        'id': y.id, 
        'name': y.name, 
        'start_date': y.start_date.isoformat(),
        'end_date': y.end_date.isoformat(),
        'is_current': y.is_current,
        'semesters_count': len(y.semesters)
    } for y in years])

@semesters_bp.route('/academic-years', methods=['POST'])
def create_academic_year():
    """Создать новый учебный год"""
    data = request.json
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
    return jsonify({'id': year.id, 'name': year.name}), 201

@semesters_bp.route('/academic-years/<int:year_id>/set-current', methods=['POST'])
def set_current_year(year_id):
    """Установить текущий учебный год"""
    AcademicYear.query.update({'is_current': False})
    year = AcademicYear.query.get_or_404(year_id)
    year.is_current = True
    db.session.commit()
    return jsonify({'success': True, 'message': f'Учебный год {year.name} установлен как текущий'})


# ==================== SEMESTERS ====================
@semesters_bp.route('/semesters', methods=['GET'])
def get_semesters():
    """Получить все семестры, опционально фильтруя по году"""
    year_id = request.args.get('academic_year_id')
    query = Semester.query
    if year_id:
        query = query.filter_by(academic_year_id=year_id)
    semesters = query.all()
    return jsonify([s.to_dict() for s in semesters])

@semesters_bp.route('/semesters', methods=['POST'])
def create_semester():
    """Создать новый семестр"""
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
    semester.generate_weeks() # Автоматически генерируем недели
    return jsonify(semester.to_dict()), 201

@semesters_bp.route('/semesters/<int:semester_id>/weeks', methods=['GET'])
def get_semester_weeks(semester_id):
    """Получить недели для конкретного семестра"""
    semester = Semester.query.get_or_404(semester_id)
    weeks = semester.weeks.all()
    return jsonify([w.to_dict() for w in weeks])

@semesters_bp.route('/semesters/<int:semester_id>/regenerate-weeks', methods=['POST'])
def regenerate_weeks(semester_id):
    """Пересоздать недели для семестра"""
    semester = Semester.query.get_or_404(semester_id)
    semester.generate_weeks()
    return jsonify({'success': True, 'weeks_count': semester.total_weeks})


# ==================== LESSON TYPES ====================
@semesters_bp.route('/lesson-types', methods=['GET'])
def get_lesson_types():
    """Получить все типы занятий"""
    types = LessonType.query.all()
    return jsonify([t.to_dict() for t in types])

# (Здесь можно добавить POST, PUT, DELETE для типов занятий, если нужно)


# ==================== LESSON TYPE CONSTRAINTS ====================
@semesters_bp.route('/lesson-type-constraints', methods=['GET'])
def get_constraints():
    """Получить все ограничения"""
    constraints = LessonTypeConstraint.query.all()
    return jsonify([c.to_dict() for c in constraints])

@semesters_bp.route('/lesson-type-constraints', methods=['POST'])
def create_constraint():
    """Создать новое ограничение"""
    data = request.json
    
    # Проверка на дубликат
    existing = LessonTypeConstraint.query.filter_by(
        type_from_id=data['type_from_id'],
        type_to_id=data['type_to_id']
    ).first()
    if existing:
        return jsonify({'error': 'Такое ограничение уже существует'}), 409 # 409 Conflict
    
    constraint = LessonTypeConstraint(
        type_from_id=data['type_from_id'],
        type_to_id=data['type_to_id'],
        min_days_between=data.get('min_days_between', 0),
        max_days_between=data.get('max_days_between') # SQLAlchemy обработает None
    )
    db.session.add(constraint)
    db.session.commit()
    return jsonify(constraint.to_dict()), 201

@semesters_bp.route('/lesson-type-constraints/<int:constraint_id>', methods=['PUT'])
def update_constraint(constraint_id):
    """Обновить существующее ограничение"""
    constraint = LessonTypeConstraint.query.get_or_404(constraint_id)
    data = request.json
    
    # Обновляем поля, если они переданы
    if 'min_days_between' in data:
        constraint.min_days_between = data['min_days_between']
    if 'max_days_between' in data:
        constraint.max_days_between = data.get('max_days_between')
        
    db.session.commit()
    return jsonify(constraint.to_dict())

@semesters_bp.route('/lesson-type-constraints/<int:constraint_id>', methods=['DELETE'])
def delete_constraint(constraint_id):
    """Удалить ограничение"""
    constraint = LessonTypeConstraint.query.get_or_404(constraint_id)
    db.session.delete(constraint)
    db.session.commit()
    return jsonify({'success': True})