"""Окно тестирования"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
                           QRadioButton, QButtonGroup, QMessageBox,
                           QProgressBar, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from utils.questions_db import QuestionsDB
from typing import Dict

class TestWindow(QMainWindow):
    def __init__(self, student_id, lab_id, result_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.lab_id = lab_id
        self.result_id = result_id
        self.questions_db = QuestionsDB()
        self.current_question_index = 0
        self.questions = []
        self.answers: Dict[int, str] = {}  # question_id -> answer_str
        self.remaining_time = QuestionsDB.TEST_DURATION * 60  # в секундах
        
        self.setup_ui()
        self.load_questions()
        self.start_timer()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Таймер
        timer_layout = QHBoxLayout()
        self.time_label = QLabel('Оставшееся время: 20:00')
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(QuestionsDB.TEST_DURATION * 60)
        self.progress_bar.setValue(QuestionsDB.TEST_DURATION * 60)
        timer_layout.addWidget(self.time_label)
        timer_layout.addWidget(self.progress_bar)
        layout.addLayout(timer_layout)
        
        # Текст вопроса
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)
        
        # Варианты ответов
        self.answers_group = QButtonGroup()
        self.answers_group.setExclusive(True)
        self.answers_layout = QVBoxLayout()
        layout.addLayout(self.answers_layout)
        
        # Кнопки навигации
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton('Предыдущий')
        self.prev_button.clicked.connect(self.prev_question)
        self.next_button = QPushButton('Следующий')
        self.next_button.clicked.connect(self.next_question)
        self.finish_button = QPushButton('Завершить')
        self.finish_button.clicked.connect(self.finish_test)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.finish_button)
        layout.addLayout(nav_layout)
        
    def load_questions(self):
        """Загрузка вопросов"""
        self.questions = self.questions_db.get_random_questions(self.lab_id)
        self.show_current_question()
        
    def show_current_question(self):
        """Отображение текущего вопроса"""
        if not self.questions:
            return
            
        # Очищаем старые варианты ответов
        for i in reversed(range(self.answers_layout.count())): 
            widget = self.answers_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        self.answers_group = QButtonGroup()
        self.answers_group.setExclusive(True)
        
        # Получаем текущий вопрос
        question = self.questions[self.current_question_index]
        question_id = question[0]
        
        # Создаем радиокнопки для вариантов ответов
        for i, answer in enumerate(['A', 'B', 'C', 'D']):
            radio = QRadioButton(answer)
            self.answers_layout.addWidget(radio)
            self.answers_group.addButton(radio, i)
            if question_id in self.answers and self.answers[question_id] == str(i):
                radio.setChecked(True)
                
        self.question_label.setText(f"Вопрос {self.current_question_index + 1} из {len(self.questions)}:\n{question[1]}")
        
        # Обновляем состояние кнопок
        self.prev_button.setEnabled(self.current_question_index > 0)
        self.next_button.setEnabled(self.current_question_index < len(self.questions) - 1)
        
    def start_timer(self):
        """Запуск таймера"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # каждую секунду
        
    def update_timer(self):
        """Обновление таймера"""
        self.remaining_time -= 1
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_label.setText(f'Оставшееся время: {minutes:02d}:{seconds:02d}')
        self.progress_bar.setValue(self.remaining_time)
        
        if self.remaining_time <= 0:
            self.timer.stop()
            QMessageBox.warning(self, 'Время истекло', 'Время тестирования истекло!')
            self.finish_test()
        
    def submit_answer(self):
        """Сохранение текущего ответа"""
        checked_button = self.answers_group.checkedButton()
        if checked_button:
            answer_index = self.answers_group.id(checked_button)
            current_question = self.questions[self.current_question_index]
            question_id = current_question[0]
            answer_str = str(answer_index)
            
            # Store answer in dictionary
            self.answers[question_id] = answer_str
            
            # Save to database
            self.questions_db.submit_answer(
                self.result_id,
                question_id,
                answer_str
            )
        
    def prev_question(self):
        """Переход к предыдущему вопросу"""
        if self.current_question_index > 0:
            self.submit_answer()
            self.current_question_index -= 1
            self.show_current_question()
        
    def next_question(self):
        """Переход к следующему вопросу"""
        if self.current_question_index < len(self.questions) - 1:
            self.submit_answer()
            self.current_question_index += 1
            self.show_current_question()
        
    def finish_test(self):
        """Завершение тестирования"""
        self.submit_answer()
        self.timer.stop()
        
        # Проверяем, на все ли вопросы даны ответы
        unanswered = sum(1 for answer in self.answers.values() if answer is None)
        if unanswered > 0:
            reply = QMessageBox.question(
                self,
                'Завершение теста',
                f'Вы не ответили на {unanswered} вопросов. Вы уверены, что хотите завершить тест?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Завершаем тест в базе данных
        total_points = self.questions_db.finish_test(self.result_id)
        
        QMessageBox.information(
            self,
            'Тест завершен',
            f'Тестирование завершено!\nНабрано баллов: {total_points}'
        )
        
        # Возвращаемся к окну выбора лабораторных работ
        from ui.lab_selection import LabSelectionWindow
        from ui.window_manager import WindowManager
        WindowManager().show_window(self.parent())
        self.close()
