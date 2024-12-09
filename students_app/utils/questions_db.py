"""Модуль для работы с базой данных вопросов"""
import os
import sqlite3
from typing import List, Tuple, Optional, Dict, Any, Union
from datetime import datetime

class QuestionsDB:
    TEST_DURATION: int = 20  # Длительность теста в минутах

    def __init__(self, db_path: str = 'questions.db') -> None:
        self.db_path = db_path
        self.init_db()
        # Добавляем тестовые данные, если база пустая
        self.init_test_data()

    def get_connection(self) -> sqlite3.Connection:
        """Получение соединения с базой данных"""
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица студентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    group_name TEXT NOT NULL
                )
            ''')

            # Таблица лабораторных работ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            ''')

            # Таблица вопросов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lab_id INTEGER,
                    question_text TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    points INTEGER DEFAULT 1,
                    FOREIGN KEY (lab_id) REFERENCES labs(id)
                )
            ''')

            # Таблица результатов тестирования
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    lab_id INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    points INTEGER DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (lab_id) REFERENCES labs(id)
                )
            ''')

            # Таблица ответов на тест
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_answers (
                    result_id INTEGER,
                    question_id INTEGER,
                    answer TEXT,
                    points_earned INTEGER DEFAULT 0,
                    FOREIGN KEY (result_id) REFERENCES test_results(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id),
                    PRIMARY KEY (result_id, question_id)
                )
            ''')

            conn.commit()

    def init_test_data(self) -> None:
        """Инициализация тестовых данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем, есть ли уже лабораторные работы
            cursor.execute('SELECT COUNT(*) FROM labs')
            if cursor.fetchone()[0] == 0:
                # Добавляем тестовые лабораторные работы
                labs = [
                    ('Лабораторная работа №1', 'Исследование линейной электрической цепи постоянного тока'),
                    ('Лабораторная работа №2', 'Исследование нелинейной электрической цепи постоянного тока'),
                    ('Лабораторная работа №3', 'Исследование линейной электрической цепи переменного тока'),
                ]
                cursor.executemany('INSERT INTO labs (name, description) VALUES (?, ?)', labs)
                conn.commit()

    def get_random_questions(self, lab_id: int, count: int = 10) -> List[Tuple[int, str, int]]:
        """Получение случайных вопросов для теста"""
        query = """
            SELECT id, question_text, points
            FROM questions
            WHERE lab_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (lab_id, count))
            return cursor.fetchall()

    def start_test(self, student_id: int, lab_id: int) -> int:
        """Начало тестирования"""
        query = """
            INSERT INTO test_results
            (student_id, lab_id, start_time)
            VALUES (?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            start_time = datetime.now().isoformat()
            cursor.execute(query, (student_id, lab_id, start_time))
            return cursor.lastrowid

    def submit_answer(self, result_id: int, question_id: int, answer: str) -> None:
        """Сохранение ответа на вопрос"""
        query = """
            INSERT OR REPLACE INTO test_answers
            (result_id, question_id, answer, points_earned)
            VALUES (?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT points FROM questions WHERE id = ?', (question_id,))
            points = cursor.fetchone()[0]
            cursor.execute(query, (result_id, question_id, answer, points))

    def finish_test(self, result_id: int) -> int:
        """Завершение тестирования"""
        query = """
            UPDATE test_results
            SET end_time = ?
            WHERE id = ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            end_time = datetime.now().isoformat()
            cursor.execute(query, (end_time, result_id))

            # Подсчитываем количество правильных ответов
            query = """
                SELECT COUNT(*)
                FROM test_answers ta
                JOIN questions q ON ta.question_id = q.id
                WHERE ta.result_id = ? AND ta.answer = q.correct_answer
            """
            cursor.execute(query, (result_id,))
            correct_answers = cursor.fetchone()[0]

            # Обновляем количество баллов
            query = """
                UPDATE test_results
                SET points = ?
                WHERE id = ?
            """
            points = int(correct_answers * 100 / 10)  # 10 вопросов максимум
            cursor.execute(query, (points, result_id))
            return points

    def get_test_results(self, student_id: int, lab_id: Optional[int] = None) -> List[Tuple[int, int, str, str, str, int]]:
        """Получение результатов тестирования"""
        query = """
            SELECT tr.id, tr.student_id, l.name, tr.start_time, tr.end_time,
                   COALESCE((SELECT SUM(points_earned)
                            FROM test_answers ta
                            WHERE ta.result_id = tr.id), 0) as total_points
            FROM test_results tr
            JOIN labs l ON tr.lab_id = l.id
            WHERE tr.student_id = ?
        """
        params: List[Union[int, str]] = [student_id]

        if lab_id is not None:
            query += " AND tr.lab_id = ?"
            params.append(lab_id)

        query += " ORDER BY tr.start_time DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    def get_detailed_results(self, result_id: int) -> List[Dict[str, Any]]:
        """Получить детальные результаты теста"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT q.question_text, ta.answer, q.correct_answer, ta.points_earned
                FROM test_answers ta
                JOIN questions q ON ta.question_id = q.id
                WHERE ta.result_id = ?
            """
            cursor.execute(query, (result_id,))
            results = []
            for row in cursor.fetchall():
                results.append({
                    'question': row[0],
                    'student_answer': row[1],
                    'correct_answer': row[2],
                    'points': row[3]
                })
            return results

    def get_all_labs(self) -> List[Tuple[int, str, str]]:
        """Получить список всех лабораторных работ"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, description FROM labs ORDER BY id')
            return cursor.fetchall()

    def _has_data(self) -> bool:
        """Проверка наличия данных в базе"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM labs')
            return cursor.fetchone()[0] > 0

    def _populate_db(self) -> None:
        """Заполнение базы данных тестовыми данными"""
        labs_data = [
            (1, "Лабораторная работа №1", "Основы работы с PyQt"),
            (2, "Лабораторная работа №2", "Работа с базами данных"),
            (3, "Лабораторная работа №3", "Создание графического интерфейса")
        ]

        questions_data = [
            # ... existing code ...
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Добавляем лабораторные работы
            cursor.executemany('INSERT INTO labs (id, name, description) VALUES (?, ?, ?)', labs_data)

            # Добавляем вопросы
            cursor.executemany(
                'INSERT INTO questions (lab_id, question_type, question_text, correct_answer, image_path, points) VALUES (?, ?, ?, ?, ?, ?)',
                questions_data
            )

            conn.commit()

    def __del__(self) -> None:
        """Очистка тестовой базы данных при завершении"""
        if os.path.exists(self.db_path) and self.db_path == 'test.db':
            os.remove(self.db_path)
