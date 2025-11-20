"""
Скрипт для инициализации базы данных и добавления тестовых данных
"""

from backend.app import create_app, db
from app.models import Teacher, Room, Group, Subject, GroupSubject

def init_database():
    """Инициализация базы данных"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🗄️  ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
        print("="*70 + "\n")
        
        # Удаление старых таблиц
        print("🗑️  Удаление старых таблиц...")
        db.drop_all()
        
        # Создание новых таблиц
        print("📦 Создание новых таблиц...")
        db.create_all()
        
        print("✅ Структура базы данных создана!\n")
        
        # Добавление тестовых данных
        add_sample_data()

def add_sample_data():
    """Добавление тестовых данных"""
    print("="*70)
    print("📝 ДОБАВЛЕНИЕ ТЕСТОВЫХ ДАННЫХ")
    print("="*70 + "\n")
    
    # ========== ПРЕДМЕТЫ ==========
    print("📚 Создание предметов...")
    subjects_data = []
    
    subjects = []
    for s_data in subjects_data:
        subject = Subject(**s_data)
        db.session.add(subject)
        subjects.append(subject)
    
    db.session.commit()
    print(f"   ✓ Добавлено предметов: {len(subjects)}")
    for s in subjects:
        print(f"      • {s.name} ({s.code})")
    
    # ========== ПРЕПОДАВАТЕЛИ ==========
    print(f"\n👨‍🏫 Создание преподавателей...")
    
    teacher1 = Teacher(
        name="Иванов Иван Иванович",
        email="ivanov@university.edu",
        max_hours_per_week=20
    )
    teacher1.subjects = [subjects[0], subjects[1], subjects[4]]  # Математика, Высшая математика, Физика
    
    teacher2 = Teacher(
        name="Петрова Анна Сергеевна",
        email="petrova@university.edu",
        max_hours_per_week=18
    )
    teacher2.subjects = [subjects[2], subjects[3]]  # Информатика, Программирование
    
    teacher3 = Teacher(
        name="Сидоров Петр Петрович",
        email="sidorov@university.edu",
        max_hours_per_week=16
    )
    teacher3.subjects = [subjects[5], subjects[6]]  # Английский, История
    
    teacher4 = Teacher(
        name="Козлова Мария Александровна",
        email="kozlova@university.edu",
        max_hours_per_week=20
    )
    teacher4.subjects = [subjects[7], subjects[6]]  # Философия, История
    
    teacher5 = Teacher(
        name="Смирнов Алексей Викторович",
        email="smirnov@university.edu",
        max_hours_per_week=22
    )
    teacher5.subjects = [subjects[8], subjects[9], subjects[2]]  # БД, Веб, Информатика
    
    teachers = [teacher1, teacher2, teacher3, teacher4, teacher5]
    db.session.add_all(teachers)
    db.session.commit()
    
    print(f"   ✓ Добавлено преподавателей: {len(teachers)}")
    for t in teachers:
        subjects_str = ", ".join([s.name for s in t.subjects])
        print(f"      • {t.name}")
        print(f"        Предметы: {subjects_str}")
    
    # ========== АУДИТОРИИ ==========
    print(f"\n🏫 Создание аудиторий...")
    rooms_data = [
        {'name': '101', 'capacity': 30, 'building': 'Корпус A'},
        {'name': '102', 'capacity': 25, 'building': 'Корпус A'},
        {'name': '205', 'capacity': 35, 'building': 'Корпус B'},
        {'name': '206', 'capacity': 28, 'building': 'Корпус B'},
        {'name': '301', 'capacity': 40, 'building': 'Корпус A'},
        {'name': '305', 'capacity': 32, 'building': 'Корпус A'},
        {'name': 'Лаб-1', 'capacity': 20, 'building': 'Корпус C'},
        {'name': 'Лаб-2', 'capacity': 22, 'building': 'Корпус C'},
        {'name': 'Актовый зал', 'capacity': 100, 'building': 'Главный корпус'},
    ]
    
    rooms = []
    for r_data in rooms_data:
        room = Room(**r_data)
        db.session.add(room)
        rooms.append(room)
    
    db.session.commit()
    print(f"   ✓ Добавлено аудиторий: {len(rooms)}")
    for r in rooms:
        print(f"      • {r.name} ({r.building}) - вместимость: {r.capacity} чел.")
    
    # ========== ГРУППЫ ==========
    print(f"\n👥 Создание групп...")
    
    group1 = Group(name="ПИ-101", course=1, student_count=28)
    group2 = Group(name="ПИ-102", course=1, student_count=26)
    group3 = Group(name="ИБ-101", course=1, student_count=25)
    group4 = Group(name="ИС-101", course=1, student_count=30)
    
    groups = [group1, group2, group3, group4]
    db.session.add_all(groups)
    db.session.commit()
    
    print(f"   ✓ Добавлено групп: {len(groups)}")
    for g in groups:
        print(f"      • {g.name} ({g.student_count} студентов)")
    
    # ========== ПРЕДМЕТЫ ДЛЯ ГРУПП ==========
    print(f"\n📖 Назначение предметов группам...")
    
    group_subjects_data = [
        # ПИ-101
        {'group_id': group1.id, 'subject_id': subjects[0].id, 'hours_per_week': 4},  # Математика
        {'group_id': group1.id, 'subject_id': subjects[2].id, 'hours_per_week': 4},  # Информатика
        {'group_id': group1.id, 'subject_id': subjects[3].id, 'hours_per_week': 4},  # Программирование
        {'group_id': group1.id, 'subject_id': subjects[4].id, 'hours_per_week': 3},  # Физика
        {'group_id': group1.id, 'subject_id': subjects[5].id, 'hours_per_week': 2},  # Английский
        
        # ПИ-102
        {'group_id': group2.id, 'subject_id': subjects[0].id, 'hours_per_week': 4},  # Математика
        {'group_id': group2.id, 'subject_id': subjects[2].id, 'hours_per_week': 4},  # Информатика
        {'group_id': group2.id, 'subject_id': subjects[3].id, 'hours_per_week': 4},  # Программирование
        {'group_id': group2.id, 'subject_id': subjects[5].id, 'hours_per_week': 2},  # Английский
        {'group_id': group2.id, 'subject_id': subjects[6].id, 'hours_per_week': 2},  # История
        
        # ИБ-101
        {'group_id': group3.id, 'subject_id': subjects[1].id, 'hours_per_week': 4},  # Высшая математика
        {'group_id': group3.id, 'subject_id': subjects[2].id, 'hours_per_week': 3},  # Информатика
        {'group_id': group3.id, 'subject_id': subjects[8].id, 'hours_per_week': 3},  # Базы данных
        {'group_id': group3.id, 'subject_id': subjects[5].id, 'hours_per_week': 2},  # Английский
        {'group_id': group3.id, 'subject_id': subjects[7].id, 'hours_per_week': 2},  # Философия
        
        # ИС-101
        {'group_id': group4.id, 'subject_id': subjects[0].id, 'hours_per_week': 3},  # Математика
        {'group_id': group4.id, 'subject_id': subjects[2].id, 'hours_per_week': 4},  # Информатика
        {'group_id': group4.id, 'subject_id': subjects[9].id, 'hours_per_week': 3},  # Веб-разработка
        {'group_id': group4.id, 'subject_id': subjects[8].id, 'hours_per_week': 3},  # Базы данных
        {'group_id': group4.id, 'subject_id': subjects[5].id, 'hours_per_week': 2},  # Английский
    ]
    
    total_hours = 0
    for gs_data in group_subjects_data:
        gs = GroupSubject(**gs_data)
        db.session.add(gs)
        total_hours += gs_data['hours_per_week']
    
    db.session.commit()
    
    print(f"   ✓ Назначено предметов: {len(group_subjects_data)}")
    print(f"   ✓ Всего часов в неделю: {total_hours}")
    
    # Вывод по группам
    for group in groups:
        group_subj = GroupSubject.query.filter_by(group_id=group.id).all()
        print(f"\n      📋 {group.name}:")
        for gs in group_subj:
            print(f"         • {gs.subject.name}: {gs.hours_per_week} ч/нед")
    
    # ========== ИТОГИ ==========
    print("\n" + "="*70)
    print("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("="*70)
    print(f"\n📊 Итоговая статистика:")
    print(f"   • Предметов:     {len(subjects)}")
    print(f"   • Преподавателей: {len(teachers)}")
    print(f"   • Аудиторий:     {len(rooms)}")
    print(f"   • Групп:         {len(groups)}")
    print(f"   • Всего часов:   {total_hours} ч/нед")
    print(f"   • Всего пар:     {total_hours} (примерно {total_hours // len(groups)} пар на группу)")
    print("\n" + "="*70)
    print("🚀 Можно запускать сервер: python run.py")
    print("="*70 + "\n")

if __name__ == '__main__':
    init_database()