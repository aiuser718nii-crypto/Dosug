from abc import ABC, abstractmethod
from typing import List, Dict, Any
from collections import defaultdict

class BaseScheduler(ABC):
    """
    Абстрактный базовый класс для всех алгоритмов планирования.
    Определяет интерфейс, которому должны следовать CSP и Genetic.
    """
    
    def __init__(self, teachers: List, rooms: List, groups: List):
        """
        Инициализация общими данными.
        Args:
            teachers: Список объектов Teacher (из БД)
            rooms: Список объектов Room (из БД)
            groups: Список объектов Group (из БД)
        """
        # Создаем словари для быстрого доступа по ID
        self.teachers = {t.id: t for t in teachers}
        self.rooms = {r.id: r for r in rooms}
        self.groups = {g.id: g for g in groups}
        
        # Константы (можно вынести в конфиг)
        self.days_per_week = 5
        self.slots_per_day = 7
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """
        Основной метод генерации расписания.
        Returns:
            Dict с ключами:
                - lessons: Список словарей для создания моделей Lesson
                - fitness: Оценка качества
                - conflicts: Список найденных конфликтов
                - time: Время выполнения
        """
        pass
    
    def check_conflicts(self, lessons: List[Dict]) -> List[Dict]:
        """
        Универсальная проверка конфликтов в списке занятий.
        Проверяет пересечения учителей, групп и аудиторий.
        """
        conflicts = []
        
        # Группируем занятия по уникальному временному слоту
        # Ключ: (week_id, day, time_slot)
        time_slots = defaultdict(list)
        
        for lesson in lessons:
            # week_id=0 используется как заглушка, если недели не используются
            week = lesson.get('week_id', 0)
            day = lesson.get('day_of_week', lesson.get('day')) # Поддержка обоих ключей
            slot = lesson.get('time_slot')
            
            if day is None or slot is None:
                continue
                
            key = (week, day, slot)
            time_slots[key].append(lesson)
        
        # Проверяем каждый слот
        for (week, day, slot), slot_lessons in time_slots.items():
            if len(slot_lessons) <= 1:
                continue
            
            # 1. Конфликт ПРЕПОДАВАТЕЛЯ
            teachers = [l['teacher_id'] for l in slot_lessons]
            if len(teachers) != len(set(teachers)):
                # Находим, кто именно пересекается
                seen = set()
                dupes = set(x for x in teachers if x in seen or seen.add(x))
                for t_id in dupes:
                    t_obj = self.teachers.get(t_id)
                    t_name = t_obj.name if t_obj else f"ID {t_id}"
                    conflicts.append({
                        'type': 'teacher_conflict',
                        'message': f'Преподаватель {t_name} занят дважды',
                        'week': week, 'day': day, 'slot': slot,
                        'teacher_id': t_id
                    })

            # 2. Конфликт АУДИТОРИИ
            rooms = [l['room_id'] for l in slot_lessons]
            if len(rooms) != len(set(rooms)):
                seen = set()
                dupes = set(x for x in rooms if x in seen or seen.add(x))
                for r_id in dupes:
                    r_obj = self.rooms.get(r_id)
                    r_name = r_obj.name if r_obj else f"ID {r_id}"
                    conflicts.append({
                        'type': 'room_conflict',
                        'message': f'Аудитория {r_name} занята дважды',
                        'week': week, 'day': day, 'slot': slot,
                        'room_id': r_id
                    })

            # 3. Конфликт ГРУППЫ
            groups = [l['group_id'] for l in slot_lessons]
            if len(groups) != len(set(groups)):
                seen = set()
                dupes = set(x for x in groups if x in seen or seen.add(x))
                for g_id in dupes:
                    g_obj = self.groups.get(g_id)
                    g_name = g_obj.name if g_obj else f"ID {g_id}"
                    conflicts.append({
                        'type': 'group_conflict',
                        'message': f'Группа {g_name} должна быть в двух местах',
                        'week': week, 'day': day, 'slot': slot,
                        'group_id': g_id
                    })
                    
        return conflicts