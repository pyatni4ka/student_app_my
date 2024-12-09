"""Окно тестирования"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                           QRadioButton, QButtonGroup, QPushButton, QMessageBox)
from PyQt5.QtCore import QTimer
from PyQt5 import uic
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from typing import List, Tuple, Dict
from students_app.utils.questions_db import QuestionsDB

class TestWindow(QMainWindow):
    def __init__(self, student_id, lab_id, result_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.lab_id = lab_id
        self.result_id = result_id
        self.questions_db = QuestionsDB()
        self.current_question_index = 0
        self.questions: List[Tuple] = []
        self.answers: Dict[int, str] = {}
        self.remaining_time = QuestionsDB.TEST_DURATION * 60

        # Load UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(current_dir, "test_window.ui"), self)

        self.load_questions()
        self.create_question_widgets()
        self.start_timer()
        self.show_question(0)
        self.update_navigation_buttons()
        self.showFullScreen()

        # Add export PDF button
        self.export_button = QPushButton("Экспорт в PDF", self)
        self.export_button.clicked.connect(self.export_to_pdf)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.layout().addWidget(self.export_button)

    def load_questions(self):
        """Загрузка вопросов"""
        self.questions = self.questions_db.get_random_questions(self.lab_id)
        self.progress_indicator.setMaximum(len(self.questions))

    def create_question_widgets(self):
        for i, question in enumerate(self.questions):
            # Create question page
            page = QWidget()
            layout = QVBoxLayout(page)

            # Question text
            question_label = QLabel(f"Вопрос {i + 1} из {len(self.questions)}:\n{question[1]}")
            question_label.setWordWrap(True)
            question_label.setStyleSheet("QLabel { font-size: 16pt; padding: 20px; }")
            layout.addWidget(question_label)

            # Answer options
            button_group = QButtonGroup(self)
            answers = ['A', 'B', 'C', 'D']  # Замените на реальные варианты ответов
            for j, option in enumerate(answers):
                radio = QRadioButton(option)
                radio.clicked.connect(lambda checked, q=i: self.save_answer(q))
                button_group.addButton(radio, j)
                layout.addWidget(radio)

            layout.addStretch()
            self.question_stack.addWidget(page)

    def show_question(self, index):
        self.current_question_index = index
        self.question_stack.setCurrentIndex(index)
        self.progress_indicator.setValue(index + 1)

        # Restore saved answer if exists
        if self.answers.get(index) is not None:
            buttons = self.question_stack.currentWidget().findChildren(QRadioButton)
            buttons[self.answers[index]].setChecked(True)

        self.update_navigation_buttons()

    def save_answer(self, question_index):
        buttons = self.question_stack.widget(question_index).findChildren(QRadioButton)
        for i, button in enumerate(buttons):
            if button.isChecked():
                self.answers[question_index] = i
                break

    def show_previous_question(self):
        if self.current_question_index > 0:
            self.show_question(self.current_question_index - 1)

    def show_next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.show_question(self.current_question_index + 1)

    def update_navigation_buttons(self):
        self.prev_button.setEnabled(self.current_question_index > 0)
        self.next_button.setEnabled(self.current_question_index < len(self.questions) - 1)

        # Show finish button on last question
        self.finish_button.setVisible(self.current_question_index == len(self.questions) - 1)

    def start_timer(self):
        """Запуск таймера"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.update_timer()

    def update_timer(self):
        """Обновление таймера"""
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.finish_test()
        else:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.time_label.setText(f"⏱ {minutes:02d}:{seconds:02d}")
            self.time_progress.setValue(self.remaining_time)

        # Изменяем цвет при малом количестве времени
        if self.remaining_time <= 300:  # последние 5 минут
            self.time_label.setStyleSheet("""
                QLabel {
                    font-size: 18pt;
                    color: #e74c3c;
                    font-weight: bold;
                }
            """)
            self.time_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-size: 14pt;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #e74c3c;
                    border-radius: 3px;
                }
            """)

    def finish_test(self):
        """Завершение тестирования"""
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

        # Сохраняем ответы
        for i, answer in self.answers.items():
            question_id = self.questions[i][0]
            answer_str = str(answer)
            self.questions_db.submit_answer(
                self.result_id,
                question_id,
                answer_str
            )

        # Завершаем тест в базе данных
        total_points = self.questions_db.finish_test(self.result_id)

        QMessageBox.information(
            self,
            'Тест завершен',
            f'Тестирование завершено!\nНабрано баллов: {total_points}'
        )

        # Возвращаемся к окну выбора лабораторных работ
        from ui.lab_selection import LabSelectionWindow
        self.lab_window = LabSelectionWindow(self.student_id, self.db_manager)
        self.lab_window.show()
        self.close()

    def export_to_pdf(self):
        """Экспорт результатов тестов в PDF"""
        try:
            # Создаем имя файла с текущей датой
            filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            # Создаем PDF документ
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # Заголовок
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Результаты тестирования")

            # Информация о студенте
            c.setFont("Helvetica", 12)
            student_info = self.questions_db.get_student_info(self.student_id)
            c.drawString(50, height - 80, f"Студент: {student_info['name']}")
            c.drawString(50, height - 100, f"Группа: {student_info['group']}")

            # Информация о тесте
            lab_info = self.questions_db.get_lab_info(self.lab_id)
            c.drawString(50, height - 120, f"Лабораторная работа: {lab_info['name']}")
            c.drawString(50, height - 140, f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

            # Результаты
            results = self.questions_db.get_test_results(self.result_id)
            c.drawString(50, height - 170, f"Результат: {results['score']}%")
            c.drawString(50, height - 190, f"Правильных ответов: {results['correct_answers']}")
            c.drawString(50, height - 210, f"Всего вопросов: {results['total_questions']}")

            c.save()

            QMessageBox.information(self, "Успех", f"Результаты сохранены в файл {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF: {str(e)}")
