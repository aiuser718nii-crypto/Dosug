from flask import Blueprint, request, jsonify
from app import db
from app.models import Room

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([r.to_dict() for r in rooms])

@rooms_bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.json
    room = Room(
        name=data['name'],
        capacity=data['capacity'],
        building=data.get('building'),
        is_special=data.get('is_special', False) 
    )
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201

@rooms_bp.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict(include_details=True))

@rooms_bp.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.json
    for field in ['name', 'capacity', 'building', 'floor', 'room_type', 'is_special', 'is_active', 'notes']:
        if field in data:
            setattr(room, field, data[field])
    db.session.commit()
    return jsonify(room.to_dict())

@rooms_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'success': True})