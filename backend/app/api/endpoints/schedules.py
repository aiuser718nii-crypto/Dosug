from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models import Schedule, Lesson, Teacher, Room, Group, Semester, AcademicYear, Week, SemesterEnum
from app.schedulers.csp import CSPScheduler
from app.exporter import ExcelExporter
import tempfile
import os
import traceback

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """Получить список всех расписаний"""
    schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()
    return jsonify([s.to_dict() for s in schedules])

@schedules_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Получить одно расписание (базовая информация)"""
    schedule = Schedule.query.get_or_404(schedule_id)
    return jsonify(schedule.to_dict())

@schedules_bp.route('/schedules/generate-semester', methods=['POST'])
def generate_semester_schedule():
    """Генерация расписания с использованием CSP"""
    try:
        data = request.json
        print(f"🚀 Запуск генерации CSP для семестра {data.get('semester_id')}")
        
        # 1. Создаем запись расписания
        schedule = Schedule(
            name=data.get('name', 'Новое семестровое расписание'),
            semester=data.get('semester_label'),
            academic_year=data.get('academic_year'),
            generation_method='csp_backtracking'
        )
        db.session.add(schedule)
        db.session.commit()
        
        # 2. Запускаем планировщик
        scheduler = CSPScheduler(
            semester_id=data['semester_id'],
            max_iterations=data.get('max_iterations', 500000),
            max_lessons_per_day=data.get('max_lessons_per_day', 5),
        )
        result = scheduler.generate()
        
        # 3. Сохраняем результаты
        for lesson_data in result['lessons']:
            lesson = Lesson(
                schedule_id=schedule.id,
                **lesson_data
            )
            db.session.add(lesson)
            
        schedule.fitness_score = result.get('fitness', 0.0)
        schedule.conflicts_count = len(result.get('conflicts', []))
        schedule.generation_time = result.get('time', 0.0)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'schedule_id': schedule.id,
            'lessons_count': len(result['lessons']),
            'conflicts': result.get('conflicts', []),
            'fitness': result.get('fitness', 0.0),
            'time': result.get('time', 0.0)
        })
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schedules_bp.route('/schedules/<int:schedule_id>/extended', methods=['GET'])
def get_extended_schedule(schedule_id):
    """Получение расписания с разбивкой по неделям"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        lessons = Lesson.query.filter_by(schedule_id=schedule_id).all()
        
        weeks_data = {}
        for lesson in lessons:
            if not lesson.week: continue
            week_num = lesson.week.week_number
            
            if week_num not in weeks_data:
                weeks_data[week_num] = {
                    'week_number': week_num,
                    'start_date': lesson.week.start_date.isoformat(),
                    'end_date': lesson.week.end_date.isoformat(),
                    'lessons': []
                }
            weeks_data[week_num]['lessons'].append(lesson.to_dict())
            
        return jsonify({
            **schedule.to_dict(),
            'weeks': sorted(weeks_data.values(), key=lambda x: x['week_number'])
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@schedules_bp.route('/schedules/<int:schedule_id>/week/<int:week_number>', methods=['GET'])
def get_schedule_week(schedule_id, week_number):
    """Получить расписание на конкретную неделю (исправленная версия)"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)

        # 1. Находим семестр, к которому относится расписание
        academic_year = AcademicYear.query.filter_by(name=schedule.academic_year).first()
        if not academic_year:
            academic_year = AcademicYear.query.filter_by(is_current=True).first()
        
        if not academic_year:
            return jsonify({'error': f'Учебный год "{schedule.academic_year}" не найден'}), 404
        
        semester_type_str = schedule.semester.lower()
        if 'осенний' in semester_type_str or 'fall' in semester_type_str:
            semester_type = SemesterEnum.FALL
        else:
            semester_type = SemesterEnum.SPRING

        # 2. Находим нужную неделю внутри правильного семестра и года
        week = Week.query.join(Semester).filter(
            Semester.academic_year_id == academic_year.id,
            Semester.type == semester_type,
            Week.week_number == week_number
        ).first()

        if not week:
            return jsonify({'error': f'Неделя {week_number} для семестра "{schedule.semester}" не найдена'}), 404
        
        # 3. Получаем занятия для этой недели и этого расписания
        lessons = Lesson.query.filter_by(
            schedule_id=schedule_id,
            week_id=week.id
        ).all()
        
        # 4. Группируем по дням и времени
        timetable = {day: {slot: [] for slot in range(7)} for day in range(5)}
        
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
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@schedules_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Удалить расписание"""
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'success': True})

@schedules_bp.route('/schedules/<int:schedule_id>/export', methods=['GET'])
def export_schedule(schedule_id):
    """Экспорт в Excel"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        export_type = request.args.get('type', 'group')
        
        exporter = ExcelExporter()
        
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        
        exporter.export_schedule(schedule, path, export_type=export_type)
        
        return send_file(
            path,
            as_attachment=True,
            download_name=f'schedule_{schedule.id}_{export_type}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500