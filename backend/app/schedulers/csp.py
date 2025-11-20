import random
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Generator
from collections import defaultdict

from app.schedulers.base import BaseScheduler
from app.models import Semester, Week, LessonType, Group, Teacher, Room, Subject, LessonTypeConstraint

class TimeSlot:
    """Вспомогательный класс для CSP: Временной слот"""
    def __init__(self, week_id: int, day: int, time: int):
        self.week_id, self.day, self.time = week_id, day, time
    
    def __hash__(self):
        return hash((self.week_id, self.day, self.time))
    
    def __eq__(self, other):
        return (isinstance(other, TimeSlot) and 
                (self.week_id, self.day, self.time) == (other.week_id, other.day, other.time))

class LessonTask:
    """Вспомогательный класс для CSP: Задача на размещение одного занятия"""
    def __init__(self, group_id: int, subject_id: int, lesson_type_id: int, hours_per_week: int):
        self.group_id, self.subject_id, self.lesson_type_id, self.hours_per_week = group_id, subject_id, lesson_type_id, hours_per_week

class CSPScheduler(BaseScheduler):
    """
    CSP (Constraint Satisfaction Problem) планировщик с бэктрекингом.
    """
    def __init__(self, semester_id: int, max_iterations: int = 500000, 
                 max_lessons_per_day: int = 5):
        
        self.semester_id = semester_id
        self.max_iterations = max_iterations
        self.max_lessons_per_day = max_lessons_per_day
        
        self.iterations = 0
        self.solution = []
        self.max_progress_index = 0
        
        self.teacher_busy = defaultdict(set)
        self.room_busy = defaultdict(set)
        self.group_busy = defaultdict(set)
        
        self.group_daily_count = defaultdict(int)
        self.task_weekly_count = defaultdict(int)
        
        self.group_subject_type_last_day_index = {} 

        self._load_data()
        
        super().__init__(self.db_teachers, self.db_rooms, self.db_groups)

    def _load_data(self):
        """Загрузка данных из БД и подготовка кэшей"""
        self.semester = Semester.query.get(self.semester_id)
        if not self.semester:
            raise ValueError("Семестр не найден")
            
        self.weeks = self.semester.weeks.order_by(Week.week_number).all()
        self.week_ids = [w.id for w in self.weeks]
        self.week_id_to_index = {wid: i for i, wid in enumerate(self.week_ids)}
        
        self.db_teachers = Teacher.query.filter_by(is_active=True).all()
        self.db_rooms = Room.query.filter_by(is_active=True).all()
        self.db_groups = Group.query.filter_by(is_active=True).all()
        self.lesson_types = {lt.id: lt for lt in LessonType.query.all()}
        
        self.subject_teachers = defaultdict(list)
        for t in self.db_teachers:
            for s in t.subjects:
                self.subject_teachers[s.id].append(t.id)

        # Загружаем ограничения из БД
        self.constraints = LessonTypeConstraint.query.all()
        # Преобразуем в удобный для поиска словарь: (type_from_id, type_to_id) -> constraint_object
        self.constraints_map = {(c.type_from_id, c.type_to_id): c for c in self.constraints}
        print(f"   Загружено ограничений между типами: {len(self.constraints)}")

    def generate(self) -> Dict:
        start_time = time.time()
        print(f"🚀 CSP: Старт генерации для {len(self.db_groups)} групп на {len(self.weeks)} недель")
        
        self.assignments_to_schedule = self._create_assignments()
        print(f"📊 Всего занятий для распределения: {len(self.assignments_to_schedule)}")
        
        if not self.assignments_to_schedule:
            return {'lessons': [], 'fitness': 1.0, 'conflicts': [], 'time': 0}

        success = self._backtrack(0)
        duration = time.time() - start_time
        
        if success:
            result_lessons = [{'week_id': item['slot'].week_id, 'day_of_week': item['slot'].day, 'time_slot': item['slot'].time,
                               'group_id': item['task'].group_id, 'subject_id': item['task'].subject_id,
                               'teacher_id': item['teacher_id'], 'room_id': item['room_id'],
                               'lesson_type_id': item['task'].lesson_type_id} for item in self.solution]
            print(f"✅ CSP: Успех! За {duration:.2f}с")
            return {'lessons': result_lessons, 'fitness': 1.0, 'conflicts': [], 'time': duration, 'iterations': self.iterations}
        else:
            max_progress = (self.max_progress_index / len(self.assignments_to_schedule)) if self.assignments_to_schedule else 0
            print(f"❌ CSP: Не удалось найти полное решение. Максимальный прогресс: {max_progress*100:.1f}%.")
            return {'lessons': [], 'fitness': max_progress, 'conflicts': [{'type': 'no_solution', 'message': 'Не удалось найти полное решение'}], 'time': duration, 'iterations': self.iterations}

    def _create_assignments(self) -> List[LessonTask]:
        task_groups = defaultdict(list)
        for group in self.db_groups:
            for gs in group.group_subjects:
                for load in gs.lesson_type_loads:
                    if load.hours_per_week > 0:
                        total_hours = load.hours_per_week * len(self.weeks)
                        task = LessonTask(group.id, gs.subject_id, load.lesson_type_id, load.hours_per_week)
                        task_groups[(group.id, gs.subject_id, load.lesson_type_id)].extend([task] * total_hours)
        sorted_keys = sorted(task_groups.keys(), key=lambda k: (-task_groups[k][0].hours_per_week, len(self.subject_teachers.get(k[1], []))))
        final_tasks = []
        for key in sorted_keys:
            random.shuffle(task_groups[key])
            final_tasks.extend(task_groups[key])
        return final_tasks

    def _get_domain(self, task: LessonTask) -> Generator[Tuple[TimeSlot, int, int], None, None]:
        suitable_teachers = self.subject_teachers.get(task.subject_id, [])
        group_obj = self.groups.get(task.group_id)
        if not group_obj: return
        l_type = self.lesson_types.get(task.lesson_type_id)
        req_special = l_type.requires_special_room if l_type else False
        available_rooms = [r for r in self.rooms.values() if r.capacity >= group_obj.student_count]
        suitable_rooms = [r for r in available_rooms if r.is_special] if req_special else ([self.rooms.get(group_obj.default_room_id)] if group_obj.default_room_id and not self.rooms.get(group_obj.default_room_id).is_special and self.rooms.get(group_obj.default_room_id) in available_rooms else [r for r in available_rooms if not r.is_special])
        if not suitable_teachers or not suitable_rooms: return

        shuffled_weeks = list(self.week_ids); random.shuffle(shuffled_weeks)
        for week_id in shuffled_weeks:
            weekly_key = (task.group_id, task.subject_id, task.lesson_type_id, week_id)
            if self.task_weekly_count.get(weekly_key, 0) >= task.hours_per_week: continue
            days = list(range(self.days_per_week)); random.shuffle(days)
            for day in days:
                if self.group_daily_count.get((task.group_id, week_id, day), 0) >= self.max_lessons_per_day: continue
                
                # --- УМНАЯ ПРОВЕРКА ОГРАНИЧЕНИЙ ---
                day_abs_idx = self.week_id_to_index.get(week_id, 0) * self.days_per_week + day
                conflict_found = False
                for (g_id, s_id, lt_id), last_idx in self.group_subject_type_last_day_index.items():
                    if g_id != task.group_id or s_id != task.subject_id: continue
                    
                    # Проверяем оба направления: (уже стоит -> новое) и (новое -> уже стоит)
                    constraint_forward = self.constraints_map.get((lt_id, task.lesson_type_id))
                    constraint_backward = self.constraints_map.get((task.lesson_type_id, lt_id))
                    
                    constraint = constraint_forward or constraint_backward
                    
                    if constraint:
                        days_diff = abs(day_abs_idx - last_idx)
                        if days_diff < constraint.min_days_between:
                            conflict_found = True
                            break
                        if constraint.max_days_between and days_diff > constraint.max_days_between:
                            conflict_found = True
                            break
                if conflict_found: continue
                # --- КОНЕЦ ПРОВЕРКИ ---

                times = list(range(self.slots_per_day)); random.shuffle(times)
                for time_slot in times:
                    slot = TimeSlot(week_id, day, time_slot)
                    if slot in self.group_busy[task.group_id]: continue
                    for t_id in random.sample(suitable_teachers, len(suitable_teachers)):
                        if slot in self.teacher_busy[t_id]: continue
                        for r in random.sample(suitable_rooms, len(suitable_rooms)):
                            if slot in self.room_busy[r.id]: continue
                            yield (slot, t_id, r.id)

    def _assign(self, task, slot, t_id, r_id):
        key = (task.group_id, task.subject_id, task.lesson_type_id)
        prev_day = self.group_subject_type_last_day_index.get(key)
        self.solution.append({'task': task, 'slot': slot, 'teacher_id': t_id, 'room_id': r_id, 'prev_last_day': prev_day})
        self.group_busy[task.group_id].add(slot); self.teacher_busy[t_id].add(slot); self.room_busy[r_id].add(slot)
        self.group_daily_count[(task.group_id, slot.week_id, slot.day)] += 1
        self.task_weekly_count[(task.group_id, task.subject_id, task.lesson_type_id, slot.week_id)] += 1
        day_idx = self.week_id_to_index.get(slot.week_id, 0) * self.days_per_week + slot.day
        self.group_subject_type_last_day_index[key] = day_idx

    def _unassign(self):
        last = self.solution.pop()
        task, slot, t_id, r_id = last['task'], last['slot'], last['teacher_id'], last['room_id']
        self.group_busy[task.group_id].remove(slot); self.teacher_busy[t_id].remove(slot); self.room_busy[r_id].remove(slot)
        self.group_daily_count[(task.group_id, slot.week_id, slot.day)] -= 1
        self.task_weekly_count[(task.group_id, task.subject_id, task.lesson_type_id, slot.week_id)] -= 1
        key = (task.group_id, task.subject_id, task.lesson_type_id)
        if last['prev_last_day'] is not None: self.group_subject_type_last_day_index[key] = last['prev_last_day']
        elif key in self.group_subject_type_last_day_index: del self.group_subject_type_last_day_index[key]

    def _backtrack(self, idx: int) -> bool:
        self.iterations += 1
        self.max_progress_index = max(self.max_progress_index, idx)
        if self.iterations > self.max_iterations: return False
        if idx >= len(self.assignments_to_schedule): return True
        if self.iterations > 0 and self.iterations % 50000 == 0:
            progress = (self.max_progress_index / len(self.assignments_to_schedule)) * 100
            print(f"   ... итерация {self.iterations}, макс. прогресс {progress:.1f}%")
        task = self.assignments_to_schedule[idx]
        for slot, t_id, r_id in self._get_domain(task):
            self._assign(task, slot, t_id, r_id)
            if self._backtrack(idx + 1): return True
            self._unassign()
        if idx == self.max_progress_index:
            group = self.groups.get(task.group_id); subject = Subject.query.get(task.subject_id); l_type = self.lesson_types.get(task.lesson_type_id)
            if group and subject and l_type: print(f"-> ❌ Не удалось найти место для задачи {idx+1}/{len(self.assignments_to_schedule)}: Группа '{group.name}', Предмет '{subject.name}', Тип '{l_type.name}'")
        return False