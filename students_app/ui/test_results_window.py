"""Окно результатов тестирования"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database.db_manager import DatabaseManager

class TestResultsWindow(QDialog):
    """Окно с результатами тестирования"""

    def __init__(self, user_data: dict, lab_number: int, lab_topic: str,
                 score: int, max_score: int, time_spent: int, db_manager: DatabaseManager):
        super().__init__()

        self.user_data = user_data
        self.db_manager = db_manager
        self.setWindowTitle("Результаты тестирования")
        self.setMinimumSize(400, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Информация о студенте
        student_frame = QFrame()
        student_frame.setFrameShape(QFrame.StyledPanel)
        student_layout = QVBoxLayout(student_frame)

        student_info = QLabel(f"Студент: {user_data['username']}")
        student_info.setFont(QFont('Segoe UI', 11))
        group_info = QLabel(f"Группа: {user_data['group_number']}")
        group_info.setFont(QFont('Segoe UI', 11))

        student_layout.addWidget(student_info)
        student_layout.addWidget(group_info)

        # Информация о тесте
        test_frame = QFrame()
        test_frame.setFrameShape(QFrame.StyledPanel)
        test_layout = QVBoxLayout(test_frame)

        lab_info = QLabel(f"Лабораторная работа №{lab_number}")
        lab_info.setFont(QFont('Segoe UI', 11))
        topic_info = QLabel(f"Тема: {lab_topic}")
        topic_info.setFont(QFont('Segoe UI', 11))
        topic_info.setWordWrap(True)

        test_layout.addWidget(lab_info)
        test_layout.addWidget(topic_info)

        # Результат
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.StyledPanel)
        result_layout = QVBoxLayout(result_frame)

        result_label = QLabel(f"Результат: {score} из {max_score} баллов")
        result_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        result_label.setAlignment(Qt.AlignCenter)

        # Время прохождения
        minutes = time_spent // 60
        seconds = time_spent % 60
        time_label = QLabel(f"Время прохождения: {minutes:02d}:{seconds:02d}")
        time_label.setFont(QFont('Segoe UI', 11))
        time_label.setAlignment(Qt.AlignCenter)

        result_layout.addWidget(result_label)
        result_layout.addWidget(time_label)

        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.setFixedWidth(120)
        close_button.clicked.connect(self.return_to_main)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        # Добавляем все элементы в главный layout
        layout.addWidget(student_frame)
        layout.addWidget(test_frame)
        layout.addWidget(result_frame)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def return_to_main(self):
        """Возврат на главное окно"""
        from .lab_selection import LabSelectionWindow
        self.accept()
        # Создаем и показываем окно выбора лабораторных работ
        self.lab_window = LabSelectionWindow(self.user_data, self.db_manager)
        self.lab_window.show()
