"""Модуль для управления студентами"""
import sqlite3
from datetime import datetime

class StudentDB:
    def __init__(self, db_path='students.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных студентов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    group_name TEXT NOT NULL
                )
            ''')
            conn.commit()

    def get_current_semester(self):
        """Определение текущего семестра на основе даты"""
        current_month = datetime.now().month
        # Январь-Июнь (1-6): 4 семестр
        # Июль-Август (7-8): 4 семестр (каникулы)
        # Сентябрь-Декабрь (9-12): 5 семестр
        return '5' if 9 <= current_month <= 12 else '4'

    def validate_group(self, group_name):
        """Проверка корректности группы"""
        try:
            # Проверяем формат группы (например, ПС4-51 или ПС4-42)
            faculty = group_name[:2]  # ПС
            subgroup = group_name[2]  # 4
            semester = group_name[-2:]  # 51 или 42

            if faculty != 'ПС' or subgroup not in ['2', '4']:
                return False

            # Проверяем семестр
            current_semester = self.get_current_semester()
            expected_group_start = current_semester + '1'  # 41 или 51
            alternative_group = current_semester + '2'  # 42 или 52

            return semester in [expected_group_start, alternative_group]
        except:
            return False

    def find_student(self, first_name, last_name, group_name):
        """Поиск студента в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, group_name FROM students 
                WHERE first_name = ? AND last_name = ?
            ''', (first_name, last_name))
            return cursor.fetchone()

    def add_student(self, first_name, last_name, group_name):
        """Добавление нового студента"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (first_name, last_name, group_name)
                VALUES (?, ?, ?)
            ''', (first_name, last_name, group_name))
            conn.commit()
            return cursor.lastrowid

    def update_student_group(self, student_id, new_group):
        """Обновление группы студента"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE students 
                SET group_name = ?
                WHERE id = ?
            ''', (new_group, student_id))
            conn.commit()

    def check_and_update_semester(self, student_id, current_group):
        """Проверка и обновление семестра студента"""
        current_semester = self.get_current_semester()
        group_semester = current_group[-2]  # Получаем первую цифру семестра из группы

        if group_semester != current_semester:
            # Группа не соответствует текущему семестру
            return True, f"ПС{current_group[2]}-{current_semester}1"
        return False, None

    def get_group_statistics(self, group_name):
        """Получение статистики по группе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as total_students,
                       AVG(CASE WHEN last_visit IS NOT NULL THEN 1 ELSE 0 END) as attendance_rate
                FROM students 
                WHERE group_name = ?
            ''', (group_name,))
            return cursor.fetchone()

    def validate_student_name(self, name):
        """Валидация имени/фамилии студента"""
        if not name or len(name) < 2:
            return False
        # Только кириллица и дефис
        return all(c.isalpha() or c == '-' for c in name) and any(c.isalpha() for c in name)

    def get_student_history(self, student_id):
        """Получение истории посещений студента"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT visit_date, lab_name, points
                FROM visits
                JOIN labs ON visits.lab_id = labs.id
                WHERE student_id = ?
                ORDER BY visit_date DESC
            ''', (student_id,))
            return cursor.fetchall()
