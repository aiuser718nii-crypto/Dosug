"""
CSP (Constraint Satisfaction Problem) планировщик расписания

Использует backtracking с эвристиками для составления расписания на семестр.
Гарантирует отсутствие конфликтов или сообщает, что решение невозможно.

Версия с корректным backtracking, равномерным распределением и чередованием занятий.

Автор: AI Assistant
Дата: 2024
"""

from typing import List, Dict, Set, Tuple, Optional, Generator
from collections import defaultdict
from datetime import datetime
import random

# Предполагается, что эти модели импортированы из вашего Flask-приложения
from app.models import Teacher, Room, Group, Subject, Semester, Week, LessonType


class TimeSlot:
    """Временной слот в расписании (неделя + день + пара)"""
    def __init__(self, week_id: int, day: int, time: int):
        self.week_id = week_id
        self.day = day
        self.time = time
    
    def __hash__(self):
        return hash((self.week_id, self.day, self.time))
    
    def __eq__(self, other):
        return isinstance(other, TimeSlot) and (self.week_id, self.day, self.time) == (other.week_id, other.day, other.time)
    
    def __repr__(self):
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']
        return f"Неделя {self.week_id}, {days[self.day]}, пара {self.time + 1}"


class LessonTask:
    """Задача планирования ОДНОГО занятия."""
    def __init__(self, group_id: int, subject_id: int, lesson_type_id: int, hours_per_week: int):
        self.group_id = group_id
        self.subject_id = subject_id
        self.lesson_type_id = lesson_type_id
        self.hours_per_week = hours_per_week
    
    def __repr__(self):
        return f"LessonTask(group={self.group_id}, subject={self.subject_id}, type={self.lesson_type_id}, h/w={self.hours_per_week})"


class CSPScheduler:
    """
    CSP планировщик с корректным backtracking, равномерным распределением и чередованием.
    """
    # ИСПРАВЛЕНИЕ: Добавляем 'min_days_between_lessons' в конструктор
    def __init__(self, semester_id: int, max_iterations: int = 1000000, max_lessons_per_day: int = 5, min_days_between_lessons: int = 2):
        self.semester_id = semester_id
        self.max_iterations = max_iterations
        self.iterations = 0
        
        # Настройки ограничений
        self.max_lessons_per_day = max_lessons_per_day
        # ИСПРАВЛЕНИЕ: Сохраняем параметр как атрибут экземпляра
        self.min_days_between_lessons = min_days_between_lessons
        
        # Данные из БД
        self.semester: Optional[Semester] = None
        self.weeks: List[Week] = []
        self.week_ids: List[int] = []
        self.week_id_to_index: Dict[int, int] = {}
        self.groups: List[Group] = []
        self.teachers: List[Teacher] = []
        self.rooms: List[Room] = []
        self.lesson_types: Dict[int, LessonType] = {}
        
        # Плоский список индивидуальных заданий
        self.assignments_to_schedule: List[LessonTask] = []
        self.solution = [] # Здесь будут храниться итоговые назначения
        
        # Состояние планировщика
        self.teacher_busy: Dict[int, Set[TimeSlot]] = defaultdict(set)
        self.room_busy: Dict[int, Set[TimeSlot]] = defaultdict(set)
        self.group_busy: Dict[int, Set[TimeSlot]] = defaultdict(set)
        self.group_daily_count: Dict[Tuple[int, int, int], int] = defaultdict(int)
        self.task_weekly_count: Dict[Tuple[int, int, int], int] = defaultdict(int)

        # Кэши
        self.subject_teachers: Dict[int, List[int]] = defaultdict(list)
        self.group_dict: Dict[int, Group] = {}
        self.subject_dict: Dict[int, Subject] = {}
        
        self.start_time: Optional[datetime] = None
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка всех необходимых данных из БД"""
        print("\n📚 Загрузка данных для CSP планировщика...")
        
        self.semester = Semester.query.get(self.semester_id)
        if not self.semester: raise ValueError(f"Семестр с ID {self.semester_id} не найден")
        
        self.weeks = self.semester.weeks.order_by(Week.week_number).all()
        if not self.weeks: raise ValueError("В семестре нет недель! Запустите генерацию недель.")
        
        self.week_ids = [week.id for week in self.weeks]
        self.week_id_to_index = {wid: i for i, wid in enumerate(self.week_ids)}
        
        print(f"   ✅ Семестр: {self.semester.type.value}, Недель: {len(self.weeks)}")
        
        self.groups = Group.query.filter_by(is_active=True).all()
        if not self.groups: raise ValueError("Нет активных групп!")
        self.group_dict = {g.id: g for g in self.groups}
        print(f"   ✅ Групп: {len(self.groups)}")

        self.teachers = Teacher.query.filter_by(is_active=True).all()
        if not self.teachers: raise ValueError("Нет активных преподавателей!")
        print(f"   ✅ Преподавателей: {len(self.teachers)}")

        self.rooms = Room.query.filter_by(is_active=True).all()
        if not self.rooms: raise ValueError("Нет активных аудиторий!")
        print(f"   ✅ Аудиторий: {len(self.rooms)}")

        self.lesson_types = {lt.id: lt for lt in LessonType.query.all()}
        for teacher in self.teachers:
            for subject in teacher.subjects:
                self.subject_teachers[subject.id].append(teacher.id)
                self.subject_dict[subject.id] = subject
        
        self._create_assignments()

    def _create_assignments(self):
        """Создание плоского списка индивидуальных занятий."""
        print("\n📋 Создание атомарных задач для планирования...")
        
        all_tasks_definitions = []
        for group in self.groups:
            for gs in group.group_subjects:
                if not gs.subject: continue
                
                lesson_configs = [
                    ('lecture', gs.lecture_hours or 0), ('seminar', gs.seminar_hours or 0),
                    ('lab', gs.lab_hours or 0), ('practice', gs.practice_hours or 0),
                ]
                total_specific = sum(h for _, h in lesson_configs)
                if total_specific == 0 and gs.hours_per_week > 0:
                    lesson_configs = [('lecture', gs.hours_per_week)]
                
                for type_name, hours in lesson_configs:
                    if hours == 0: continue
                    l_type = next((lt for lt in self.lesson_types.values() if lt.code.value == type_name), None)
                    if not l_type or not self.subject_teachers[gs.subject_id]: continue
                    
                    total_hours = hours * len(self.weeks)
                    task_def = LessonTask(group.id, gs.subject_id, l_type.id, hours)
                    all_tasks_definitions.extend([task_def] * total_hours)
                    print(f"   • Добавлено {total_hours} занятий: {group.name} / {gs.subject.name} / {type_name}")
        
        all_tasks_definitions.sort(key=lambda t: (len(self._get_suitable_teachers(t)), -t.hours_per_week))
        self.assignments_to_schedule = all_tasks_definitions
        print(f"\n   📊 Всего занятий для планирования: {len(self.assignments_to_schedule)}")
    
    def _get_suitable_teachers(self, task: LessonTask) -> List[int]:
        return self.subject_teachers.get(task.subject_id, [])

    def _get_suitable_rooms(self, task: LessonTask) -> List[Room]:
        group = self.group_dict[task.group_id]
        lesson_type = self.lesson_types[task.lesson_type_id]
        
        if hasattr(group, 'default_room') and group.default_room and not lesson_type.requires_special_room:
            return [group.default_room]
        
        suitable = [r for r in self.rooms if r.capacity >= group.student_count]
        return suitable if suitable else self.rooms

    def _get_domain(self, task: LessonTask) -> Generator[Tuple[TimeSlot, int, int], None, None]:
        """Генератор, который возвращает все возможные значения для одного занятия."""
        suitable_teachers = self._get_suitable_teachers(task)
        suitable_rooms = self._get_suitable_rooms(task)
        if not suitable_teachers or not suitable_rooms: return

        weeks = sorted(self.week_ids, key=lambda wid: self.task_weekly_count.get((task.group_id, task.subject_id, wid), 0))
        times = [1, 2, 0, 3, 4, 5, 6]
        
        for week_id in weeks:
            if self.task_weekly_count.get((task.group_id, task.subject_id, week_id), 0) >= task.hours_per_week:
                continue

            days = list(range(5))
            random.shuffle(days)
            for day in days:
                if self.group_daily_count.get((task.group_id, week_id, day), 0) >= self.max_lessons_per_day:
                    continue

                is_too_close = False
                current_day_index = self.week_id_to_index[week_id] * 5 + day
                # ИСПРАВЛЕНИЕ: Используем self.min_days_between_lessons вместо глобальной константы
                for day_offset in range(-self.min_days_between_lessons + 1, self.min_days_between_lessons):
                    if day_offset == 0: continue
                    check_day_idx = current_day_index + day_offset
                    if 0 <= check_day_idx < len(self.weeks) * 5:
                        check_week_idx, check_day = divmod(check_day_idx, 5)
                        check_week_id = self.week_ids[check_week_idx]
                        for t in range(7):
                            check_slot = TimeSlot(check_week_id, check_day, t)
                            if check_slot in self.group_busy[task.group_id]:
                                if any(a['subject_id'] == task.subject_id for a in self.solution if a['slot'] == check_slot and a['group_id'] == task.group_id):
                                    is_too_close = True
                                    break
                        if is_too_close: break
                if is_too_close: continue

                for time in times:
                    slot = TimeSlot(week_id, day, time)
                    if slot in self.group_busy[task.group_id]: continue
                    
                    for teacher_id in random.sample(suitable_teachers, len(suitable_teachers)):
                        if slot in self.teacher_busy[teacher_id]: continue
                        
                        for room in random.sample(suitable_rooms, len(suitable_rooms)):
                            if slot in self.room_busy[room.id]: continue
                            
                            yield (slot, teacher_id, room.id)

    def _assign(self, task: LessonTask, slot: TimeSlot, teacher_id: int, room_id: int):
        self.solution.append({'task': task, 'slot': slot, 'teacher_id': teacher_id, 'room_id': room_id, 'group_id': task.group_id, 'subject_id': task.subject_id})
        self.group_busy[task.group_id].add(slot)
        self.teacher_busy[teacher_id].add(slot)
        self.room_busy[room_id].add(slot)
        self.group_daily_count[(task.group_id, slot.week_id, slot.day)] += 1
        self.task_weekly_count[(task.group_id, task.subject_id, slot.week_id)] += 1

    def _unassign(self):
        last_assignment = self.solution.pop()
        task, slot, teacher_id, room_id = last_assignment['task'], last_assignment['slot'], last_assignment['teacher_id'], last_assignment['room_id']
        self.group_busy[task.group_id].remove(slot)
        self.teacher_busy[teacher_id].remove(slot)
        self.room_busy[room_id].remove(slot)
        self.group_daily_count[(task.group_id, slot.week_id, slot.day)] -= 1
        self.task_weekly_count[(task.group_id, task.subject_id, slot.week_id)] -= 1

    def _backtrack(self, assignment_index: int) -> bool:
        """Рекурсия по плоскому списку индивидуальных занятий."""
        self.iterations += 1
        if self.iterations > self.max_iterations: return False
        
        if assignment_index >= len(self.assignments_to_schedule):
            return True
        
        if self.iterations % 50000 == 0:
            progress = (assignment_index / len(self.assignments_to_schedule) * 100)
            print(f"   🔄 Итерация {self.iterations:,}: Запланировано {assignment_index}/{len(self.assignments_to_schedule)} ({progress:.1f}%)")
        
        task = self.assignments_to_schedule[assignment_index]
        
        for slot, teacher_id, room_id in self._get_domain(task):
            self._assign(task, slot, teacher_id, room_id)
            if self._backtrack(assignment_index + 1):
                return True
            self._unassign()
            
        return False

    def generate(self) -> Dict:
        print("\n" + "="*70)
        print("🎯 CSP ПЛАНИРОВЩИК (КОРРЕКТНАЯ ВЕРСИЯ)")
        print(f"   - Макс. пар в день: {self.max_lessons_per_day}")
        print(f"   - Перерыв между предметами: {self.min_days_between_lessons} дн.")
        print("="*70)
        
        self.start_time = datetime.now()
        
        print("\n🔍 Запуск алгоритма backtracking...\n")
        success = self._backtrack(0)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        
        if success:
            print(f"✅ РАСПИСАНИЕ УСПЕШНО СОСТАВЛЕНО! ({len(self.solution)} занятий)")
            print("="*70)
            
            result_lessons = []
            for a in self.solution:
                task, slot = a['task'], a['slot']
                result_lessons.append({
                    'group_id': task.group_id, 'subject_id': task.subject_id,
                    'lesson_type_id': task.lesson_type_id, 'teacher_id': a['teacher_id'],
                    'room_id': a['room_id'], 'week_id': slot.week_id, 'day': slot.day, 'time_slot': slot.time
                })

            print(f"📊 Статистика:")
            print(f"   • Итераций: {self.iterations:,}")
            print(f"   • Время: {elapsed:.2f} сек")
            print(f"   • Конфликтов: 0 (гарантировано)")
            print("="*70)
            
            return {
                'lessons': result_lessons, 'fitness': 1.0, 'conflicts': [],
                'method': 'csp_backtracking_correct', 'iterations': self.iterations, 'time': elapsed
            }
        else:
            print("❌ НЕ УДАЛОСЬ СОСТАВИТЬ РАСПИСАНИЕ")
            print("="*70)
            progress = (len(self.solution) / len(self.assignments_to_schedule) * 100) if self.assignments_to_schedule else 0
            
            print(f"📊 Прогресс: {progress:.1f}% ({len(self.solution)}/{len(self.assignments_to_schedule)} занятий)")
            print(f"   • Итераций: {self.iterations:,} (возможно, достигнут лимит)")
            print(f"   • Время: {elapsed:.2f} сек")
            
            print(f"\n🔍 Возможные причины:")
            print(f"   • Чрезмерно строгие ограничения (мало пар в день, слишком большой перерыв между предметами).")
            print(f"   • Нехватка аудиторий/преподавателей для предметов с высокой нагрузкой.")
            print(f"   • Слишком большая общая нагрузка на группы, не помещающаяся в сетку.")
            
            return {
                'lessons': [], 'fitness': progress / 100,
                'conflicts': [{'type': 'no_solution_found', 'message': f'Не удалось найти полное решение. Прогресс: {progress:.1f}%'}],
                'method': 'csp_backtracking_correct', 'iterations': self.iterations, 'time': elapsed
            }