"""
Модели базы данных для системы генерации расписания.
Итоговая версия после рефакторинга.
"""

from app import db
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import event, UniqueConstraint, Enum
from sqlalchemy.ext.hybrid import hybrid_property
import enum

# ========== ВСПОМОГАТЕЛЬНЫЕ ТАБЛИЦЫ ==========

teacher_subjects = db.Table('teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


# ========== ENUMS ==========

class LessonTypeEnum(enum.Enum):
    """Типы занятий"""
    LECTURE = "lecture"
    SEMINAR = "seminar"
    LAB = "lab"
    PRACTICE = "practice"
    FIELD_TRIP = "field_trip"
    TRAINING_CENTER = "training_center"
    PRODUCTION_VISIT = "production_visit"
    EXERCISES = "exercises"
    INDIVIDUAL = "individual"
    EXAM = "exam"
    TEST = "test"


class SemesterEnum(enum.Enum):
    """Семестры"""
    FALL = "fall"
    SPRING = "spring"


# ========== ОСНОВНЫЕ МОДЕЛИ ==========

class Teacher(db.Model):
    """Модель преподавателя"""
    __tablename__ = 'teacher'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    
    max_hours_per_week = db.Column(db.Integer, default=20)
    min_hours_per_week = db.Column(db.Integer, default=0)
    
    department = db.Column(db.String(100))
    position = db.Column(db.String(50))
    academic_degree = db.Column(db.String(50))
    
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Связи
    subjects = db.relationship(
        'Subject',
        secondary=teacher_subjects,
        backref=db.backref('teachers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    unavailable_slots = db.relationship(
        'TeacherUnavailableSlot',
        back_populates='teacher',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    preferred_slots = db.relationship(
        'TeacherPreferredSlot',
        back_populates='teacher',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    @hybrid_property
    def subject_list(self) -> List:
        return list(self.subjects.all())
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'max_hours_per_week': self.max_hours_per_week,
            'min_hours_per_week': self.min_hours_per_week,
            'department': self.department,
            'position': self.position,
            'is_active': self.is_active,
            'subjects': [{'id': s.id, 'name': s.name, 'code': s.code} for s in self.subjects.all()],
        }
        if include_details:
            result['notes'] = self.notes
        return result
    
    def __repr__(self):
        return f'<Teacher {self.name}>'


class AcademicYear(db.Model):
    """Учебный год"""
    __tablename__ = 'academic_year'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)  # "2023/2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    
    semesters = db.relationship('Semester', back_populates='academic_year', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Semester(db.Model):
    """Семестр"""
    __tablename__ = 'semester'
    
    id = db.Column(db.Integer, primary_key=True)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
    type = db.Column(Enum(SemesterEnum), nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    academic_year = db.relationship('AcademicYear', back_populates='semesters')
    weeks = db.relationship('Week', back_populates='semester', cascade='all, delete-orphan', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_weeks(self):
        return self.weeks.count()
    
    def generate_weeks(self):
        Week.query.filter_by(semester_id=self.id).delete()
        db.session.commit()

        current_date = self.start_date
        week_number = 1

        while current_date <= self.end_date:
            week_start = current_date
            week_end = min(current_date + timedelta(days=6), self.end_date)

            week = Week(
                semester_id=self.id,
                week_number=week_number,
                start_date=week_start,
                end_date=week_end
            )
            db.session.add(week)

            current_date += timedelta(days=7)
            week_number += 1

        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'total_weeks': self.total_weeks
        }


class Week(db.Model):
    """Неделя"""
    __tablename__ = 'week'
    
    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    is_session = db.Column(db.Boolean, default=False)
    is_vacation = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    semester = db.relationship('Semester', back_populates='weeks')
    # Связь обновлена на Lesson (ранее LessonExtended)
    lessons = db.relationship('Lesson', back_populates='week', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'week_number': self.week_number,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_session': self.is_session,
            'is_vacation': self.is_vacation
        }


class LessonType(db.Model):
    """Тип занятия"""
    __tablename__ = 'lesson_type'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(Enum(LessonTypeEnum), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    duration_hours = db.Column(db.Integer, default=2)
    requires_special_room = db.Column(db.Boolean, default=False)
    can_be_online = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), default='#3B82F6')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code.value,
            'name': self.name,
            'duration_hours': self.duration_hours,
            'requires_special_room': self.requires_special_room,
            'color': self.color
        }


class LessonTypeLoad(db.Model):
    """Нагрузка по типу занятия для связки 'группа-предмет'"""
    __tablename__ = 'lesson_type_load'
    
    id = db.Column(db.Integer, primary_key=True)
    group_subject_id = db.Column(db.Integer, db.ForeignKey('group_subject.id'), nullable=False)
    lesson_type_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    hours_per_week = db.Column(db.Integer, nullable=False, default=0)

    lesson_type = db.relationship('LessonType')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lesson_type_id': self.lesson_type_id,
            'lesson_type_name': self.lesson_type.name if self.lesson_type else None,
            'hours_per_week': self.hours_per_week
        }


class LessonTypeConstraint(db.Model):
    """Ограничения между типами занятий"""
    __tablename__ = 'lesson_type_constraint'
    
    id = db.Column(db.Integer, primary_key=True)
    type_from_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    type_to_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    
    min_days_between = db.Column(db.Integer, default=0)
    max_days_between = db.Column(db.Integer)
    same_subject_only = db.Column(db.Boolean, default=True)
    
    type_from = db.relationship('LessonType', foreign_keys=[type_from_id])
    type_to = db.relationship('LessonType', foreign_keys=[type_to_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'type_from': self.type_from.name,
            'type_to': self.type_to.name,
            'min_days_between': self.min_days_between,
            'max_days_between': self.max_days_between
        }


class TeacherUnavailableSlot(db.Model):
    """Недоступные слоты преподавателя"""
    __tablename__ = 'teacher_unavailable_slot'
    __table_args__ = (UniqueConstraint('teacher_id', 'day', 'time_slot', name='unique_teacher_unavailable'),)
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    time_slot = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    
    teacher = db.relationship('Teacher', back_populates='unavailable_slots')


class TeacherPreferredSlot(db.Model):
    """Предпочитаемые слоты преподавателя"""
    __tablename__ = 'teacher_preferred_slot'
    __table_args__ = (UniqueConstraint('teacher_id', 'day', 'time_slot', name='unique_teacher_preferred'),)
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    time_slot = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, default=3)
    
    teacher = db.relationship('Teacher', back_populates='preferred_slots')


class Room(db.Model):
    """Аудитория"""
    __tablename__ = 'room'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    building = db.Column(db.String(50))
    floor = db.Column(db.Integer)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50))
    is_special = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    equipment = db.relationship('RoomEquipment', back_populates='room', cascade='all, delete-orphan', lazy='dynamic')
    
    @hybrid_property
    def equipment_list(self) -> List[str]:
        return [eq.equipment_type for eq in self.equipment.all()]
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'name': self.name,
            'building': self.building,
            'capacity': self.capacity,
            'room_type': self.room_type,
            'is_special': self.is_special,
            'is_active': self.is_active,
            'equipment': self.equipment_list
        }
        if include_details:
            result['notes'] = self.notes
        return result


class RoomEquipment(db.Model):
    __tablename__ = 'room_equipment'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    condition = db.Column(db.String(50))
    room = db.relationship('Room', back_populates='equipment')


class Subject(db.Model):
    """Предмет"""
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, index=True)
    short_name = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    difficulty_level = db.Column(db.Integer, default=3)
    
    # Эти поля можно оставить для совместимости или удалить, если используется только LessonTypeLoad
    lecture_hours = db.Column(db.Integer, default=0)
    practice_hours = db.Column(db.Integer, default=0)
    lab_hours = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    required_equipment = db.relationship('SubjectEquipment', back_populates='subject', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'difficulty_level': self.difficulty_level,
        }
        return result


class SubjectEquipment(db.Model):
    __tablename__ = 'subject_equipment'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    subject = db.relationship('Subject', back_populates='required_equipment')


class Group(db.Model):
    """Модель группы студентов"""
    __tablename__ = 'group'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    course = db.Column(db.Integer, index=True)
    student_count = db.Column(db.Integer, nullable=False)
    default_room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    
    specialization = db.Column(db.String(100))
    faculty = db.Column(db.String(100))
    start_year = db.Column(db.Integer)
    
    max_lessons_per_day = db.Column(db.Integer, default=7)
    prefer_morning = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    group_subjects = db.relationship(
        'GroupSubject',
        back_populates='group',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    default_room = db.relationship('Room', foreign_keys=[default_room_id])
    
    @hybrid_property
    def total_hours_per_week(self) -> int:
        total = 0
        for gs in self.group_subjects.all():
            for load in gs.lesson_type_loads.all():
                total += load.hours_per_week
        return total
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'name': self.name,
            'course': self.course,
            'student_count': self.student_count,
            'is_active': self.is_active,
        }
        if include_details:
            result['subjects'] = [gs.to_dict() for gs in self.group_subjects.all()]
            result['total_hours_per_week'] = self.total_hours_per_week
        return result
    
    def __repr__(self):
        return f'<Group {self.name}>'


class GroupSubject(db.Model):
    """Связь между группой и предметом"""
    __tablename__ = 'group_subject'
    __table_args__ = (UniqueConstraint('group_id', 'subject_id', name='unique_group_subject'),)

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    semester_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    group = db.relationship('Group', back_populates='group_subjects')
    subject = db.relationship('Subject')
    
    # Нагрузка
    lesson_type_loads = db.relationship(
        'LessonTypeLoad', 
        backref='group_subject', 
        lazy='dynamic', 
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'group_id': self.group_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'loads': [load.to_dict() for load in self.lesson_type_loads.all()]
        }


class Schedule(db.Model):
    """Расписание"""
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(20))
    status = db.Column(db.String(20), default='draft', index=True)
    
    fitness_score = db.Column(db.Float)
    generation_method = db.Column(db.String(50))
    generation_time = db.Column(db.Float)
    generation_params = db.Column(db.JSON)
    conflicts_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Связь на новую единую модель Lesson
    lessons = db.relationship(
        'Lesson',
        back_populates='schedule',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    @hybrid_property
    def lessons_count(self) -> int:
        return self.lessons.count()
    
    def activate(self):
        Schedule.query.filter(
            Schedule.id != self.id,
            Schedule.semester == self.semester,
            Schedule.status == 'active'
        ).update({'status': 'archived'})
        
        self.status = 'active'
        self.activated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_lessons: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'name': self.name,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'status': self.status,
            'fitness_score': self.fitness_score,
            'lessons_count': self.lessons_count,
            'conflicts_count': self.conflicts_count,
            'generation_method': self.generation_method,
            'generation_time': self.generation_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_lessons:
            result['lessons'] = [l.to_dict() for l in self.lessons.all()]
        return result
    
    def get_conflicts(self) -> List[Dict]:
        """Базовая проверка конфликтов"""
        from collections import defaultdict
        conflicts = []
        time_slots_map = defaultdict(list)
        
        for lesson in self.lessons.all():
            key = (lesson.week_id, lesson.day_of_week, lesson.time_slot)
            time_slots_map[key].append(lesson)
        
        for (week, day, slot), slot_lessons in time_slots_map.items():
            if len(slot_lessons) <= 1:
                continue
                
            # Проверка учителей
            teachers = [l.teacher_id for l in slot_lessons]
            if len(teachers) != len(set(teachers)):
                conflicts.append({'type': 'teacher', 'week': week, 'day': day, 'slot': slot})
                
            # Проверка аудиторий
            rooms = [l.room_id for l in slot_lessons]
            if len(rooms) != len(set(rooms)):
                conflicts.append({'type': 'room', 'week': week, 'day': day, 'slot': slot})
                
            # Проверка групп
            groups = [l.group_id for l in slot_lessons]
            if len(groups) != len(set(groups)):
                conflicts.append({'type': 'group', 'week': week, 'day': day, 'slot': slot})
                
        return conflicts


class Lesson(db.Model):
    """
    Единая модель занятия (бывшая LessonExtended).
    Умная модель с поддержкой недель, типов и точного времени.
    """
    __tablename__ = 'lesson'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
    
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    lesson_type_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-4 (Пн-Пт)
    time_slot = db.Column(db.Integer, nullable=False)  # 0-6 (пары)
    duration = db.Column(db.Integer, default=1)
    
    is_online = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    schedule = db.relationship('Schedule', back_populates='lessons')
    week = db.relationship('Week', back_populates='lessons')
    group = db.relationship('Group')
    subject = db.relationship('Subject')
    teacher = db.relationship('Teacher')
    room = db.relationship('Room')
    lesson_type = db.relationship('LessonType')
    
    @property
    def date(self):
        """Точная дата занятия"""
        if self.week:
            return self.week.start_date + timedelta(days=self.day_of_week)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'week_id': self.week_id,
            'week_number': self.week.week_number if self.week else None,
            'date': self.date.isoformat() if self.date else None,
            'day_of_week': self.day_of_week,
            'day': self.day_of_week, # Алиас для совместимости
            'time_slot': self.time_slot,
            'group_id': self.group_id,
            'group': self.group.name if self.group else None,
            'subject_id': self.subject_id,
            'subject': self.subject.name if self.subject else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.name if self.teacher else None,
            'room_id': self.room_id,
            'room': self.room.name if self.room else None,
            'lesson_type': self.lesson_type.to_dict() if self.lesson_type else None,
            'is_online': self.is_online,
        }
    
    def __repr__(self):
        return f'<Lesson W{self.week.week_number if self.week else "?"} {self.subject.name}>'


# ========== СОБЫТИЯ ==========

@event.listens_for(Schedule, 'before_update')
def update_schedule_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()