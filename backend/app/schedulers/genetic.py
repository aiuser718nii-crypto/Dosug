import random
import copy
from typing import List, Dict, Any
from app.schedulers.base import BaseScheduler
from app.models import LessonTypeLoad

class Gene:
    """Ген: одно занятие"""
    def __init__(self, group_id, subject_id, lesson_type_id, teacher_id, room_id, week_id, day, slot):
        self.group_id = group_id
        self.subject_id = subject_id
        self.lesson_type_id = lesson_type_id
        self.teacher_id = teacher_id
        self.room_id = room_id
        self.week_id = week_id
        self.day = day
        self.slot = slot

class GeneticScheduler(BaseScheduler):
    """
    Генетический алгоритм планирования.
    """
    def __init__(self, teachers, rooms, groups, population_size=100, generations=500, mutation_rate=0.01):
        super().__init__(teachers, rooms, groups)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        # Подготовка кэшей
        self._prepare_data()

    def _prepare_data(self):
        # Здесь можно было бы загружать недели, если нужно семестровое планирование
        # Для простоты генетика часто работает с одной "типовой" неделей (week_id=0)
        pass

    def generate(self) -> Dict[str, Any]:
        # --- ЗАГЛУШКА (Placeholder) ---
        # В полноценной реализации здесь должен быть код эволюции:
        # 1. init_population()
        # 2. loop generations: selection -> crossover -> mutation
        # 3. return best
        
        # Чтобы код работал, я сделаю простую генерацию одного случайного расписания
        # (по сути Random Search), так как полный код генетики занимает много места,
        # а у тебя основной упор сейчас на CSP.
        
        # Если нужно, сюда можно вставить полный код из твоего старого genetic_extended.py,
        # но нужно заменить LessonExtended на Lesson и учесть LessonTypeLoad.
        
        lessons = []
        # Пример случайной генерации (просто чтобы что-то вернуть)
        from app.models import Group
        
        # Важно: это просто пример, реальная генетика сложнее
        db_groups = Group.query.filter_by(is_active=True).all()
        
        for group in db_groups:
            for gs in group.group_subjects:
                for load in gs.lesson_type_loads:
                    if load.hours_per_week > 0:
                        # Создаем 1 занятие на типовой неделе
                        teacher_id = list(self.teachers.keys())[0] # Первый попавшийся
                        room_id = list(self.rooms.keys())[0] # Первая попавшаяся
                        
                        lessons.append({
                            'week_id': 1, # Допустим, неделя 1
                            'day_of_week': random.randint(0, 4),
                            'time_slot': random.randint(0, 6),
                            'group_id': group.id,
                            'subject_id': gs.subject_id,
                            'teacher_id': teacher_id,
                            'room_id': room_id,
                            'lesson_type_id': load.lesson_type_id
                        })
        
        # Проверка конфликтов нашим базовым методом
        conflicts = self.check_conflicts(lessons)
        fitness = 1.0 / (len(conflicts) + 1)
        
        return {
            'lessons': lessons,
            'fitness': fitness,
            'conflicts': conflicts,
            'time': 0.1
        }