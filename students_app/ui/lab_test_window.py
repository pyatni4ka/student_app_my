"""Окно тестирования для лабораторной работы"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QButtonGroup,
    QStackedWidget, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from loguru import logger
from .test_results_window import TestResultsWindow
from database.db_manager import DatabaseManager

class LabTestWindow(QMainWindow):
    """Окно тестирования"""

    def __init__(self, user_data: dict, lab_number: int, lab_topic: str, db_manager: DatabaseManager = None):
        super().__init__()
        self.user_data = user_data
        self.lab_number = lab_number
        self.lab_topic = lab_topic
        self.db = db_manager or DatabaseManager()

        # Инициализация переменных для теста
        self.current_question = 0
        self.questions = []
        self.answer_groups = []
        self.correct_answers = []
        self.initial_time = 20 * 60  # 20 минут в секундах
        self.time_left = self.initial_time

        # Загрузка вопросов для теста
        self.load_questions()

        # Инициализация UI
        self.setWindowTitle(f"Лабораторная работа №{lab_number}")
        self.setMinimumSize(800, 600)

        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # Добавляем таймер
        self.timer_label = QLabel()
        self.timer_label.setFont(QFont('Segoe UI', 12))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.update_timer_display()

        # Создаем и запускаем таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # Обновление каждую секунду

        # Добавляем компоненты на форму
        main_layout.addWidget(self.timer_label)

        # Создаем стек для вопросов
        self.questions_stack = QStackedWidget()
        self.create_question_pages()
        main_layout.addWidget(self.questions_stack)

        # Панель навигации
        nav_panel = self.create_navigation_panel()
        main_layout.addWidget(nav_panel)

        logger.info(f"Окно тестирования для ЛР{lab_number} инициализировано")

    def load_questions(self):
        """Загрузка вопросов для теста"""
        # Здесь должна быть загрузка вопросов из базы данных
        # Пока используем тестовые данные
        self.questions = [
            {
                'text': 'Что такое Python?',
                'options': [
                    'Язык программирования высокого уровня',
                    'Система управления базами данных',
                    'Операционная система',
                    'Текстовый редактор'
                ],
                'correct': 0
            },
            {
                'text': 'Какой оператор используется для определения функции в Python?',
                'options': [
                    'function',
                    'def',
                    'func',
                    'define'
                ],
                'correct': 1
            },
            {
                'text': 'Какой тип данных используется для хранения последовательности элементов в Python?',
                'options': [
                    'int',
                    'str',
                    'list',
                    'char'
                ],
                'correct': 2
            },
            {
                'text': 'Как объявить пустой список в Python?',
                'options': [
                    'list()',
                    '[]',
                    'new List()',
                    '{}'
                ],
                'correct': 1
            },
            {
                'text': 'Какой метод используется для добавления элемента в конец списка?',
                'options': [
                    'add()',
                    'insert()',
                    'append()',
                    'push()'
                ],
                'correct': 2
            }
        ]

        # Сохраняем правильные ответы
        self.correct_answers = [q['correct'] for q in self.questions]

    def create_question_pages(self):
        """Создание страниц с вопросами"""
        for i, question in enumerate(self.questions, 1):
            page = QWidget()
            layout = QVBoxLayout(page)

            # Номер вопроса
            question_number = QLabel(f"Вопрос {i} из {len(self.questions)}")
            question_number.setFont(QFont('Segoe UI', 12, QFont.Bold))
            question_number.setAlignment(Qt.AlignCenter)

            # Текст вопроса
            question_text = QLabel(question['text'])
            question_text.setFont(QFont('Segoe UI', 11))
            question_text.setWordWrap(True)
            question_text.setAlignment(Qt.AlignLeft)

            # Группа радиокнопок для ответов
            answer_group = QButtonGroup()
            self.answer_groups.append(answer_group)

            # Создаем радиокнопки для каждого варианта ответа
            options_layout = QVBoxLayout()
            for j, option in enumerate(question['options']):
                radio = QRadioButton(option)
                radio.setFont(QFont('Segoe UI', 10))
                answer_group.addButton(radio, j)
                options_layout.addWidget(radio)

            # Добавляем все элементы на страницу
            layout.addWidget(question_number)
            layout.addWidget(question_text)
            layout.addLayout(options_layout)
            layout.addStretch()

            self.questions_stack.addWidget(page)

    def create_navigation_panel(self):
        """Создание панели навигации"""
        nav_panel = QFrame()
        layout = QHBoxLayout(nav_panel)

        # Кнопка "Предыдущий"
        self.prev_button = QPushButton("← Предыдущий")
        self.prev_button.clicked.connect(self.prev_question)
        self.prev_button.setEnabled(False)

        # Кнопки выбора вопросов
        questions_layout = QHBoxLayout()
        self.question_buttons = []
        for i in range(len(self.questions)):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, x=i: self.goto_question(x))
            self.question_buttons.append(btn)
            questions_layout.addWidget(btn)

        # Кнопка "Следующий"
        self.next_button = QPushButton("Следующий →")
        self.next_button.clicked.connect(self.next_question)

        # Кнопка "Завершить"
        self.finish_button = QPushButton("Завершить")
        self.finish_button.clicked.connect(self.finish_test)
        self.finish_button.setStyleSheet("background-color: #28a745; color: white;")

        layout.addWidget(self.prev_button)
        layout.addStretch()
        layout.addLayout(questions_layout)
        layout.addStretch()
        layout.addWidget(self.next_button)
        layout.addWidget(self.finish_button)

        return nav_panel

    def update_timer_display(self):
        """Обновление отображения таймера"""
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.setText(f"Оставшееся время: {minutes:02d}:{seconds:02d}")

    def update_timer(self):
        """Обновление таймера"""
        self.time_left -= 1
        self.update_timer_display()

        if self.time_left <= 0:
            self.finish_test()

    def prev_question(self):
        """Переход к предыдущему вопросу"""
        if self.current_question > 0:
            self.save_current_answer()
            self.current_question -= 1
            self.questions_stack.setCurrentIndex(self.current_question)
            self.update_navigation()

    def next_question(self):
        """Переход к следующему вопросу"""
        if self.current_question < len(self.questions) - 1:
            self.save_current_answer()
            self.current_question += 1
            self.questions_stack.setCurrentIndex(self.current_question)
            self.update_navigation()

    def goto_question(self, number: int):
        """Переход к конкретному вопросу"""
        if 0 <= number < len(self.questions):
            self.save_current_answer()
            self.current_question = number
            self.questions_stack.setCurrentIndex(number)
            self.update_navigation()

    def save_current_answer(self):
        """Сохранение текущего ответа"""
        if self.current_question < len(self.answer_groups):
            group = self.answer_groups[self.current_question]
            checked_button = group.checkedId()
            if checked_button != -1:
                # Сохраняем ответ
                pass

    def update_navigation(self):
        """Обновление состояния кнопок навигации"""
        self.prev_button.setEnabled(self.current_question > 0)
        self.next_button.setEnabled(self.current_question < len(self.questions) - 1)

        # Подсвечиваем текущий вопрос
        for i, btn in enumerate(self.question_buttons):
            if i == self.current_question:
                btn.setStyleSheet("background-color: #007bff; color: white;")
            else:
                btn.setStyleSheet("")

    def finish_test(self):
        """Завершение теста"""
        # Проверяем, все ли вопросы отвечены
        unanswered = []
        for i in range(len(self.questions)):
            if not any(btn.isChecked() for btn in self.answer_groups[i].buttons()):
                unanswered.append(i + 1)

        if unanswered:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Пожалуйста, ответьте на следующие вопросы: {', '.join(map(str, unanswered))}"
            )
            return

        # Останавливаем таймер
        self.timer.stop()
        time_spent = self.initial_time - self.time_left

        # Подсчитываем результат
        score = 0
        max_score = len(self.questions)
        for i, group in enumerate(self.answer_groups):
            for j, button in enumerate(group.buttons()):
                if button.isChecked() and j == self.correct_answers[i]:
                    score += 1

        # Сохраняем результат в базу данных
        self.db.save_test_result(
            user_id=self.user_data['id'],
            lab_number=self.lab_number,
            score=score,
            max_score=max_score,
            time_spent=time_spent
        )

        # Показываем окно с результатами
        self.result_window = TestResultsWindow(
            self.user_data,
            self.lab_number,
            self.lab_topic,
            score,
            max_score,
            time_spent,
            self.db
        )
        self.result_window.show()
        self.close()
