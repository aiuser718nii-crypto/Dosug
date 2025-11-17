"""
Модели базы данных для системы генерации расписания

Основные сущности:
- Teacher: Преподаватель
- Room: Аудитория
- Subject: Предмет
- Group: Группа студентов
- GroupSubject: Связь группы и предмета
- Schedule: Расписание
- Lesson: Занятие (пара)
- TeacherUnavailableSlot: Недоступные слоты преподавателя
- TeacherPreferredSlot: Предпочитаемые слоты преподавателя
"""

from app._init_ import db
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import event, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta
from sqlalchemy import Enum
import enum

# ========== ВСПОМОГАТЕЛЬНЫЕ ТАБЛИЦЫ ==========

teacher_subjects = db.Table('teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


# ========== ОСНОВНЫЕ МОДЕЛИ ==========


class LessonTypeEnum(enum.Enum):
    """Типы занятий"""
    LECTURE = "lecture"  # Лекция
    SEMINAR = "seminar"  # Семинар
    LAB = "lab"  # Лабораторная работа
    PRACTICE = "practice"  # Практика
    FIELD_TRIP = "field_trip"  # Выезд в поле
    TRAINING_CENTER = "training_center"  # Выезд в учебный центр
    PRODUCTION_VISIT = "production_visit"  # Выезд на производство
    EXERCISES = "exercises"  # Выезд на учения
    INDIVIDUAL = "individual"  # Индивидуальное собеседование
    EXAM = "exam"  # Экзамен
    TEST = "test"  # Зачёт


class SemesterEnum(enum.Enum):
    """Семестры"""
    FALL = "fall"  # Осенний (сентябрь-январь)
    SPRING = "spring"  # Весенний (февраль-июнь)

class Teacher(db.Model):
    """
    Модель преподавателя
    
    Attributes:
        id: Уникальный идентификатор
        name: ФИО преподавателя
        email: Email адрес
        phone: Телефон
        max_hours_per_week: Максимальная нагрузка в неделю
        department: Кафедра
        position: Должность
        is_active: Активен ли преподаватель
        subjects: Список предметов которые ведет
        unavailable_slots: Недоступные временные слоты
        preferred_slots: Предпочитаемые временные слоты
    """
    __tablename__ = 'teacher'
    
    # Основные поля
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    
    # Настройки нагрузки
    max_hours_per_week = db.Column(db.Integer, default=20)
    min_hours_per_week = db.Column(db.Integer, default=0)
    
    # Дополнительная информация
    department = db.Column(db.String(100))
    position = db.Column(db.String(50))  # Должность: профессор, доцент, ассистент
    academic_degree = db.Column(db.String(50))  # Ученая степень
    
    # Статус
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Метаданные
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
        """Получить список предметов преподавателя"""
        return list(self.subjects.all())
    
    @hybrid_property
    def subject_names(self) -> List[str]:
        """Получить список названий предметов"""
        return [s.name for s in self.subjects.all()]
    
    def can_teach(self, subject_id: int) -> bool:
        """
        Проверить, может ли преподаватель вести предмет
        
        Args:
            subject_id: ID предмета
            
        Returns:
            True если может, False если нет
        """
        return self.subjects.filter_by(id=subject_id).first() is not None
    
    def is_available(self, day: int, time_slot: int) -> bool:
        """
        Проверить, доступен ли преподаватель в указанное время
        
        Args:
            day: День недели (0-6)
            time_slot: Временной слот (0-6)
            
        Returns:
            True если доступен, False если нет
        """
        return not self.unavailable_slots.filter_by(
            day=day,
            time_slot=time_slot
        ).first()
    
    def get_preference_score(self, day: int, time_slot: int) -> int:
        """
        Получить оценку предпочтения для времени
        
        Args:
            day: День недели
            time_slot: Временной слот
            
        Returns:
            Оценка предпочтения (0-5, где 5 - наиболее предпочтительно)
        """
        pref = self.preferred_slots.filter_by(
            day=day,
            time_slot=time_slot
        ).first()
        
        return pref.priority if pref else 0
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """
        Конвертация в словарь
        
        Args:
            include_details: Включить ли детальную информацию
            
        Returns:
            Словарь с данными преподавателя
        """
        result = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'max_hours_per_week': self.max_hours_per_week,
            'min_hours_per_week': self.min_hours_per_week,
            'department': self.department,
            'position': self.position,
            'academic_degree': self.academic_degree,
            'is_active': self.is_active,
            'subjects': [{'id': s.id, 'name': s.name, 'code': s.code} for s in self.subjects.all()],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_details:
            result['unavailable_slots'] = [
                {'day': slot.day, 'time_slot': slot.time_slot}
                for slot in self.unavailable_slots.all()
            ]
            result['preferred_slots'] = [
                {'day': slot.day, 'time_slot': slot.time_slot, 'priority': slot.priority}
                for slot in self.preferred_slots.all()
            ]
            result['notes'] = self.notes
        
        return result
    
    def __repr__(self):
        return f'<Teacher {self.name}>'


class AcademicYear(db.Model):
    """
    Учебный год
    
    Определяет временные рамки семестров
    """
    __tablename__ = 'academic_year'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)  # "2023/2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    
    # Связи
    semesters = db.relationship('Semester', back_populates='academic_year', cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AcademicYear {self.name}>'


class Semester(db.Model):
    """
    Семестр
    
    Осенний: сентябрь - январь
    Весенний: февраль - июнь
    """
    __tablename__ = 'semester'
    
    id = db.Column(db.Integer, primary_key=True)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
    type = db.Column(Enum(SemesterEnum), nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Связи
    academic_year = db.relationship('AcademicYear', back_populates='semesters')
    weeks = db.relationship('Week', back_populates='semester', cascade='all, delete-orphan', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_weeks(self):
        """Общее количество недель в семестре"""
        return self.weeks.count()
    
    def generate_weeks(self):
        """Автоматически генерирует недели для семестра"""
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
    
    def __repr__(self):
        return f'<Semester {self.type.value} ({self.start_date} - {self.end_date})>'


class Week(db.Model):
    """
    Неделя учебного семестра
    """
    __tablename__ = 'week'
    
    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # 1-20
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Дополнительные поля
    is_session = db.Column(db.Boolean, default=False)  # Сессия?
    is_vacation = db.Column(db.Boolean, default=False)  # Каникулы?
    notes = db.Column(db.Text)
    
    # Связи
    semester = db.relationship('Semester', back_populates='weeks')
    lessons = db.relationship('LessonExtended', back_populates='week', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'week_number': self.week_number,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_session': self.is_session,
            'is_vacation': self.is_vacation
        }
    
    def __repr__(self):
        return f'<Week {self.week_number} ({self.start_date})>'


class LessonType(db.Model):
    """
    Тип занятия с правилами и ограничениями
    """
    __tablename__ = 'lesson_type'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(Enum(LessonTypeEnum), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Настройки
    duration_hours = db.Column(db.Integer, default=2)  # Продолжительность в часах
    requires_special_room = db.Column(db.Boolean, default=False)
    can_be_online = db.Column(db.Boolean, default=False)
    
    # Цвет для отображения в расписании
    color = db.Column(db.String(7), default='#3B82F6')  # HEX цвет
    
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
    
    def __repr__(self):
        return f'<LessonType {self.name}>'


class LessonTypeConstraint(db.Model):
    """
    Ограничения между типами занятий
    
    Например: между лекцией и семинаром должно пройти минимум 3 дня
    """
    __tablename__ = 'lesson_type_constraint'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Типы занятий
    type_from_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    type_to_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    
    # Ограничение
    min_days_between = db.Column(db.Integer, default=0)  # Минимум дней между
    max_days_between = db.Column(db.Integer)  # Максимум дней между
    
    # Для одного предмета?
    same_subject_only = db.Column(db.Boolean, default=True)
    
    # Связи
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
    
    def __repr__(self):
        return f'<Constraint {self.type_from.name} -> {self.type_to.name}: min {self.min_days_between} days>'

class TeacherUnavailableSlot(db.Model):
    """
    Недоступные временные слоты преподавателя
    
    Например: преподаватель не может вести пары по понедельникам с 8:00
    """
    __tablename__ = 'teacher_unavailable_slot'
    __table_args__ = (
        UniqueConstraint('teacher_id', 'day', 'time_slot', name='unique_teacher_unavailable'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False)  # 0-6 (Пн-Вс)
    time_slot = db.Column(db.Integer, nullable=False)  # 0-6 (пары)
    reason = db.Column(db.String(200))
    
    teacher = db.relationship('Teacher', back_populates='unavailable_slots')
    
    def __repr__(self):
        return f'<TeacherUnavailableSlot teacher={self.teacher_id} day={self.day} slot={self.time_slot}>'


class TeacherPreferredSlot(db.Model):
    """
    Предпочитаемые временные слоты преподавателя
    
    Приоритет: 1 (низкий) - 5 (высокий)
    """
    __tablename__ = 'teacher_preferred_slot'
    __table_args__ = (
        UniqueConstraint('teacher_id', 'day', 'time_slot', name='unique_teacher_preferred'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    time_slot = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, default=3)  # 1-5
    
    teacher = db.relationship('Teacher', back_populates='preferred_slots')
    
    def __repr__(self):
        return f'<TeacherPreferredSlot teacher={self.teacher_id} day={self.day} slot={self.time_slot}>'


class Room(db.Model):
    """
    Модель аудитории
    
    Attributes:
        id: Уникальный идентификатор
        name: Номер/название аудитории
        building: Здание/корпус
        floor: Этаж
        capacity: Вместимость
        room_type: Тип аудитории
        equipment: Оборудование
        is_active: Активна ли аудитория
    """
    __tablename__ = 'room'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    building = db.Column(db.String(50))
    floor = db.Column(db.Integer)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Тип аудитории
    room_type = db.Column(db.String(50))  # lecture, lab, computer, conference, etc.
    
    # Статус
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Связи
    equipment = db.relationship(
        'RoomEquipment',
        back_populates='room',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    @hybrid_property
    def equipment_list(self) -> List[str]:
        """Получить список оборудования"""
        return [eq.equipment_type for eq in self.equipment.all()]
    
    def has_equipment(self, equipment_type: str) -> bool:
        """
        Проверить наличие оборудования
        
        Args:
            equipment_type: Тип оборудования
            
        Returns:
            True если есть, False если нет
        """
        return self.equipment.filter_by(equipment_type=equipment_type).first() is not None
    
    def can_accommodate(self, student_count: int) -> bool:
        """
        Проверить, может ли аудитория вместить группу
        
        Args:
            student_count: Количество студентов
            
        Returns:
            True если может, False если нет
        """
        return self.capacity >= student_count
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Конвертация в словарь"""
        result = {
            'id': self.id,
            'name': self.name,
            'building': self.building,
            'floor': self.floor,
            'capacity': self.capacity,
            'room_type': self.room_type,
            'is_active': self.is_active,
            'equipment': self.equipment_list
        }
        
        if include_details:
            result['notes'] = self.notes
            result['created_at'] = self.created_at.isoformat() if self.created_at else None
        
        return result
    
    def __repr__(self):
        return f'<Room {self.name}>'


class RoomEquipment(db.Model):
    """Оборудование в аудитории"""
    __tablename__ = 'room_equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    condition = db.Column(db.String(50))  # good, fair, poor
    
    room = db.relationship('Room', back_populates='equipment')
    
    def __repr__(self):
        return f'<RoomEquipment {self.equipment_type} x{self.quantity}>'


class Subject(db.Model):
    """
    Модель предмета (дисциплины)
    
    Attributes:
        id: Уникальный идентификатор
        name: Название предмета
        code: Код предмета
        description: Описание
        difficulty_level: Уровень сложности (1-5)
        required_equipment: Необходимое оборудование
    """
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, index=True)
    short_name = db.Column(db.String(50))  # Сокращенное название
    description = db.Column(db.Text)
    
    # Характеристики
    difficulty_level = db.Column(db.Integer, default=3)  # 1-5
    lecture_hours = db.Column(db.Integer, default=0)
    practice_hours = db.Column(db.Integer, default=0)
    lab_hours = db.Column(db.Integer, default=0)
    
    # Статус
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    required_equipment = db.relationship(
        'SubjectEquipment',
        back_populates='subject',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    @hybrid_property
    def total_hours(self) -> int:
        """Общее количество часов"""
        return self.lecture_hours + self.practice_hours + self.lab_hours
    
    @hybrid_property
    def equipment_list(self) -> List[str]:
        """Список необходимого оборудования"""
        return [eq.equipment_type for eq in self.required_equipment.all()]
    
    def requires_equipment(self, equipment_type: str) -> bool:
        """
        Проверить, требуется ли определенное оборудование
        
        Args:
            equipment_type: Тип оборудования
            
        Returns:
            True если требуется, False если нет
        """
        return self.required_equipment.filter_by(equipment_type=equipment_type).first() is not None
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Конвертация в словарь"""
        result = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'short_name': self.short_name,
            'difficulty_level': self.difficulty_level,
            'is_active': self.is_active,
            'equipment': self.equipment_list
        }
        
        if include_details:
            result['description'] = self.description
            result['lecture_hours'] = self.lecture_hours
            result['practice_hours'] = self.practice_hours
            result['lab_hours'] = self.lab_hours
            result['total_hours'] = self.total_hours
        
        return result
    
    def __repr__(self):
        return f'<Subject {self.name}>'


class SubjectEquipment(db.Model):
    """Необходимое оборудование для предмета"""
    __tablename__ = 'subject_equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    is_required = db.Column(db.Boolean, default=True)  # Обязательно или желательно
    
    subject = db.relationship('Subject', back_populates='required_equipment')
    
    def __repr__(self):
        return f'<SubjectEquipment {self.equipment_type}>'


class Group(db.Model):
    """
    Модель группы студентов
    
    Attributes:
        id: Уникальный идентификатор
        name: Название группы
        course: Курс обучения
        student_count: Количество студентов
        specialization: Специализация
        group_subjects: Предметы группы
    """
    __tablename__ = 'group'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    course = db.Column(db.Integer, index=True)  # 1, 2, 3, 4
    student_count = db.Column(db.Integer, nullable=False)
    default_room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    # Дополнительная информация
    specialization = db.Column(db.String(100))
    faculty = db.Column(db.String(100))
    start_year = db.Column(db.Integer)
    
    # Настройки расписания
    max_lessons_per_day = db.Column(db.Integer, default=7)
    prefer_morning = db.Column(db.Boolean, default=True)
    
    # Статус
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Связи
    group_subjects = db.relationship(
        'GroupSubject',
        back_populates='group',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    default_room = db.relationship(
        'Room', 
        foreign_keys=[default_room_id]
        )
    
    @hybrid_property
    def total_hours_per_week(self) -> int:
        """Общее количество часов в неделю"""
        return sum(gs.hours_per_week for gs in self.group_subjects.all())
    
    @hybrid_property
    def subject_list(self) -> List:
        """Список предметов группы"""
        return [gs.subject for gs in self.group_subjects.all()]

    def has_subject(self, subject_id: int) -> bool:
        """
        Проверить, изучает ли группа предмет
        
        Args:
            subject_id: ID предмета
            
        Returns:
            True если изучает, False если нет
        """
        return self.group_subjects.filter_by(subject_id=subject_id).first() is not None
    
    def get_subject_hours(self, subject_id: int) -> int:
        """
        Получить количество часов предмета в неделю
        
        Args:
            subject_id: ID предмета
            
        Returns:
            Количество часов
        """
        gs = self.group_subjects.filter_by(subject_id=subject_id).first()
        return gs.hours_per_week if gs else 0
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Конвертация в словарь"""
            # Собираем список предметов с проверкой на существование   
        subjects_list = []
            
        for gs in self.group_subjects.all():
                # ИСПРАВЛЕНИЕ: Проверяем, что предмет существует
                if gs.subject:
                    subjects_list.append({
                        'subject_id': gs.subject_id,
                        'subject_name': gs.subject.name,
                        'subject_code': gs.subject.code,
                        'hours_per_week': gs.hours_per_week,
                        'lesson_type': gs.lesson_type
                    })
                else:
                    # Логируем проблему для отладки
                    print(f"WARNING: GroupSubject (id={gs.id}) references non-existent subject_id={gs.subject_id} for group '{self.name}'")
                    # Опционально: добавляем запись с заглушкой
                    subjects_list.append({
                        'subject_id': gs.subject_id,
                        'subject_name': f'[УДАЛЁННЫЙ ПРЕДМЕТ ID:{gs.subject_id}]',
                        'subject_code': 'DELETED',
                        'hours_per_week': gs.hours_per_week,
                        'lesson_type': gs.lesson_type
                    })

        result = {
                'id': self.id,
                'name': self.name,
                'course': self.course,
                'student_count': self.student_count,
                'specialization': self.specialization,
                'faculty': self.faculty,
                'is_active': self.is_active,
                'subjects': subjects_list
            }

        if include_details:
                result['total_hours_per_week'] = self.total_hours_per_week
                result['max_lessons_per_day'] = self.max_lessons_per_day
                result['prefer_morning'] = self.prefer_morning
                result['notes'] = self.notes
                result['start_year'] = self.start_year

        return result

    def __repr__(self):
                return f'<Group {self.name}>'


class GroupSubject(db.Model):
    """
    Связь между группой и предметом
    
    Определяет, какие предметы изучает группа и сколько часов
    """
    __tablename__ = 'group_subject'
    __table_args__ = (
        UniqueConstraint('group_id', 'subject_id', 'lesson_type', name='unique_group_subject_type'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    hours_per_week = db.Column(db.Integer, nullable=False)
    lecture_hours = db.Column(db.Integer, default=0)
    seminar_hours = db.Column(db.Integer, default=0)
    lab_hours = db.Column(db.Integer, default=0)
    practice_hours = db.Column(db.Integer, default=0)
    field_trip_hours = db.Column(db.Integer, default=0)
    exercises_hours = db.Column(db.Integer, default=0)
    individual_hours = db.Column(db.Integer, default=0)
    
    @property
    def total_hours(self):
        return (self.lecture_hours + self.seminar_hours + self.lab_hours + 
                self.practice_hours + self.field_trip_hours + 
                self.exercises_hours + self.individual_hours)

    # Тип занятий
    lesson_type = db.Column(db.String(20), default='mixed')  # lecture, practice, lab, mixed
    
    # Семестр
    semester = db.Column(db.Integer)  # 1-8
    
    # Дополнительные настройки
    requires_split = db.Column(db.Boolean, default=False)  # Разделение на подгруппы
    subgroup_count = db.Column(db.Integer, default=1)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    group = db.relationship('Group', back_populates='group_subjects')
    subject = db.relationship('Subject')
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        return {
            'id': self.id,
            'group_id': self.group_id,
            'group_name': self.group.name,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name,
            'hours_per_week': self.hours_per_week,
            'lesson_type': self.lesson_type,
            'semester': self.semester,
            'requires_split': self.requires_split,
            'subgroup_count': self.subgroup_count
        }
    
    def __repr__(self):
        return f'<GroupSubject group={self.group_id} subject={self.subject_id}>'


class LessonExtended(db.Model):
    """
    Расширенная модель занятия с поддержкой недель и типов
    """
    __tablename__ = 'lesson_extended'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
    
    # Основные связи
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    
    # ТИП ЗАНЯТИЯ
    lesson_type_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=False)
    
    # Время
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6
    time_slot = db.Column(db.Integer, nullable=False)  # 0-6
    duration = db.Column(db.Integer, default=1)  # Количество пар
    
    # Дополнительные поля
    is_online = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200))  # Для выездов
    notes = db.Column(db.Text)
    week = db.relationship('Week', back_populates='lessons')
    
    # Связи
    schedule = db.relationship('Schedule')
    week = db.relationship('Week', back_populates='lessons')
    group = db.relationship('Group')
    subject = db.relationship('Subject')
    teacher = db.relationship('Teacher')
    room = db.relationship('Room')
    lesson_type = db.relationship('LessonType')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def date(self):
        """Точная дата занятия"""
        return self.week.start_date + timedelta(days=self.day_of_week)
    
    def to_dict(self):
        return {
            'id': self.id,
            'week_number': self.week.week_number,
            'date': self.date.isoformat(),
            'day_of_week': self.day_of_week,
            'time_slot': self.time_slot,
            'group': self.group.name,
            'subject': self.subject.name,
            'teacher': self.teacher.name,
            'room': self.room.name,
            'lesson_type': self.lesson_type.to_dict(),
            'is_online': self.is_online,
            'location': self.location
        }
    
    def __repr__(self):
        return f'<LessonExtended Week{self.week.week_number} {self.subject.name}>'



class Schedule(db.Model):
    """
    Модель расписания
    
    Attributes:
        id: Уникальный идентификатор
        name: Название расписания
        semester: Семестр
        academic_year: Учебный год
        status: Статус (draft, active, archived)
        lessons: Занятия в расписании
    """
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20))  # "Осенний 2023", "Весенний 2024"
    academic_year = db.Column(db.String(20))  # "2023/2024"
    
    # Статус
    status = db.Column(
        db.String(20),
        default='draft',
        index=True
    )  # draft, active, archived
    
    # Оценка качества
    fitness_score = db.Column(db.Float)
    
    # Метаданные генерации
    generation_method = db.Column(db.String(50))  # simple, genetic, csp, hybrid
    generation_time = db.Column(db.Float)  # Время генерации в секундах
    generation_params = db.Column(db.JSON)  # Параметры генерации
    conflicts_count = db.Column(db.Integer, default=0)
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = db.Column(db.DateTime)  # Когда стало активным
    generation_time = db.Column(db.Float)
    # Автор
    created_by = db.Column(db.String(100))
    
    # Комментарии
    notes = db.Column(db.Text)
    
    # Связи
    lessons = db.relationship(
        'Lesson',
        back_populates='schedule',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    @hybrid_property
    def lessons_count(self) -> int:
        """Количество занятий"""
        return self.lessons.count()
    
    @hybrid_property
    def is_active(self) -> bool:
        """Активно ли расписание"""
        return self.status == 'active'
    
    def activate(self):
        """Активировать расписание"""
        # Деактивируем другие расписания этого семестра
        Schedule.query.filter(
            Schedule.id != self.id,
            Schedule.semester == self.semester,
            Schedule.status == 'active'
        ).update({'status': 'archived'})
        
        self.status = 'active'
        self.activated_at = datetime.utcnow()
        db.session.commit()
    
    def archive(self):
        """Архивировать расписание"""
        self.status = 'archived'
        db.session.commit()
    
    def get_conflicts(self) -> List[Dict]:
        """
        Получить список конфликтов в расписании
        
        Returns:
            Список конфликтов
        """
        from collections import defaultdict
        
        conflicts = []
        time_slots_map = defaultdict(list)
        
        # Группируем по времени
        for lesson in self.lessons.all():
            key = (lesson.day, lesson.time_slot)
            time_slots_map[key].append(lesson)
        
        # Проверяем конфликты
        for (day, time_slot), slot_lessons in time_slots_map.items():
            if len(slot_lessons) <= 1:
                continue
            
            # Проверяем учителей
            teachers = [l.teacher_id for l in slot_lessons]
            if len(teachers) != len(set(teachers)):
                conflicts.append({
                    'type': 'teacher',
                    'day': day,
                    'time_slot': time_slot,
                    'lessons': [l.id for l in slot_lessons]
                })
            
            # Проверяем аудитории
            rooms = [l.room_id for l in slot_lessons]
            if len(rooms) != len(set(rooms)):
                conflicts.append({
                    'type': 'room',
                    'day': day,
                    'time_slot': time_slot,
                    'lessons': [l.id for l in slot_lessons]
                })
            
            # Проверяем группы
            groups = [l.group_id for l in slot_lessons]
            if len(groups) != len(set(groups)):
                conflicts.append({
                    'type': 'group',
                    'day': day,
                    'time_slot': time_slot,
                    'lessons': [l.id for l in slot_lessons]
                })
        
        return conflicts
    
    def to_dict(self, include_lessons: bool = False) -> Dict[str, Any]:
        """Конвертация в словарь"""
        result = {
            'id': self.id,
            'name': self.name,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'status': self.status,
            'fitness_score': self.fitness_score,
            'generation_method': self.generation_method,
            'generation_time': self.generation_time,
            'conflicts_count': self.conflicts_count,
            'lessons_count': self.lessons_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'created_by': self.created_by
        }
        
        if include_lessons:
            result['lessons'] = [l.to_dict() for l in self.lessons.all()]
        
        return result
    
    def __repr__(self):
        return f'<Schedule {self.name} ({self.status})>'


class Lesson(db.Model):
    """
    Модель занятия (пары)
    
    Attributes:
        id: Уникальный идентификатор
        schedule_id: ID расписания
        group_id: ID группы
        subject_id: ID предмета
        teacher_id: ID преподавателя
        room_id: ID аудитории
        day: День недели (0-4)
        time_slot: Временной слот (0-6)
    """
    __tablename__ = 'lesson'
    __table_args__ = (
        db.Index('idx_lesson_time', 'schedule_id', 'day', 'time_slot'),
        db.Index('idx_lesson_teacher', 'schedule_id', 'teacher_id'),
        db.Index('idx_lesson_group', 'schedule_id', 'group_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False, index=True)
    
    # Основные связи
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    
    # Время
    day = db.Column(db.Integer, nullable=False)  # 0-4 (Пн-Пт)
    time_slot = db.Column(db.Integer, nullable=False)  # 0-6 (пары)
    duration = db.Column(db.Integer, default=1)  # Количество слотов (обычно 1)
    
    # Тип занятия
    lesson_type = db.Column(db.String(20))  # lecture, practice, lab
    
    # Дополнительная информация
    notes = db.Column(db.Text)
    is_online = db.Column(db.Boolean, default=False)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    schedule = db.relationship('Schedule', back_populates='lessons')
    group = db.relationship('Group')
    subject = db.relationship('Subject')
    teacher = db.relationship('Teacher')
    room = db.relationship('Room')
    
    @hybrid_property
    def day_name(self) -> str:
        """Название дня недели"""
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[self.day] if 0 <= self.day < len(days) else "?"
    
    @hybrid_property
    def time_name(self) -> str:
        """Название временного слота"""
        times = [
            "08:00-09:30", "09:40-11:10", "11:20-12:50",
            "13:30-15:00", "15:10-16:40", "16:50-18:20", "18:30-20:00"
        ]
        return times[self.time_slot] if 0 <= self.time_slot < len(times) else "?"
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Конвертация в словарь"""
        result = {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'group': self.group.name,
            'group_id': self.group_id,
            'subject': self.subject.name,
            'subject_id': self.subject_id,
            'teacher': self.teacher.name,
            'teacher_id': self.teacher_id,
            'room': self.room.name,
            'room_id': self.room_id,
            'day': self.day,
            'day_name': self.day_name,
            'time_slot': self.time_slot,
            'time_name': self.time_name,
            'duration': self.duration,
            'lesson_type': self.lesson_type,
            'is_online': self.is_online
        }
        
        if include_details:
            result['notes'] = self.notes
            result['group_details'] = self.group.to_dict()
            result['subject_details'] = self.subject.to_dict()
            result['teacher_details'] = self.teacher.to_dict()
            result['room_details'] = self.room.to_dict()
        
        return result
    
    def __repr__(self):
        return f'<Lesson {self.subject.name} - {self.group.name} ({self.day_name}, {self.time_name})>'


# ========== СОБЫТИЯ БАЗЫ ДАННЫХ ==========

@event.listens_for(Schedule, 'before_update')
def update_schedule_timestamp(mapper, connection, target):
    """Обновление временной метки при изменении расписания"""
    target.updated_at = datetime.utcnow()


# @event.listens_for(Schedule, 'before_insert')
# @event.listens_for(Schedule, 'before_update')
# def update_conflicts_count(mapper, connection, target):
#     """Обновление счетчика конфликтов"""
#     if target.lessons:
#         conflicts = target.get_conflicts()
#         target.conflicts_count = len(conflicts)