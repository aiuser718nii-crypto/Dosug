from flask import Blueprint, request, jsonify
from app import db
from app.models import Group, GroupSubject, LessonTypeLoad 

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    return jsonify([g.to_dict(include_details=True) for g in groups])

@groups_bp.route('/groups', methods=['POST'])
def create_group():
    data = request.json
    group = Group(
        name=data['name'],
        course=data.get('course'),
        student_count=data['student_count']
    )
    db.session.add(group)
    db.session.commit()
    
    if 'subjects' in data:
        for subj_data in data['subjects']:
            # Создаем связь
            gs = GroupSubject(
                group_id=group.id,
                subject_id=subj_data['subject_id']
            )
            db.session.add(gs)
            # Здесь логика добавления LessonTypeLoad (нагрузки) должна быть
            # реализована в соответствии с новой моделью, но пока оставим базовую
            
        db.session.commit()
    
    return jsonify(group.to_dict()), 201

@groups_bp.route('/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """Обновить группу и ее учебную нагрузку"""
    group = Group.query.get_or_404(group_id)
    data = request.json
    
    # 1. Обновляем основные поля группы
    if 'name' in data: group.name = data['name']
    if 'course' in data: group.course = data['course']
    if 'student_count' in data: group.student_count = data['student_count']
    # ... добавь другие поля, если они есть ...

    # 2. Обновляем предметы и нагрузку
    if 'subjects' in data:
        # Собираем ID предметов, которые пришли с фронтенда
        incoming_subject_ids = {s['subject_id'] for s in data['subjects']}
        
        # Удаляем те связи "Группа-Предмет", которых больше нет в запросе
        GroupSubject.query.filter(
            GroupSubject.group_id == group_id,
            ~GroupSubject.subject_id.in_(incoming_subject_ids)
        ).delete(synchronize_session=False)

        # Проходимся по предметам, которые пришли с фронтенда
        for subj_data in data['subjects']:
            subject_id = subj_data['subject_id']
            
            # Находим или создаем связь "Группа-Предмет"
            gs = GroupSubject.query.filter_by(
                group_id=group_id, 
                subject_id=subject_id
            ).first()
            
            if not gs:
                gs = GroupSubject(group_id=group_id, subject_id=subject_id)
                db.session.add(gs)
                db.session.flush() # Нужно для получения gs.id

            # !!! КЛЮЧЕВАЯ ЧАСТЬ !!!
            # Удаляем СТАРУЮ нагрузку ТОЛЬКО для этого предмета
            LessonTypeLoad.query.filter_by(group_subject_id=gs.id).delete()
            
            # Добавляем НОВУЮ нагрузку из массива 'loads'
            for load_data in subj_data.get('loads', []):
                new_load = LessonTypeLoad(
                    group_subject_id=gs.id,
                    lesson_type_id=load_data['lesson_type_id'],
                    hours_per_week=load_data['hours_per_week']
                )
                db.session.add(new_load)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при обновлении группы: {e}")
        return jsonify({'error': 'Internal server error'}), 500
        
    # Возвращаем обновленные данные группы
    return jsonify(group.to_dict(include_details=True))

@groups_bp.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'success': True})

@groups_bp.route('/groups/<int:group_id>/set-default-room', methods=['POST'])
def set_group_default_room(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.json
    room_id = data.get('room_id')
    
    if room_id:
        room = Room.query.get_or_404(room_id)
        group.default_room_id = room_id
    else:
        group.default_room_id = None
    
    db.session.commit()
    return jsonify({'success': True})