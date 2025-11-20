from flask import Blueprint, request, jsonify
from app import db
from app.models import Teacher, Subject

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([t.to_dict(include_details=True) for t in teachers])

@teachers_bp.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.json
    
    # Преобразуем пустую строку в None
    email_value = data.get('email') or None

    teacher = Teacher(
        name=data['name'],
        email=email_value, # Используем обработанное значение
        max_hours_per_week=data.get('max_hours_per_week', 20)
    )
    
    if 'subject_ids' in data:
        for subject_id in data['subject_ids']:
            subject = Subject.query.get(subject_id)
            if subject:
                teacher.subjects.append(subject)
                
    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.to_dict()), 201

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return jsonify(teacher.to_dict(include_details=True))

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    data = request.json
    
    # Обновляем поля, кроме email
    for field in ['name', 'phone', 'max_hours_per_week', 'min_hours_per_week', 
                  'department', 'position', 'academic_degree', 'is_active', 'notes']:
        if field in data:
            setattr(teacher, field, data[field])
            
    # Обрабатываем email отдельно
    if 'email' in data:
        teacher.email = data['email'] or None

    if 'subject_ids' in data:
        teacher.subjects = []
        for subject_id in data['subject_ids']:
            subject = Subject.query.get(subject_id)
            if subject:
                teacher.subjects.append(subject)
    
    db.session.commit()
    return jsonify(teacher.to_dict())

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({'success': True})