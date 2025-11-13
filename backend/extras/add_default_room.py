"""
Скрипт для добавления колонки default_room_id в таблицу group
"""

import sqlite3
import os

# Путь к базе данных
DB_PATH = 'schedule.db'  # или 'instance/schedule.db'

if not os.path.exists(DB_PATH):
    DB_PATH = 'instance/schedule.db'

print(f"📂 Путь к БД: {DB_PATH}")

# Подключение к базе данных
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Проверяем, существует ли уже колонка
    cursor.execute("PRAGMA table_info('group')")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"📋 Существующие колонки в таблице 'group': {columns}")
    
    if 'default_room_id' in columns:
        print("✅ Колонка default_room_id уже существует")
    else:
        print("➕ Добавление колонки default_room_id...")
        
        # Добавляем колонку
        cursor.execute("""
            ALTER TABLE "group" 
            ADD COLUMN default_room_id INTEGER 
            REFERENCES room(id)
        """)
        
        conn.commit()
        print("✅ Колонка default_room_id успешно добавлена!")
    
    # Проверяем результат
    cursor.execute("PRAGMA table_info('group')")
    columns_after = [column[1] for column in cursor.fetchall()]
    print(f"📋 Колонки после миграции: {columns_after}")
    
except sqlite3.Error as e:
    print(f"❌ Ошибка: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n✅ Миграция завершена!")