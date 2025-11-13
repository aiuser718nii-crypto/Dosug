"""
Базовый класс для всех алгоритмов генерации расписания
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from collections import defaultdict


class BaseScheduler(ABC):
    """Базовый класс для алгоритмов планирования"""
    
    def __init__(self, teachers: List, rooms: List, groups: List):
        """
        Инициализация планировщика
        
        Args:
            teachers: Список преподавателей
            rooms: Список аудиторий
            groups: Список групп
        """
        self.teachers = {t.id: t for t in teachers}
        self.rooms = {r.id: r for r in rooms}
        self.groups = {g.id: g for g in groups}
        
        # Параметры расписания
        self.days = 5  # Понедельник - Пятница
        self.time_slots = 7  # Количество пар в день
        
        # Названия для вывода
        self.day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
        self.time_names = [
            "08:00-09:30", "09:40-11:10", "11:20-12:50",
            "13:30-15:00", "15:10-16:40", "16:50-18:20", "18:30-20:00"
        ]
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """
        Генерация расписания
        
        Returns:
            Dict с ключами:
                - lessons: List[Dict] - список занятий
                - fitness: float - оценка качества
                - conflicts: List[str] - список конфликтов
        """
        pass
    
    def check_conflicts(self, lessons: List[Dict]) -> List[str]:
        """
        Проверка конфликтов в расписании
        
        Args:
            lessons: Список занятий
            
        Returns:
            Список описаний конфликтов
        """
        conflicts = []
        
        # Группируем занятия по времени
        time_slots = defaultdict(list)
        for lesson in lessons:
            key = (lesson['day'], lesson['time_slot'])
            time_slots[key].append(lesson)
        
        # Проверяем каждый временной слот
        for (day, time_slot), slot_lessons in time_slots.items():
            if len(slot_lessons) > 1:
                # Проверяем конфликты преподавателей
                teachers = [l['teacher_id'] for l in slot_lessons]
                if len(teachers) != len(set(teachers)):
                    teacher_id = [t for t in teachers if teachers.count(t) > 1][0]
                    teacher_name = self.teachers[teacher_id].name
                    conflicts.append(
                        f"Преподаватель {teacher_name} в двух местах: "
                        f"{self.day_names[day]}, {self.time_names[time_slot]}"
                    )
                
                # Проверяем конфликты аудиторий
                rooms = [l['room_id'] for l in slot_lessons]
                if len(rooms) != len(set(rooms)):
                    room_id = [r for r in rooms if rooms.count(r) > 1][0]
                    room_name = self.rooms[room_id].name
                    conflicts.append(
                        f"Аудитория {room_name} занята дважды: "
                        f"{self.day_names[day]}, {self.time_names[time_slot]}"
                    )
                
                # Проверяем конфликты групп
                groups = [l['group_id'] for l in slot_lessons]
                if len(groups) != len(set(groups)):
                    group_id = [g for g in groups if groups.count(g) > 1][0]
                    group_name = self.groups[group_id].name
                    conflicts.append(
                        f"Группа {group_name} в двух местах: "
                        f"{self.day_names[day]}, {self.time_names[time_slot]}"
                    )
        
        return conflicts
    
    def calculate_statistics(self, lessons: List[Dict]) -> Dict[str, Any]:
        """
        Расчет статистики расписания
        
        Args:
            lessons: Список занятий
            
        Returns:
            Словарь со статистикой
        """
        stats = {
            'total_lessons': len(lessons),
            'teacher_load': defaultdict(int),
            'room_usage': defaultdict(int),
            'group_load': defaultdict(int),
            'gaps': {
                'teacher': 0,
                'student': 0
            }
        }
        
        # Подсчет нагрузки
        for lesson in lessons:
            stats['teacher_load'][lesson['teacher_id']] += 1
            stats['room_usage'][lesson['room_id']] += 1
            stats['group_load'][lesson['group_id']] += 1
        
        # Подсчет окон
        stats['gaps']['teacher'] = self._count_gaps(lessons, 'teacher_id')
        stats['gaps']['student'] = self._count_gaps(lessons, 'group_id')
        
        return stats
    
    def _count_gaps(self, lessons: List[Dict], entity_key: str) -> int:
        """
        Подсчет окон в расписании
        
        Args:
            lessons: Список занятий
            entity_key: Ключ сущности ('teacher_id' или 'group_id')
            
        Returns:
            Количество окон
        """
        gaps = 0
        schedule = defaultdict(list)
        
        for lesson in lessons:
            key = (lesson[entity_key], lesson['day'])
            schedule[key].append(lesson['time_slot'])
        
        for slots in schedule.values():
            if len(slots) > 1:
                slots_sorted = sorted(slots)
                # Окна = разница между max и min минус количество занятий + 1
                gaps += (slots_sorted[-1] - slots_sorted[0] + 1 - len(slots))
        
        return gaps