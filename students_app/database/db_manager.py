"""Модуль для работы с базой данных"""

import sqlite3
from typing import Any, Dict, List, Optional

from loguru import logger


class DatabaseManager:
    """Менеджер базы данных"""

    def __init__(self, db_path: str):
        """Инициализация менеджера базы данных"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.initialize_test_data()  # Добавляем инициализацию тестовых данных

    def create_tables(self):
        """Создание необходимых таблиц"""
        # Таблица пользователей
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                group_number TEXT,
                role TEXT DEFAULT 'student'
            )
        """
        )

        # Таблица лабораторных работ
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS labs (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                max_score INTEGER
            )
        """
        )

        # Таблица вопросов
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lab_id INTEGER,
                question_number INTEGER,
                text TEXT,
                type TEXT,
                FOREIGN KEY (lab_id) REFERENCES labs (id)
            )
        """
        )

        # Таблица ответов
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                answer_number INTEGER,
                text TEXT,
                is_correct BOOLEAN,
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        """
        )

        # Таблица результатов тестов
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lab_number INTEGER,
                score INTEGER,
                max_score INTEGER,
                time_spent INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Таблица для пользовательских лабораторных работ
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_labs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lab_id INTEGER,
                status TEXT,
                grade INTEGER,
                submission_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (lab_id) REFERENCES labs (id)
            )
        """
        )

        self.conn.commit()

    def initialize_test_data(self):
        """Инициализация тестовых данных"""
        try:
            # Проверяем, есть ли уже лабораторные работы
            self.cursor.execute("SELECT COUNT(*) FROM labs")
            count = self.cursor.fetchone()[0]

            if count == 0:
                # Добавляем тестовую лабораторную работу
                self.cursor.execute(
                    """
                    INSERT INTO labs (id, title, description, max_score)
                    VALUES (1, 'Изучение базовых конструкций языка Python',
                           'Изучение основных конструкций языка Python: переменные, типы данных, операторы, функции', 100)
                """
                )

                # Добавляем тестовые вопросы
                questions = [
                    (1, 1, "Что такое переменная в Python?", "text"),
                    (1, 2, "Какие основные типы данных есть в Python?", "text"),
                    (1, 3, "Как объявить функцию в Python?", "text"),
                ]

                self.cursor.executemany(
                    """
                    INSERT INTO questions (lab_id, question_number, text, type)
                    VALUES (?, ?, ?, ?)
                """,
                    questions,
                )

                # Добавляем тестовые ответы
                answers = [
                    (1, 1, "Область памяти для хранения данных", True),
                    (1, 2, "int, float, str, bool, list, dict, tuple", True),
                    (1, 3, "def function_name():", True),
                ]

                self.cursor.executemany(
                    """
                    INSERT INTO answers (question_id, answer_number, text, is_correct)
                    VALUES (?, ?, ?, ?)
                """,
                    answers,
                )

                self.conn.commit()
                logger.info("Тестовые данные успешно добавлены")

        except Exception as e:
            logger.error(f"Ошибка при инициализации тестовых данных: {e}")

    def add_user(
        self, username: str, password: str, group_number: str, role: str = "student"
    ) -> bool:
        """Добавление нового пользователя"""
        try:
            self.cursor.execute(
                """
                INSERT INTO users (username, password, group_number, role)
                VALUES (?, ?, ?, ?)
            """,
                (username, password, group_number, role),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.error(f"Пользователь {username} уже существует")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return False

    def verify_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Проверка существования пользователя"""
        try:
            self.cursor.execute(
                """
                SELECT id, username, group_number, role
                FROM users
                WHERE username = ?
            """,
                (username,),
            )
            user = self.cursor.fetchone()
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "group_number": user[2],
                    "role": user[3],
                }
            return None
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя: {e}")
            return None

    def get_all_labs(self) -> List[Dict[str, Any]]:
        """Получение списка всех лабораторных работ"""
        try:
            self.cursor.execute(
                """
                SELECT id, title, description, max_score
                FROM labs
                ORDER BY id
            """
            )
            labs = self.cursor.fetchall()
            return [
                {
                    "id": lab[0],
                    "title": lab[1],
                    "description": lab[2],
                    "max_score": lab[3],
                }
                for lab in labs
            ]
        except Exception as e:
            logger.error(f"Ошибка при получении списка лабораторных работ: {e}")
            return []

    def get_student_info(self, student_id: int) -> Dict[str, Any]:
        """Получение информации о студенте"""
        try:
            self.cursor.execute(
                """
                SELECT username, group_number
                FROM users
                WHERE id = ? AND role = 'student'
            """,
                (student_id,),
            )
            student = self.cursor.fetchone()
            if student:
                return {"name": student[0], "group": student[1]}
            return {}
        except Exception as e:
            logger.error(f"Ошибка при получении информации о студенте: {e}")
            return {}

    def get_lab_info(self, lab_id: int) -> Dict[str, Any]:
        """Получение информации о лабораторной работе"""
        try:
            self.cursor.execute(
                """
                SELECT title, description, max_score
                FROM labs
                WHERE id = ?
            """,
                (lab_id,),
            )
            lab = self.cursor.fetchone()
            if lab:
                return {"name": lab[0], "description": lab[1], "max_score": lab[2]}
            return {}
        except Exception as e:
            logger.error(f"Ошибка при получении информации о лабораторной работе: {e}")
            return {}

    def get_test_result_by_id(self, result_id: int) -> Dict[str, Any]:
        """Получение результатов теста"""
        try:
            self.cursor.execute(
                """
                SELECT points, status
                FROM results
                WHERE id = ?
            """,
                (result_id,),
            )
            result = self.cursor.fetchone()
            if result:
                total_questions = 10  # Предполагаем, что всего 10 вопросов в тесте
                correct_answers = int(result[0] / 10)  # Каждый вопрос стоит 10 баллов
                return {
                    "score": result[0],
                    "status": result[1],
                    "correct_answers": correct_answers,
                    "total_questions": total_questions,
                }
            return {}
        except Exception as e:
            logger.error(f"Ошибка при получении результатов теста: {e}")
            return {}

    def get_monthly_report(self, month: int, year: int) -> List[Dict[str, Any]]:
        """Получение отчета о прохождении лабораторных работ за указанный месяц"""
        try:
            # Формируем SQL запрос с фильтрацией по месяцу и году
            query = """
                SELECT
                    u.username,
                    u.group_number,
                    l.title as lab_title,
                    r.points,
                    r.status,
                    r.submission_date
                FROM results r
                JOIN users u ON r.user_id = u.id
                JOIN labs l ON r.lab_id = l.id
                WHERE strftime('%m', r.submission_date) = ?
                AND strftime('%Y', r.submission_date) = ?
                AND u.role = 'student'
                ORDER BY u.group_number, u.username, l.title
            """

            # Преобразуем месяц и год в нужный формат
            month_str = str(month).zfill(2)
            year_str = str(year)

            self.cursor.execute(query, (month_str, year_str))

            # Получаем результаты
            results = []
            for row in self.cursor.fetchall():
                results.append(
                    {
                        "student_name": row[0],
                        "group": row[1],
                        "lab_title": row[2],
                        "points": row[3],
                        "status": row[4],
                        "submission_date": row[5],
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Ошибка при получении месячного отчета: {e}")
            return []

    def get_results_by_period(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """Получение результатов за указанный период"""
        try:
            query = """
                SELECT
                    u.username as student_name,
                    u.group_number as group,
                    l.title as lab_title,
                    r.points,
                    r.status,
                    r.submission_date
                FROM results r
                JOIN users u ON r.user_id = u.id
                JOIN labs l ON r.lab_id = l.id
                WHERE r.submission_date BETWEEN ? AND ?
                AND u.role = 'student'
                ORDER BY u.group_number, u.username, l.title
            """
            self.cursor.execute(query, (start_date, end_date))
            results = self.cursor.fetchall()

            return [
                {
                    "student_name": result[0],
                    "group": result[1],
                    "lab_title": result[2],
                    "points": result[3],
                    "status": result[4],
                    "submission_date": result[5],
                }
                for result in results
            ]

        except Exception as e:
            logger.error(f"Ошибка при получении результатов за период: {e}")
            return []

    def save_test_result(
        self, user_id: int, lab_number: int, score: int, max_score: int, time_spent: int
    ) -> bool:
        """Сохранение результата теста"""
        try:
            # Сохраняем результат теста
            self.cursor.execute(
                """
                INSERT INTO test_results (user_id, lab_number, score, max_score, time_spent)
                VALUES (?, ?, ?, ?, ?)
            """,
                (user_id, lab_number, score, max_score, time_spent),
            )

            # Обновляем статус лабораторной работы в user_labs
            self.cursor.execute(
                """
                UPDATE user_labs
                SET status = 'completed',
                    grade = ?,
                    submission_date = CURRENT_TIMESTAMP
                WHERE user_id = ? AND lab_id = ?
            """,
                (score, user_id, lab_number),
            )

            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении результата теста: {e}")
            return False

    def get_test_results(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Получение результатов тестов за период"""
        try:
            self.cursor.execute(
                """
                SELECT
                    u.username,
                    u.group_number,
                    tr.lab_number,
                    tr.score,
                    tr.max_score,
                    tr.time_spent,
                    tr.completed_at
                FROM test_results tr
                JOIN users u ON tr.user_id = u.id
                WHERE tr.completed_at BETWEEN ? AND ?
                ORDER BY tr.completed_at DESC
            """,
                (start_date, end_date),
            )

            results = []
            for row in self.cursor.fetchall():
                results.append(
                    {
                        "username": row[0],
                        "group_number": row[1],
                        "lab_number": row[2],
                        "score": row[3],
                        "max_score": row[4],
                        "time_spent": row[5],
                        "completed_at": row[6],
                    }
                )
            return results
        except Exception as e:
            logger.error(f"Ошибка при получении результатов тестов: {e}")
            return []

    def get_labs_with_results(self, user_id: int) -> list:
        """Получение списка лабораторных работ с результатами для пользователя"""
        try:
            self.cursor.execute(
                """
                SELECT
                    l.id as lab_number,
                    l.title,
                    COALESCE(r.status, 'not_started') as status,
                    r.submission_date,
                    r.points
                FROM labs l
                LEFT JOIN results r ON l.id = r.lab_id AND r.user_id = ?
                ORDER BY l.id
            """,
                (user_id,),
            )

            labs = []
            for row in self.cursor.fetchall():
                lab = {
                    "lab_number": row[0],
                    "title": row[1],
                    "status": row[2],
                    "submission_date": row[3] if row[3] else "",
                    "points": row[4] if row[4] else 0,
                }
                labs.append(lab)

            return labs

        except Exception as e:
            logger.error(f"Ошибка при получении списка лабораторных работ: {e}")
            return []

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        self.conn.close()
