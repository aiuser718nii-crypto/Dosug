from flask import Blueprint, request, jsonify
from app import db
from app.models import Subject

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([s.to_dict() for s in subjects])

@subjects_bp.route('/subjects', methods=['POST'])
def create_subject():
    data = request.json
    subject = Subject(
        name=data['name'],
        code=data.get('code')
    )
    db.session.add(subject)
    db.session.commit()
    return jsonify(subject.to_dict()), 201

@subjects_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.json
    if 'name' in data: subject.name = data['name']
    if 'code' in data: subject.code = data['code']
    db.session.commit()
    return jsonify(subject.to_dict())

@subjects_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'success': True})