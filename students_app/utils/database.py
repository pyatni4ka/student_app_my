import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='students.db'):
        """Инициализация базы данных"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация структуры базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    visit_date TEXT NOT NULL
                )
            ''')
            conn.commit()
    
    def add_student(self, group, name, date):
        """Добавление записи о посещении студента"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO students (group_name, student_name, visit_date) VALUES (?, ?, ?)',
                (group, name, date)
            )
            conn.commit()
    
    def get_all_students(self):
        """Получение всех записей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT group_name, student_name, visit_date FROM students')
            return [{'group': row[0], 'name': row[1], 'date': row[2]} for row in cursor.fetchall()]
    
    def search_students(self, query):
        """Поиск студентов по имени или группе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT group_name, student_name, visit_date 
                   FROM students 
                   WHERE student_name LIKE ? OR group_name LIKE ?''',
                (f'%{query}%', f'%{query}%')
            )
            return [{'group': row[0], 'name': row[1], 'date': row[2]} for row in cursor.fetchall()]
    
    def get_students_by_group(self, group):
        """Получение студентов определенной группы"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT group_name, student_name, visit_date FROM students WHERE group_name = ?',
                (group,)
            )
            return [{'group': row[0], 'name': row[1], 'date': row[2]} for row in cursor.fetchall()]
    
    def get_groups(self):
        """Получение списка всех групп"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT group_name FROM students')
            return [row[0] for row in cursor.fetchall()]
    
    def clear_all(self):
        """Очистка всех данных (для тестов)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM students')
            conn.commit()
    
    def __del__(self):
        """Очистка тестовой базы данных при завершении"""
        if os.path.exists(self.db_path) and self.db_path == 'test.db':
            os.remove(self.db_path)
