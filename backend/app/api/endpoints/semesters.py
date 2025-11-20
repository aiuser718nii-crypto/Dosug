from flask import Blueprint, request, jsonify
from app import db
from app.models import AcademicYear, Semester, LessonType, LessonTypeConstraint
from datetime import datetime

semesters_bp = Blueprint('semesters', __name__)

# --- Academic Years ---
@semesters_bp.route('/academic-years', methods=['GET'])
def get_academic_years():
    years = AcademicYear.query.order_by(AcademicYear.start_date.desc()).all()
    return jsonify([{
        'id': y.id, 'name': y.name, 
        'is_current': y.is_current,
        'semesters_count': len(y.semesters)
    } for y in years])

@semesters_bp.route('/academic-years/<int:year_id>/set-current', methods=['POST'])
def set_current_year(year_id):
    AcademicYear.query.update({'is_current': False})
    year = AcademicYear.query.get_or_404(year_id)
    year.is_current = True
    db.session.commit()
    return jsonify({'success': True})

# --- Semesters ---
@semesters_bp.route('/semesters', methods=['GET'])
def get_semesters():
    year_id = request.args.get('academic_year_id')
    query = Semester.query
    if year_id:
        query = query.filter_by(academic_year_id=year_id)
    return jsonify([s.to_dict() for s in query.all()])

@semesters_bp.route('/semesters/<int:semester_id>/weeks', methods=['GET'])
def get_semester_weeks(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    return jsonify([w.to_dict() for w in semester.weeks.all()])

@semesters_bp.route('/semesters/<int:semester_id>/regenerate-weeks', methods=['POST'])
def regenerate_weeks(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    semester.generate_weeks()
    return jsonify({'success': True, 'weeks_count': semester.total_weeks})

# --- Lesson Types ---
@semesters_bp.route('/lesson-types', methods=['GET'])
def get_lesson_types():
    types = LessonType.query.all()
    return jsonify([t.to_dict() for t in types])

# --- Constraints ---
@semesters_bp.route('/lesson-type-constraints', methods=['GET'])
def get_constraints():
    constraints = LessonTypeConstraint.query.all()
    return jsonify([c.to_dict() for c in constraints])