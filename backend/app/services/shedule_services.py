from app.schedulers.genetic import GeneticScheduler
from app.models import Lesson
from typing import List, Dict
from collections import defaultdict

class ScheduleService:
    """Сервис для работы с расписаниями"""
    
    def generate_genetic(self, teachers, rooms, groups, **kwargs):
        """Генерация расписания генетическим алгоритмом"""
        
        scheduler = GeneticScheduler(
            teachers=teachers,
            rooms=rooms,
            groups=groups,
            population_size=kwargs.get('population_size', 100),
            generations=kwargs.get('generations', 500),
            mutation_rate=kwargs.get('mutation_rate', 0.01)
        )
        
        best_chromosome = scheduler.evolve()
        
        # Конвертируем в формат для сохранения
        lessons = []
        for gene in best_chromosome.genes:
            lessons.append({
                'group_id': gene.group_id,
                'subject_id': gene.subject_id,
                'teacher_id': gene.teacher_id,
                'room_id': gene.room_id,
                'day': gene.day,
                'time_slot': gene.time_slot
            })
        
        # Проверяем конфликты
        conflicts = self._check_chromosome_conflicts(best_chromosome)
        
        return {
            'lessons': lessons,
            'fitness': best_chromosome.fitness,
            'conflicts': conflicts
        }
    
    def _check_chromosome_conflicts(self, chromosome):
        """Проверка конфликтов в хромосоме"""
        conflicts = []
        
        for i, gene1 in enumerate(chromosome.genes):
            for gene2 in chromosome.genes[i+1:]:
                if gene1.day == gene2.day and gene1.time_slot == gene2.time_slot:
                    if gene1.teacher_id == gene2.teacher_id:
                        conflicts.append(f"Конфликт преподавателя ID {gene1.teacher_id}")
                    
                    if gene1.room_id == gene2.room_id:
                        conflicts.append(f"Конфликт аудитории ID {gene1.room_id}")
                    
                    if gene1.group_id == gene2.group_id:
                        conflicts.append(f"Конфликт группы ID {gene1.group_id}")
        
        return conflicts
    
    def check_conflicts(self, schedule):
        """Проверка конфликтов в сохраненном расписании"""
        conflicts = []
        lessons = schedule.lessons
        
        # Группируем по времени
        time_slots = defaultdict(list)
        for lesson in lessons:
            key = (lesson.day, lesson.time_slot)
            time_slots[key].append(lesson)
        
        # Проверяем каждый временной слот
        for (day, time_slot), slot_lessons in time_slots.items():
            if len(slot_lessons) > 1:
                # Проверяем конфликты
                teachers = [l.teacher_id for l in slot_lessons]
                rooms = [l.room_id for l in slot_lessons]
                groups = [l.group_id for l in slot_lessons]
                
                if len(teachers) != len(set(teachers)):
                    conflicts.append({
                        'type': 'teacher',
                        'day': day,
                        'time_slot': time_slot,
                        'message': 'Преподаватель в двух местах одновременно'
                    })
                
                if len(rooms) != len(set(rooms)):
                    conflicts.append({
                        'type': 'room',
                        'day': day,
                        'time_slot': time_slot,
                        'message': 'Аудитория занята дважды'
                    })
                
                if len(groups) != len(set(groups)):
                    conflicts.append({
                        'type': 'group',
                        'day': day,
                        'time_slot': time_slot,
                        'message': 'Группа в двух местах одновременно'
                    })
        
        return conflicts