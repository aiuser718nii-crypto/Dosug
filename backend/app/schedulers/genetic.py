"""
Генетический алгоритм для генерации расписания
"""

import random
import copy
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
from .base import BaseScheduler

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  NumPy не установлен, используется простая версия генетического алгоритма")


@dataclass
class Gene:
    """Ген - одно занятие в расписании"""
    group_id: int
    subject_id: int
    teacher_id: int
    room_id: int
    day: int
    time_slot: int
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            'group_id': self.group_id,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'room_id': self.room_id,
            'day': self.day,
            'time_slot': self.time_slot
        }


class Chromosome:
    """Хромосома - полное расписание"""
    
    def __init__(self, genes: List[Gene]):
        self.genes = genes
        self.fitness = 0.0
    
    def __len__(self):
        return len(self.genes)
    
    def copy(self):
        """Создание копии хромосомы"""
        return Chromosome([copy.deepcopy(g) for g in self.genes])


class GeneticScheduler(BaseScheduler):
    """Генетический алгоритм для составления расписания"""
    
    def __init__(self, teachers: List, rooms: List, groups: List,
                 population_size: int = 100,
                 generations: int = 500,
                 mutation_rate: float = 0.01,
                 crossover_rate: float = 0.7,
                 elite_size: int = 10):
        """
        Инициализация генетического алгоритма
        
        Args:
            teachers: Список преподавателей
            rooms: Список аудиторий
            groups: Список групп
            population_size: Размер популяции
            generations: Количество поколений
            mutation_rate: Вероятность мутации
            crossover_rate: Вероятность кроссовера
            elite_size: Размер элиты (лучшие особи)
        """
        super().__init__(teachers, rooms, groups)
        
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        # Веса для фитнес-функции
        self.weights = {
            'hard_conflicts': -1000,    # Жесткие конфликты (критично)
            'teacher_gaps': -10,        # Окна у преподавателей
            'student_gaps': -15,        # Окна у студентов
            'late_classes': -8,         # Поздние пары
            'early_classes': -3,        # Ранние пары
            'room_efficiency': -5,      # Неэффективное использование аудиторий
            'balanced_days': 10,        # Равномерность распределения
            'teacher_preferences': 20,  # Соответствие предпочтениям
        }
    
    def generate(self) -> Dict[str, Any]:
        """
        Основной метод генерации расписания
        
        Returns:
            Dict с результатами
        """
        print(f"\n{'='*70}")
        print(f"🧬 ГЕНЕТИЧЕСКИЙ АЛГОРИТМ - СТАРТ")
        print(f"{'='*70}")
        print(f"⚙️  Параметры:")
        print(f"   • Размер популяции: {self.population_size}")
        print(f"   • Количество поколений: {self.generations}")
        print(f"   • Вероятность мутации: {self.mutation_rate}")
        print(f"   • Вероятность кроссовера: {self.crossover_rate}")
        print(f"   • Размер элиты: {self.elite_size}")
        print(f"{'='*70}\n")
        
        # Эволюция
        best_chromosome = self._evolve()
        
        # Конвертируем в формат для сохранения
        lessons = [gene.to_dict() for gene in best_chromosome.genes]
        
        # Проверяем конфликты
        conflicts = self.check_conflicts(lessons)
        
        # Статистика
        stats = self.calculate_statistics(lessons)
        
        print(f"\n{'='*70}")
        print(f"✅ ГЕНЕТИЧЕСКИЙ АЛГОРИТМ - ЗАВЕРШЕН")
        print(f"{'='*70}")
        print(f"📊 Итоговые результаты:")
        print(f"   • Занятий: {len(lessons)}")
        print(f"   • Конфликтов: {len(conflicts)}")
        print(f"   • Фитнес: {best_chromosome.fitness:.2f}")
        print(f"   • Окон (преподаватели): {stats['gaps']['teacher']}")
        print(f"   • Окон (студенты): {stats['gaps']['student']}")
        print(f"{'='*70}\n")
        
        return {
            'lessons': lessons,
            'fitness': best_chromosome.fitness,
            'conflicts': conflicts,
            'statistics': stats
        }
    
    def _evolve(self) -> Chromosome:
        """
        Основной цикл эволюции
        
        Returns:
            Лучшая хромосома
        """
        # Создаем начальную популяцию
        print("🌱 Создание начальной популяции...")
        population = self._generate_initial_population()
        
        # Оцениваем начальную популяцию
        for chromosome in population:
            self._calculate_fitness(chromosome)
        
        best_overall = max(population, key=lambda x: x.fitness)
        print(f"   Начальный лучший фитнес: {best_overall.fitness:.2f}")
        
        # Эволюция
        for generation in range(self.generations):
            # Селекция
            selected = self._selection(population)
            
            # Кроссовер и мутация
            next_generation = []
            
            for i in range(0, len(selected) - 1, 2):
                child1, child2 = self._crossover(selected[i], selected[i+1])
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                next_generation.extend([child1, child2])
            
            # Оценка новой популяции
            for chromosome in next_generation:
                self._calculate_fitness(chromosome)
            
            population = next_generation[:self.population_size]
            
            # Обновляем лучшее решение
            generation_best = max(population, key=lambda x: x.fitness)
            if generation_best.fitness > best_overall.fitness:
                best_overall = generation_best.copy()
            
            # Логирование прогресса
            if generation % 50 == 0 or generation == self.generations - 1:
                if NUMPY_AVAILABLE:
                    avg_fitness = np.mean([c.fitness for c in population])
                else:
                    avg_fitness = sum(c.fitness for c in population) / len(population)
                
                print(f"🧬 Поколение {generation:4d}: "
                      f"Лучший = {best_overall.fitness:8.2f}, "
                      f"Средний = {avg_fitness:8.2f}")
        
        return best_overall
    
    def _generate_initial_population(self) -> List[Chromosome]:
        """Создание начальной популяции"""
        from app.models import GroupSubject
        
        population = []
        
        for _ in range(self.population_size):
            genes = []
            
            # Для каждой группы
            for group_id in self.groups.keys():
                group_subjects = GroupSubject.query.filter_by(group_id=group_id).all()
                
                for gs in group_subjects:
                    subject = gs.subject
                    
                    # Находим подходящих учителей
                    suitable_teachers = [
                        t_id for t_id, t in self.teachers.items()
                        if subject in t.subjects
                    ]
                    
                    if not suitable_teachers:
                        continue
                    
                    # Создаем нужное количество занятий
                    for _ in range(gs.hours_per_week):
                        gene = Gene(
                            group_id=group_id,
                            subject_id=gs.subject_id,
                            teacher_id=random.choice(suitable_teachers),
                            room_id=random.choice(list(self.rooms.keys())),
                            day=random.randint(0, self.days - 1),
                            time_slot=random.randint(0, self.time_slots - 1)
                        )
                        genes.append(gene)
            
            population.append(Chromosome(genes))
        
        return population
    
    def _calculate_fitness(self, chromosome: Chromosome) -> float:
        """Расчет фитнес-функции"""
        score = 0.0
        
        # 1. Жесткие конфликты
        conflicts = self._count_hard_conflicts(chromosome)
        score += conflicts * self.weights['hard_conflicts']
        
        # 2. Окна в расписании
        teacher_gaps = self._count_entity_gaps(chromosome, 'teacher_id')
        score += teacher_gaps * self.weights['teacher_gaps']
        
        student_gaps = self._count_entity_gaps(chromosome, 'group_id')
        score += student_gaps * self.weights['student_gaps']
        
        # 3. Поздние пары
        late = sum(1 for g in chromosome.genes if g.time_slot >= 5)
        score += late * self.weights['late_classes']
        
        # 4. Ранние пары
        early = sum(1 for g in chromosome.genes if g.time_slot == 0)
        score += early * self.weights['early_classes']
        
        # 5. Равномерность распределения
        balance_score = self._calculate_balance(chromosome)
        score += balance_score * self.weights['balanced_days']
        
        chromosome.fitness = score
        return score
    
    def _count_hard_conflicts(self, chromosome: Chromosome) -> int:
        """Подсчет жестких конфликтов"""
        conflicts = 0
        
        for i, gene1 in enumerate(chromosome.genes):
            for gene2 in chromosome.genes[i+1:]:
                if gene1.day == gene2.day and gene1.time_slot == gene2.time_slot:
                    # Конфликт преподавателя
                    if gene1.teacher_id == gene2.teacher_id:
                        conflicts += 1
                    
                    # Конфликт аудитории
                    if gene1.room_id == gene2.room_id:
                        conflicts += 1
                    
                    # Конфликт группы
                    if gene1.group_id == gene2.group_id:
                        conflicts += 1
        
        return conflicts
    
    def _count_entity_gaps(self, chromosome: Chromosome, entity_attr: str) -> int:
        """Подсчет окон для сущности"""
        gaps = 0
        schedule = defaultdict(list)
        
        for gene in chromosome.genes:
            entity_id = getattr(gene, entity_attr)
            key = (entity_id, gene.day)
            schedule[key].append(gene.time_slot)
        
        for slots in schedule.values():
            if len(slots) > 1:
                slots_sorted = sorted(slots)
                gaps += (slots_sorted[-1] - slots_sorted[0] + 1 - len(slots))
        
        return gaps
    
    def _calculate_balance(self, chromosome: Chromosome) -> int:
        """Расчет равномерности распределения по дням"""
        group_day_load = defaultdict(lambda: [0] * self.days)
        
        for gene in chromosome.genes:
            group_day_load[gene.group_id][gene.day] += 1
        
        balance_score = 0
        for loads in group_day_load.values():
            if NUMPY_AVAILABLE:
                std_dev = np.std(loads)
            else:
                mean = sum(loads) / len(loads)
                variance = sum((x - mean) ** 2 for x in loads) / len(loads)
                std_dev = variance ** 0.5
            
            balance_score -= int(std_dev * 2)
        
        return balance_score
    
    def _selection(self, population: List[Chromosome]) -> List[Chromosome]:
        """Турнирная селекция"""
        selected = []
        
        # Сохраняем элиту
        elite = sorted(population, key=lambda x: x.fitness, reverse=True)[:self.elite_size]
        selected.extend([e.copy() for e in elite])
        
        # Турнирная селекция для остальных
        tournament_size = 5
        while len(selected) < self.population_size:
            tournament = random.sample(population, min(tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner.copy())
        
        return selected
    
    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Одноточечный кроссовер"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        min_len = min(len(parent1.genes), len(parent2.genes))
        if min_len <= 1:
            return parent1.copy(), parent2.copy()
        
        point = random.randint(1, min_len - 1)
        
        child1 = Chromosome(parent1.genes[:point] + parent2.genes[point:])
        child2 = Chromosome(parent2.genes[:point] + parent1.genes[point:])
        
        return child1, child2
    
    def _mutate(self, chromosome: Chromosome) -> Chromosome:
        """Мутация хромосомы"""
        from app.models import GroupSubject
        
        for gene in chromosome.genes:
            if random.random() < self.mutation_rate:
                mutation_type = random.randint(0, 3)
                
                if mutation_type == 0:  # Изменить день
                    gene.day = random.randint(0, self.days - 1)
                
                elif mutation_type == 1:  # Изменить время
                    gene.time_slot = random.randint(0, self.time_slots - 1)
                
                elif mutation_type == 2:  # Изменить аудиторию
                    gene.room_id = random.choice(list(self.rooms.keys()))
                
                else:  # Изменить преподавателя
                    gs = GroupSubject.query.filter_by(
                        group_id=gene.group_id,
                        subject_id=gene.subject_id
                    ).first()
                    
                    if gs:
                        subject = gs.subject
                        suitable = [
                            t_id for t_id, t in self.teachers.items()
                            if subject in t.subjects
                        ]
                        if suitable:
                            gene.teacher_id = random.choice(suitable)
        
        return chromosome