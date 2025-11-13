from flask import request, jsonify, send_file
from app.api.routes import api_bp
from app.models import Schedule, Lesson
from app.models import Teacher
from app.models import Room
from app.models import Group
from app._init_ import db
from app.schedulers.genetic import GeneticScheduler
from app.exporter import ExcelExporter
from app.services.shedule_services import ScheduleService
import time
import tempfile
import os

schedule_service = ScheduleService()

@api_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """Получить список всех расписаний"""
    schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()
    return jsonify([s.to_dict() for s in schedules])


@api_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Получить конкретное расписание"""
    schedule = Schedule.query.get_or_404(schedule_id)
    lessons = [lesson.to_dict() for lesson in schedule.lessons]
    
    return jsonify({
        **schedule.to_dict(),
        'lessons': lessons
    })


@api_bp.route('/schedules/generate', methods=['POST'])
def generate_schedule():
    """Генерация нового расписания"""
    try:
        data = request.json
        
        # Параметры генерации
        name = data.get('name', 'Новое расписание')
        semester = data.get('semester')
        academic_year = data.get('academic_year')
        method = data.get('method', 'genetic')  # genetic, csp, hybrid
        
        # Параметры генетического алгоритма
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 500)
        mutation_rate = data.get('mutation_rate', 0.01)
        
        # Получаем данные из БД
        teachers = Teacher.query.all()
        rooms = Room.query.all()
        groups = Group.query.all()
        
        if not teachers or not rooms or not groups:
            return jsonify({
                'error': 'Недостаточно данных для генерации расписания'
            }), 400
        
        # Создаем запись расписания
        schedule = Schedule(
            name=name,
            semester=semester,
            academic_year=academic_year,
            generation_method=method,
            status='draft'
        )
        db.session.add(schedule)
        db.session.commit()
        
        # Генерируем расписание
        start_time = time.time()
        
        if method == 'genetic':
            result = schedule_service.generate_genetic(
                teachers=teachers,
                rooms=rooms,
                groups=groups,
                population_size=population_size,
                generations=generations,
                mutation_rate=mutation_rate
            )
        else:
            return jsonify({'error': f'Метод {method} пока не реализован'}), 400
        
        generation_time = time.time() - start_time
        
        # Сохраняем результат
        schedule.fitness_score = result['fitness']
        schedule.generation_time = generation_time
        schedule.conflicts_count = len(result['conflicts'])
        
        # Сохраняем занятия
        for lesson_data in result['lessons']:
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
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'schedule': schedule.to_dict(),
            'conflicts': result['conflicts'],
            'generation_time': generation_time
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/schedules/<int:schedule_id>/export', methods=['POST'])
def export_schedule(schedule_id):
    """Экспорт расписания в Excel"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        data = request.json
        
        export_type = data.get('type', 'group')  # group, teacher, room, consolidated
        use_template = data.get('use_template', True)
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as tmp:
            output_path = tmp.name
        
        # Экспортируем
        exporter = ExcelExporter()
        exporter.export_schedule(
            schedule=schedule,
            output_path=output_path,
            export_type=export_type,
            use_template=use_template
        )
        
        # Отправляем файл
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=f'schedule_{schedule.id}_{export_type}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Удаляем временный файл после отправки
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/schedules/<int:schedule_id>/conflicts', methods=['GET'])
def get_conflicts(schedule_id):
    """Получить конфликты в расписании"""
    schedule = Schedule.query.get_or_404(schedule_id)
    conflicts = schedule_service.check_conflicts(schedule)
    
    return jsonify({
        'schedule_id': schedule_id,
        'conflicts_count': len(conflicts),
        'conflicts': conflicts
    })


@api_bp.route('/schedules/<int:schedule_id>/activate', methods=['POST'])
def activate_schedule(schedule_id):
    """Активировать расписание"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Деактивируем другие расписания
    Schedule.query.filter(
        Schedule.status == 'active',
        Schedule.semester == schedule.semester
    ).update({'status': 'archived'})
    
    schedule.status = 'active'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'schedule': schedule.to_dict()
    })


@api_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Удалить расписание"""
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'success': True})