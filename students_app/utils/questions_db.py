"""Модуль для работы с базой данных вопросов"""
import sqlite3
import random
import os
from datetime import datetime, timedelta

class QuestionsDB:
    TEST_DURATION = 20  # Длительность теста в минутах
    
    def __init__(self, db_path='questions.db'):
        self.db_path = db_path
        self.init_db()
        # Добавляем тестовые данные, если база пустая
        self.init_test_data()
    
    def get_connection(self):
        """Получение соединения с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
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
    
    def init_test_data(self):
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
    
    def start_test(self, student_id, lab_id):
        """Начать тестирование"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            start_time = datetime.now()
            cursor.execute('''
                INSERT INTO test_results (student_id, lab_id, start_time)
                VALUES (?, ?, ?)
            ''', (student_id, lab_id, start_time))
            return cursor.lastrowid
    
    def check_test_time(self, result_id):
        """Проверка времени тестирования"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT start_time, end_time FROM test_results WHERE id = ?', (result_id,))
            start_time, end_time = cursor.fetchone()
            
            if end_time:
                return False  # Тест уже завершен
                
            start = datetime.strptime(start_time.split('.')[0], '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            
            # Если прошло больше 20 минут, автоматически завершаем тест
            if current_time - start > timedelta(minutes=self.TEST_DURATION):
                self.finish_test(result_id)
                return False
                
            return True
    
    def submit_answer(self, result_id, question_id, student_answer):
        """Сохранить ответ студента"""
        # Проверяем, не истекло ли время
        if not self.check_test_time(result_id):
            return False, 0
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем правильный ответ
            cursor.execute('SELECT correct_answer, points FROM questions WHERE id = ?', (question_id,))
            correct_answer, points = cursor.fetchone()
            
            # Проверяем ответ
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
            points_earned = points if is_correct else 0
            
            # Сохраняем ответ
            cursor.execute('''
                INSERT INTO test_answers (result_id, question_id, answer, points_earned)
                VALUES (?, ?, ?, ?)
            ''', (result_id, question_id, student_answer, points_earned))
            
            conn.commit()
            return is_correct, points_earned
    
    def finish_test(self, result_id):
        """Завершить тестирование"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Подсчитываем общее количество баллов
            cursor.execute('''
                SELECT SUM(points_earned)
                FROM test_answers
                WHERE result_id = ?
            ''', (result_id,))
            total_points = cursor.fetchone()[0] or 0
            
            # Обновляем результат теста
            cursor.execute('''
                UPDATE test_results 
                SET end_time = ?, points = ?
                WHERE id = ?
            ''', (datetime.now(), total_points, result_id))
            
            conn.commit()
            return total_points
    
    def get_test_results(self, student_id, lab_id=None):
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
        params = [student_id]
        
        if lab_id is not None:
            query += " AND tr.lab_id = ?"
            params.append(lab_id)
            
        query += " ORDER BY tr.start_time DESC"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_detailed_results(self, result_id):
        """Получить детальные результаты теста"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT q.question_text, sa.answer, q.correct_answer, 
                       sa.points_earned
                FROM test_answers sa
                JOIN questions q ON sa.question_id = q.id
                WHERE sa.result_id = ?
            ''', (result_id,))
            return cursor.fetchall()
    
    def get_all_labs(self):
        """Получить список всех лабораторных работ"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, description FROM labs ORDER BY id')
            return cursor.fetchall()
            
    def get_random_questions(self, lab_id):
        """Получение случайного набора вопросов для лабораторной работы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем 2 случайных теоретических вопроса
            cursor.execute('''
                SELECT id, question_text, correct_answer, points
                FROM questions 
                WHERE lab_id = ? AND question_type = 'theory'
                ORDER BY RANDOM() LIMIT 2
            ''', (lab_id,))
            theory_questions = cursor.fetchall()
            
            # Получаем 2 случайных практических задания
            cursor.execute('''
                SELECT id, question_text, correct_answer, points
                FROM questions 
                WHERE lab_id = ? AND question_type = 'practice'
                ORDER BY RANDOM() LIMIT 2
            ''', (lab_id,))
            practice_questions = cursor.fetchall()
            
            # Получаем 1 случайный графический вопрос
            cursor.execute('''
                SELECT id, question_text, correct_answer, image_path, points
                FROM questions 
                WHERE lab_id = ? AND question_type = 'graphics'
                ORDER BY RANDOM() LIMIT 1
            ''', (lab_id,))
            graphics_question = cursor.fetchone()
            
            return {
                'theory': theory_questions,
                'practice': practice_questions,
                'graphics': graphics_question
            }
    
    def add_question(self, lab_id, question_type, text, answer, image_path=None, points=1):
        """Добавление нового вопроса (только для преподавателя)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO questions (lab_id, question_type, question_text, correct_answer, image_path, points)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (lab_id, question_type, text, answer, image_path, points))
            conn.commit()
            return cursor.lastrowid
    
    def update_question(self, question_id, text=None, answer=None, image_path=None, points=None):
        """Обновление существующего вопроса (только для преподавателя)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if text is not None:
                updates.append('question_text = ?')
                params.append(text)
            if answer is not None:
                updates.append('correct_answer = ?')
                params.append(answer)
            if image_path is not None:
                updates.append('image_path = ?')
                params.append(image_path)
            if points is not None:
                updates.append('points = ?')
                params.append(points)
                
            if updates:
                params.append(question_id)
                query = f'UPDATE questions SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                return True
            return False
    
    def _has_data(self):
        """Проверка наличия данных в базе"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM labs')
            return cursor.fetchone()[0] > 0
    
    def _populate_db(self):
        """Заполнение базы данных тестовыми данными"""
        labs_data = [
            (1, "Лабораторная работа №1", "Основы работы с PyQt"),
            (2, "Лабораторная работа №2", "Работа с базами данных"),
            (3, "Лабораторная работа №3", "Создание графического интерфейса")
        ]
        
        questions_data = [
            # Лабораторная работа 1
            # Теоретические вопросы
            (1, 'theory', 'Что такое PyQt?', 'PyQt - это набор привязок Python для платформы Qt', None, 1),
            (1, 'theory', 'Какой класс является базовым для всех виджетов в PyQt?', 'QWidget', None, 1),
            (1, 'theory', 'Что такое сигналы и слоты в PyQt?', 'Механизм коммуникации между объектами', None, 1),
            (1, 'theory', 'Как создать главное окно приложения?', 'Наследоваться от QMainWindow', None, 1),
            (1, 'theory', 'Какой менеджер компоновки используется по умолчанию?', 'QWidget не имеет менеджера компоновки по умолчанию', None, 1),
            
            # Практические задания
            (1, 'practice', 'Создайте простое окно с кнопкой "Привет"', 'window = QWidget()\nbutton = QPushButton("Привет", window)\nwindow.show()', None, 2),
            (1, 'practice', 'Добавьте обработчик нажатия кнопки', 'button.clicked.connect(handle_click)', None, 2),
            (1, 'practice', 'Создайте форму с полями ввода имени и возраста', 'layout = QVBoxLayout()\nname_input = QLineEdit()\nage_input = QSpinBox()', None, 2),
            (1, 'practice', 'Реализуйте валидацию формы', 'if name and age >= 18:\n    accept()\nelse:\n    show_error()', None, 2),
            (1, 'practice', 'Добавьте меню в главное окно', 'menubar = self.menuBar()\nfile_menu = menubar.addMenu("File")', None, 2),
            
            # Графические вопросы
            (1, 'graphics', 'Определите, какие виджеты используются на изображении', 'QLabel, QPushButton, QLineEdit', 'lab1_widgets.png', 3),
            (1, 'graphics', 'Найдите ошибку в макете окна', 'Неправильное выравнивание кнопок', 'lab1_layout.png', 3),
            (1, 'graphics', 'Определите тип менеджера компоновки', 'QGridLayout', 'lab1_grid.png', 3),
            (1, 'graphics', 'Укажите неправильно расположенные элементы', 'Метка находится вне контейнера', 'lab1_mistake.png', 3),
            (1, 'graphics', 'Определите структуру диалогового окна', 'Form Dialog с QDialogButtonBox', 'lab1_dialog.png', 3),

            # Лабораторная работа 2
            # Теоретические вопросы
            (2, 'theory', 'Что такое SQL?', 'SQL - язык структурированных запросов для работы с базами данных', None, 1),
            (2, 'theory', 'Какие типы данных поддерживает SQLite?', 'NULL, INTEGER, REAL, TEXT, BLOB', None, 1),
            (2, 'theory', 'Что такое первичный ключ?', 'Уникальный идентификатор записи в таблице', None, 1),
            (2, 'theory', 'Зачем нужны индексы в базе данных?', 'Для ускорения поиска и сортировки данных', None, 1),
            (2, 'theory', 'Что такое транзакция?', 'Набор операций, который должен быть выполнен полностью или не выполнен вообще', None, 1),

            # Практические задания
            (2, 'practice', 'Создайте таблицу users с полями id, name, age', 'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)', None, 2),
            (2, 'practice', 'Напишите запрос для выборки всех пользователей старше 18 лет', 'SELECT * FROM users WHERE age > 18', None, 2),
            (2, 'practice', 'Добавьте нового пользователя в таблицу', 'INSERT INTO users (name, age) VALUES ("John", 25)', None, 2),
            (2, 'practice', 'Обновите возраст пользователя', 'UPDATE users SET age = 26 WHERE name = "John"', None, 2),
            (2, 'practice', 'Удалите пользователя из таблицы', 'DELETE FROM users WHERE name = "John"', None, 2),

            # Графические вопросы
            (2, 'graphics', 'Определите структуру базы данных по схеме', 'Таблицы users и orders связаны через user_id', 'lab2_schema.png', 3),
            (2, 'graphics', 'Найдите ошибку в схеме базы данных', 'Отсутствует внешний ключ', 'lab2_error.png', 3),
            (2, 'graphics', 'Определите тип связи между таблицами', 'Один ко многим (1:N)', 'lab2_relation.png', 3),
            (2, 'graphics', 'Укажите первичные и внешние ключи на схеме', 'PK: id, FK: user_id', 'lab2_keys.png', 3),
            (2, 'graphics', 'Проанализируйте диаграмму базы данных', 'Нормализованная структура с тремя таблицами', 'lab2_diagram.png', 3),

            # Лабораторная работа 3
            # Теоретические вопросы
            (3, 'theory', 'Что такое событийно-ориентированное программирование?', 'Парадигма программирования, где поток выполнения определяется событиями', None, 1),
            (3, 'theory', 'Какие виды layout managers существуют в PyQt?', 'QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout', None, 1),
            (3, 'theory', 'Что такое стили в PyQt?', 'Способ настройки внешнего вида виджетов через CSS-подобный синтаксис', None, 1),
            (3, 'theory', 'Как работает система координат в PyQt?', 'Начало координат в левом верхнем углу, ось Y направлена вниз', None, 1),
            (3, 'theory', 'Что такое модальные и немодальные окна?', 'Модальные блокируют работу с другими окнами, немодальные - нет', None, 1),

            # Практические задания
            (3, 'practice', 'Создайте окно с таблицей данных', 'table = QTableWidget()\ntable.setColumnCount(3)\ntable.setRowCount(5)', None, 2),
            (3, 'practice', 'Добавьте контекстное меню к виджету', 'widget.setContextMenuPolicy(Qt.CustomContextMenu)\nwidget.customContextMenuRequested.connect(show_menu)', None, 2),
            (3, 'practice', 'Реализуйте drag and drop', 'widget.setAcceptDrops(True)\nwidget.dragEnterEvent = handle_drag\nwidget.dropEvent = handle_drop', None, 2),
            (3, 'practice', 'Создайте анимацию перемещения виджета', 'animation = QPropertyAnimation(widget, b"geometry")\nanimation.setDuration(1000)', None, 2),
            (3, 'practice', 'Добавьте всплывающие подсказки', 'widget.setToolTip("Подсказка")\nQToolTip.setFont(QFont("Arial", 12))', None, 2),

            # Графические вопросы
            (3, 'graphics', 'Определите тип используемого layout', 'QGridLayout с вложенными QVBoxLayout', 'lab3_layout.png', 3),
            (3, 'graphics', 'Найдите ошибки в дизайне интерфейса', 'Нарушение принципов UX: неправильные отступы', 'lab3_design.png', 3),
            (3, 'graphics', 'Определите структуру главного окна', 'MainWindow с dock widgets и центральным виджетом', 'lab3_mainwindow.png', 3),
            (3, 'graphics', 'Укажите проблемы с выравниванием виджетов', 'Несогласованные отступы и выравнивание', 'lab3_alignment.png', 3),
            (3, 'graphics', 'Проанализируйте иерархию виджетов', 'Дерево виджетов с вложенными контейнерами', 'lab3_hierarchy.png', 3),
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
    
    def __del__(self):
        """Очистка тестовой базы данных при завершении"""
        if os.path.exists(self.db_path) and self.db_path == 'test.db':
            os.remove(self.db_path)

    def get_random_questions(self, lab_id, count=10):
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

    def start_test(self, student_id, lab_id):
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

    def submit_answer(self, result_id, question_id, answer):
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

    def finish_test(self, result_id):
        """Завершение тестирования"""
        # Обновляем время завершения
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
