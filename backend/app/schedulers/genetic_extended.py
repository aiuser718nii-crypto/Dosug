"""
Расширенный генетический алгоритм для семестрового планирования

Учитывает:
- Недели семестра
- Типы занятий (лекции, семинары, лабораторные и т.д.)
- Временные ограничения между типами занятий
- Стандартные аудитории для групп
- Специальные требования к аудиториям
"""

import random
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import timedelta
import copy

from app.models import Teacher, Room, Group, Subject
from app.models import (
    Semester, Week, LessonType, LessonTypeEnum,
    LessonTypeConstraint, LessonExtended
)


class ScheduleGene:
    """
    Ген расписания - одно занятие
    """
    def __init__(self, group_id, subject_id, lesson_type_id, teacher_id, 
                 room_id, week_id, day, time_slot):
        self.group_id = group_id
        self.subject_id = subject_id
        self.lesson_type_id = lesson_type_id
        self.teacher_id = teacher_id
        self.room_id = room_id
        self.week_id = week_id
        self.day = day  # 0-4 (Пн-Пт)
        self.time_slot = time_slot  # 0-6
    
    def clone(self):
        """Клонировать ген"""
        return ScheduleGene(
            self.group_id, self.subject_id, self.lesson_type_id,
            self.teacher_id, self.room_id, self.week_id,
            self.day, self.time_slot
        )
    
    def to_dict(self):
        """Конвертация в словарь"""
        return {
            'group_id': self.group_id,
            'subject_id': self.subject_id,
            'lesson_type_id': self.lesson_type_id,
            'teacher_id': self.teacher_id,
            'room_id': self.room_id,
            'week_id': self.week_id,
            'day': self.day,
            'time_slot': self.time_slot
        }


class Chromosome:
    """
    Хромосома - полное расписание на семестр
    """
    def __init__(self, genes: List[ScheduleGene] = None):
        self.genes = genes or []
        self.fitness = 0.0
        self.conflicts = []
    
    def clone(self):
        """Клонировать хромосому"""
        return Chromosome([gene.clone() for gene in self.genes])
    
    def calculate_fitness(self, constraints_data):
        """Вычислить фитнес-функцию"""
        fitness = 1.0
        self.conflicts = []
        
        # Подготовка данных для быстрой проверки
        time_slots = defaultdict(list)  # {(week, day, time): [genes]}
        teacher_schedule = defaultdict(list)  # {(teacher_id, week, day, time): [genes]}
        room_schedule = defaultdict(list)  # {(room_id, week, day, time): [genes]}
        group_schedule = defaultdict(list)  # {(group_id, week, day, time): [genes]}
        subject_lessons = defaultdict(list)  # {(group_id, subject_id): [(week_id, day, gene)]}
        
        for gene in self.genes:
            key = (gene.week_id, gene.day, gene.time_slot)
            time_slots[key].append(gene)
            
            teacher_key = (gene.teacher_id, gene.week_id, gene.day, gene.time_slot)
            teacher_schedule[teacher_key].append(gene)
            
            room_key = (gene.room_id, gene.week_id, gene.day, gene.time_slot)
            room_schedule[room_key].append(gene)
            
            group_key = (gene.group_id, gene.week_id, gene.day, gene.time_slot)
            group_schedule[group_key].append(gene)
            
            subject_key = (gene.group_id, gene.subject_id)
            subject_lessons[subject_key].append((gene.week_id, gene.day, gene))
        
        # 1. Конфликты преподавателей (жёсткое ограничение)
        for key, genes_list in teacher_schedule.items():
            if len(genes_list) > 1:
                fitness -= 0.3
                self.conflicts.append({
                    'type': 'teacher_conflict',
                    'severity': 'hard',
                    'genes': genes_list
                })
        
        # 2. Конфликты аудиторий (жёсткое ограничение)
        for key, genes_list in room_schedule.items():
            if len(genes_list) > 1:
                fitness -= 0.3
                self.conflicts.append({
                    'type': 'room_conflict',
                    'severity': 'hard',
                    'genes': genes_list
                })
        
        # 3. Конфликты групп (жёсткое ограничение)
        for key, genes_list in group_schedule.items():
            if len(genes_list) > 1:
                fitness -= 0.3
                self.conflicts.append({
                    'type': 'group_conflict',
                    'severity': 'hard',
                    'genes': genes_list
                })
        
        # 4. Временные ограничения между типами занятий
        fitness -= self._check_lesson_type_constraints(
            subject_lessons, 
            constraints_data['lesson_type_constraints'],
            constraints_data['weeks_map']
        )
        
        # 5. Окна в расписании (мягкое ограничение)
        fitness -= self._calculate_gaps_penalty(time_slots) * 0.05
        
        # 6. Распределение нагрузки по дням (мягкое ограничение)
        fitness -= self._calculate_daily_load_penalty(group_schedule) * 0.03
        
        # 7. Проверка соответствия аудиторий требованиям
        fitness -= self._check_room_requirements(constraints_data) * 0.1
        
        self.fitness = max(0.0, min(1.0, fitness))
        return self.fitness
    
    def _check_lesson_type_constraints(self, subject_lessons, constraints, weeks_map):
        """
        Проверка временных ограничений между типами занятий
        
        Например: между лекцией и семинаром должно пройти минимум 3 дня
        """
        penalty = 0.0
        
        for (group_id, subject_id), lessons in subject_lessons.items():
            # Сортируем по неделям и дням
            sorted_lessons = sorted(lessons, key=lambda x: (weeks_map[x[0]], x[1]))
            
            for i in range(len(sorted_lessons) - 1):
                week1_id, day1, gene1 = sorted_lessons[i]
                week2_id, day2, gene2 = sorted_lessons[i + 1]
                
                # Проверяем ограничения для пары типов занятий
                for constraint in constraints:
                    if (constraint['type_from_id'] == gene1.lesson_type_id and
                        constraint['type_to_id'] == gene2.lesson_type_id):
                        
                        # Вычисляем разницу в днях
                        week1_start = weeks_map[week1_id]
                        week2_start = weeks_map[week2_id]
                        
                        date1 = week1_start + timedelta(days=day1)
                        date2 = week2_start + timedelta(days=day2)
                        days_diff = (date2 - date1).days
                        
                        # Проверяем минимальное расстояние
                        if days_diff < constraint['min_days']:
                            penalty += 0.2
                            self.conflicts.append({
                                'type': 'lesson_type_constraint',
                                'severity': 'medium',
                                'message': f"Между занятиями прошло {days_diff} дней, требуется минимум {constraint['min_days']}",
                                'genes': [gene1, gene2]
                            })
                        
                        # Проверяем максимальное расстояние
                        if constraint['max_days'] and days_diff > constraint['max_days']:
                            penalty += 0.1
        
        return penalty
    
    def _calculate_gaps_penalty(self, time_slots):
        """Штраф за окна в расписании"""
        gaps_count = 0
        
        for (week, day, time), genes in time_slots.items():
            # Проверяем, есть ли окна для каждой группы
            groups_at_time = {gene.group_id for gene in genes}
            
            for group_id in groups_at_time:
                # Проверяем следующий слот
                next_key = (week, day, time + 1)
                if next_key in time_slots:
                    next_groups = {gene.group_id for gene in time_slots[next_key]}
                    if group_id not in next_groups and time < 6:
                        # Проверяем, есть ли занятия позже в этот день
                        for future_time in range(time + 2, 7):
                            future_key = (week, day, future_time)
                            if future_key in time_slots:
                                future_groups = {gene.group_id for gene in time_slots[future_key]}
                                if group_id in future_groups:
                                    gaps_count += 1
                                    break
        
        return gaps_count
    
    def _calculate_daily_load_penalty(self, group_schedule):
        """Штраф за неравномерное распределение нагрузки по дням"""
        penalty = 0.0
        
        daily_loads = defaultdict(int)
        for (group_id, week, day, time), genes in group_schedule.items():
            daily_loads[(group_id, week, day)] += len(genes)
        
        # Идеальная нагрузка - 3-4 пары в день
        for load in daily_loads.values():
            if load > 5:
                penalty += (load - 5) * 0.5
            elif load < 2:
                penalty += (2 - load) * 0.3
        
        return penalty
    
    def _check_room_requirements(self, constraints_data):
        """Проверка соответствия аудиторий требованиям"""
        penalty = 0.0
        
        for gene in self.genes:
            lesson_type = constraints_data['lesson_types'].get(gene.lesson_type_id)
            room = constraints_data['rooms'].get(gene.room_id)
            group = constraints_data['groups'].get(gene.group_id)
            
            if not all([lesson_type, room, group]):
                continue
            
            # Проверка вместимости
            if room['capacity'] < group['student_count']:
                penalty += 0.2
            
            # Проверка специальных требований
            if lesson_type.get('requires_special_room'):
                # Здесь должна быть логика проверки специального оборудования
                pass
        
        return penalty


class GeneticSchedulerExtended:
    """
    Расширенный генетический алгоритм для семестрового планирования
    """
    
    def __init__(self, semester_id: int, population_size: int = 100, 
                 generations: int = 500, mutation_rate: float = 0.1):
        self.semester_id = semester_id
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        # Загрузка данных
        self.semester = None
        self.weeks = []
        self.groups = []
        self.teachers = []
        self.rooms = []
        self.lesson_types = {}
        self.constraints = []
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка всех необходимых данных из БД"""
        from app._init_ import db
        
        print("📚 Загрузка данных для генерации расписания...")
        
        # Семестр и недели
        self.semester = Semester.query.get(self.semester_id)
        if not self.semester:
            raise ValueError(f"Семестр с ID {self.semester_id} не найден")
        
        self.weeks = self.semester.weeks.all()
        print(f"   ✅ Недель: {len(self.weeks)}")
        
        # Группы и их предметы
        self.groups = Group.query.filter_by(is_active=True).all()
        print(f"   ✅ Групп: {len(self.groups)}")
        
        # Преподаватели
        self.teachers = Teacher.query.filter_by(is_active=True).all()
        print(f"   ✅ Преподавателей: {len(self.teachers)}")
        
        # Аудитории
        self.rooms = Room.query.filter_by(is_active=True).all()
        print(f"   ✅ Аудиторий: {len(self.rooms)}")
        
        # Типы занятий
        lesson_types_list = LessonType.query.all()
        self.lesson_types = {lt.id: lt for lt in lesson_types_list}
        print(f"   ✅ Типов занятий: {len(self.lesson_types)}")
        
        # Ограничения между типами
        self.constraints = LessonTypeConstraint.query.all()
        print(f"   ✅ Ограничений: {len(self.constraints)}")
        
        # Проверка данных
        self._validate_data()
    
    def _validate_data(self):
        """Проверка корректности данных"""
        errors = []
        
        if not self.weeks:
            errors.append("Нет недель в семестре")
        
        if not self.groups:
            errors.append("Нет активных групп")
        
        if not self.teachers:
            errors.append("Нет активных преподавателей")
        
        if not self.rooms:
            errors.append("Нет активных аудиторий")
        
        # Проверка покрытия предметов преподавателями
        for group in self.groups:
            for gs in group.group_subjects.all():
                if not gs.subject:
                    continue
                
                can_teach = any(
                    gs.subject in teacher.subjects.all()
                    for teacher in self.teachers
                )
                
                if not can_teach:
                    errors.append(
                        f"Группа '{group.name}': предмет '{gs.subject.name}' - нет преподавателей"
                    )
        
        if errors:
            print("\n❌ ОШИБКИ ВАЛИДАЦИИ:")
            for error in errors:
                print(f"   • {error}")
            raise ValueError("Данные некорректны для генерации расписания")
    
    def _create_random_chromosome(self) -> Chromosome:
        """Создание случайной хромосомы (расписания)"""
        genes = []
        
        for group in self.groups:
            for gs in group.group_subjects.all():
                if not gs.subject:
                    continue
                
                # Определяем типы занятий и их количество
                lesson_types_hours = {
                    'lecture': gs.lecture_hours or 0,
                    'seminar': gs.seminar_hours or 0,
                    'lab': gs.lab_hours or 0,
                    'practice': gs.practice_hours or 0,
                }
                
                # Если не указаны конкретные типы, используем общее количество часов
                total_specific = sum(lesson_types_hours.values())
                if total_specific == 0 and gs.hours_per_week > 0:
                    lesson_types_hours['lecture'] = gs.hours_per_week
                
                # Создаём гены для каждого типа занятий
                for lesson_type_name, hours in lesson_types_hours.items():
                    if hours == 0:
                        continue
                    
                    # Находим тип занятия
                    lesson_type = next(
                        (lt for lt in self.lesson_types.values() 
                         if lt.code.value == lesson_type_name),
                        None
                    )
                    
                    if not lesson_type:
                        continue
                    
                    # Находим подходящих преподавателей
                    suitable_teachers = [
                        t for t in self.teachers
                        if gs.subject in t.subjects.all()
                    ]
                    
                    if not suitable_teachers:
                        continue
                    
                    # Создаём занятия
                    lessons_count = hours  # Упрощение: 1 час = 1 занятие
                    weeks_to_use = random.sample(self.weeks, min(lessons_count, len(self.weeks)))
                    
                    for week in weeks_to_use:
                        teacher = random.choice(suitable_teachers)
                        
                        # Выбор аудитории
                        if group.default_room and not lesson_type.requires_special_room:
                            room = group.default_room
                        else:
                            suitable_rooms = [
                                r for r in self.rooms
                                if r.capacity >= group.student_count
                            ]
                            room = random.choice(suitable_rooms) if suitable_rooms else self.rooms[0]
                        
                        # Случайное время
                        day = random.randint(0, 4)  # Пн-Пт
                        time_slot = random.randint(0, 6)
                        
                        gene = ScheduleGene(
                            group_id=group.id,
                            subject_id=gs.subject_id,
                            lesson_type_id=lesson_type.id,
                            teacher_id=teacher.id,
                            room_id=room.id,
                            week_id=week.id,
                            day=day,
                            time_slot=time_slot
                        )
                        
                        genes.append(gene)
        
        return Chromosome(genes)
    
    def _selection(self, population: List[Chromosome]) -> List[Chromosome]:
        """Отбор лучших особей (турнирный отбор)"""
        tournament_size = 5
        selected = []
        
        for _ in range(len(population)):
            tournament = random.sample(population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Скрещивание двух хромосом (одноточечное)"""
        if len(parent1.genes) == 0 or len(parent2.genes) == 0:
            return parent1.clone(), parent2.clone()
        
        point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        
        child1_genes = parent1.genes[:point] + parent2.genes[point:]
        child2_genes = parent2.genes[:point] + parent1.genes[point:]
        
        return Chromosome(child1_genes), Chromosome(child2_genes)
    
    def _mutate(self, chromosome: Chromosome):
        """Мутация хромосомы"""
        for gene in chromosome.genes:
            if random.random() < self.mutation_rate:
                mutation_type = random.choice(['time', 'teacher', 'room', 'week'])
                
                if mutation_type == 'time':
                    gene.day = random.randint(0, 4)
                    gene.time_slot = random.randint(0, 6)
                
                elif mutation_type == 'teacher':
                    # Находим подходящих преподавателей
                    subject = Subject.query.get(gene.subject_id)
                    if subject:
                        suitable_teachers = [
                            t for t in self.teachers
                            if subject in t.subjects.all()
                        ]
                        if suitable_teachers:
                            gene.teacher_id = random.choice(suitable_teachers).id
                
                elif mutation_type == 'room':
                    gene.room_id = random.choice(self.rooms).id
                
                elif mutation_type == 'week':
                    gene.week_id = random.choice(self.weeks).id
    
    def generate(self) -> Dict:
        """Основной метод генерации расписания"""
        print("\n" + "="*70)
        print("🧬 ГЕНЕТИЧЕСКИЙ АЛГОРИТМ - СЕМЕСТРОВОЕ ПЛАНИРОВАНИЕ")
        print("="*70)
        print(f"📊 Параметры:")
        print(f"   • Размер популяции: {self.population_size}")
        print(f"   • Поколений: {self.generations}")
        print(f"   • Вероятность мутации: {self.mutation_rate}")
        print(f"   • Семестр: {self.semester.type.value}")
        print(f"   • Недель: {len(self.weeks)}")
        print("="*70)
        
        # Подготовка данных для фитнес-функции
        constraints_data = self._prepare_constraints_data()
        
        # Создание начальной популяции
        print("\n🌱 Создание начальной популяции...")
        population = [self._create_random_chromosome() for _ in range(self.population_size)]
        
        # Оценка начальной популяции
        for chromosome in population:
            chromosome.calculate_fitness(constraints_data)
        
        best_chromosome = max(population, key=lambda x: x.fitness)
        print(f"   Начальный лучший фитнес: {best_chromosome.fitness:.2f}")
        
        # Эволюция
        for generation in range(self.generations):
            # Отбор
            selected = self._selection(population)
            
            # Скрещивание
            offspring = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    child1, child2 = self._crossover(selected[i], selected[i+1])
                    offspring.extend([child1, child2])
            
            # Мутация
            for chromosome in offspring:
                self._mutate(chromosome)
            
            # Оценка потомков
            for chromosome in offspring:
                chromosome.calculate_fitness(constraints_data)
            
            # Новая популяция (элитизм: сохраняем 10% лучших)
            elite_size = self.population_size // 10
            population.sort(key=lambda x: x.fitness, reverse=True)
            population = population[:elite_size] + offspring[:self.population_size - elite_size]
            
            # Статистика
            best_chromosome = max(population, key=lambda x: x.fitness)
            avg_fitness = sum(c.fitness for c in population) / len(population)
            
            if generation % 50 == 0 or generation == self.generations - 1:
                print(f"🧬 Поколение {generation:4d}: "
                      f"Лучший = {best_chromosome.fitness:8.2f}, "
                      f"Средний = {avg_fitness:8.2f}")
        
        # Результат
        print("\n" + "="*70)
        print("✅ ГЕНЕТИЧЕСКИЙ АЛГОРИТМ - ЗАВЕРШЕН")
        print("="*70)
        print(f"📊 Итоговые результаты:")
        print(f"   • Занятий: {len(best_chromosome.genes)}")
        print(f"   • Конфликтов: {len(best_chromosome.conflicts)}")
        print(f"   • Фитнес: {best_chromosome.fitness:.2f}")
        print("="*70)
        
        return {
            'lessons': [gene.to_dict() for gene in best_chromosome.genes],
            'fitness': best_chromosome.fitness,
            'conflicts': best_chromosome.conflicts
        }
    
    def _prepare_constraints_data(self) -> Dict:
        """Подготовка данных для быстрого доступа в фитнес-функции"""
        weeks_map = {week.id: week.start_date for week in self.weeks}
        
        constraints_list = []
        for constraint in self.constraints:
            constraints_list.append({
                'type_from_id': constraint.type_from_id,
                'type_to_id': constraint.type_to_id,
                'min_days': constraint.min_days_between,
                'max_days': constraint.max_days_between
            })
        
        return {
            'weeks_map': weeks_map,
            'lesson_type_constraints': constraints_list,
            'lesson_types': {lt.id: lt.__dict__ for lt in self.lesson_types.values()},
            'rooms': {r.id: {'capacity': r.capacity} for r in self.rooms},
            'groups': {g.id: {'student_count': g.student_count} for g in self.groups}
        }