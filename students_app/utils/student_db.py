"""
Модуль для работы с базой данных студентов
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union


class StudentDB:
    def __init__(self, db_path: str = "students.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self) -> None:
        """Инициализация базы данных студентов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создаем таблицу групп
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                faculty TEXT NOT NULL,
                subgroup TEXT NOT NULL,
                semester INTEGER NOT NULL
            )
        """
        )

        # Создаем таблицу студентов
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        """
        )

        # Создаем таблицу посещений
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                lab_id INTEGER,
                visit_date DATE,
                points INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (lab_id) REFERENCES labs (id)
            )
        """
        )

        # Создаем таблицу лабораторных работ
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS labs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()

    def get_current_semester(self) -> str:
        """Определение текущего семестра на основе даты"""
        current_month = datetime.now().month
        # Январь-Июнь (1-6): 4 семестр
        # Июль-Август (7-8): 4 семестр
        # Сентябрь-Декабрь (9-12): 5 семестр
        return "5" if 9 <= current_month <= 12 else "4"

    def validate_group(self, group_name: str) -> bool:
        """Проверка корректности группы"""
        try:
            # Проверяем формат группы (например, ПС4-51 или ПС4-42)
            if not group_name.startswith("ПС"):
                return False

            # Проверяем номер курса (4)
            if not group_name[2].isdigit():
                return False

            # Проверяем наличие дефиса
            if group_name[3] != "-":
                return False

            # Проверяем номер группы (51 или 42)
            if not group_name[4:].isdigit():
                return False

            return True
        # trunk-ignore(ruff/E722)
        except:
            return False

    def find_student(
        self, first_name: str, last_name: str, group_name: str
    ) -> Optional[Tuple[int, str]]:
        """Поиск студента в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, group_id FROM students
                WHERE first_name = ? AND last_name = ?
            """,
                (first_name, last_name),
            )
            result = cursor.fetchone()
            if result:
                student_id, group_id = result
                cursor.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
                group_result = cursor.fetchone()
                if group_result:
                    return student_id, group_result[0]
            return None
        finally:
            conn.close()

    def add_student(
        self, first_name: str, last_name: str, group_name: str
    ) -> Union[int, None]:
        """Добавление нового студента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Получаем ID группы
            cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
            group_id = cursor.fetchone()

            if not group_id:
                return None

            # Добавляем студента
            cursor.execute(
                """
                INSERT INTO students (first_name, last_name, group_id)
                VALUES (?, ?, ?)
            """,
                (first_name, last_name, group_id[0]),
            )

            conn.commit()
            return cursor.lastrowid

        except sqlite3.Error:
            return None
        finally:
            conn.close()

    def update_student_group(self, student_id: int, new_group: str) -> bool:
        """Обновление группы студента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE students
                SET group_id = (SELECT id FROM groups WHERE name = ?)
                WHERE id = ?
            """,
                (new_group, student_id),
            )

            conn.commit()
            return cursor.rowcount > 0

        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def check_and_update_semester(
        self, student_id: int, current_group: str
    ) -> Tuple[bool, Optional[str]]:
        """Проверка и обновление семестра студента"""
        current_semester = self.get_current_semester()
        group_semester = current_group[-2]  # Получаем первую цифру семестра из группы

        # Если текущий семестр больше семестра группы, нужно обновить
        if current_semester > group_semester:
            return True, f"ПС{current_group[2]}-{current_semester}1"
        return False, None

    def get_group_statistics(self, group_name: str) -> Tuple[int, float]:
        """Получение статистики по группе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT COUNT(*) as total_students,
                       AVG(CASE WHEN last_visit IS NOT NULL THEN 1 ELSE 0 END) as attendance_rate
                FROM students
                WHERE group_id = (SELECT id FROM groups WHERE name = ?)
            """,
                (group_name,),
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def validate_student_name(self, name: str) -> bool:
        """Валидация имени/фамилии студента"""
        if not name or len(name) < 2:
            return False
        # Проверяем, что имя содержит только буквы и дефис
        return all(c.isalpha() or c == "-" for c in name) and any(
            c.isalpha() for c in name
        )

    def get_student_history(self, student_id: int) -> List[Dict[str, Union[str, int]]]:
        """Получение истории посещений студента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT g.name, g.semester
                FROM students s
                JOIN groups g ON s.group_id = g.id
                WHERE s.id = ?
                ORDER BY g.semester
            """,
                (student_id,),
            )

            history: List[Dict[str, Union[str, int]]] = []
            for group_name, semester in cursor.fetchall():
                history.append({"group": group_name, "semester": semester})

            return history
        finally:
            conn.close()
