"""Окно выбора лабораторной работы"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                           QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from utils.questions_db import QuestionsDB
from .test_history import TestHistoryWindow
from .test_window import TestWindow
from .window_manager import WindowManager

class LabSelectionWindow(QWidget):
    def __init__(self, student_name, student_surname, student_group, student_id=None, parent=None):
        super().__init__(parent)
        self.student_name = student_name
        self.student_surname = student_surname
        self.student_group = student_group
        # Если student_id не передан, создаем его из имени, фамилии и группы
        self.student_id = student_id or f"{student_surname}_{student_name}_{student_group}"
        self.questions_db = QuestionsDB()
        self.setup_ui()
        self.load_labs()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle('Выбор лабораторной работы')
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        # Информация о студенте
        student_info = QLabel(f'Студент: {self.student_name} {self.student_surname}\nГруппа: {self.student_group}')
        student_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(student_info)

        # Список лабораторных работ
        self.labs_list = QListWidget()
        self.labs_list.itemDoubleClicked.connect(self.start_lab)
        layout.addWidget(QLabel('Доступные лабораторные работы:'))
        layout.addWidget(self.labs_list)

        # Кнопки
        button_layout = QVBoxLayout()
        
        # Кнопка начала тестирования
        self.start_button = QPushButton('Начать тестирование')
        self.start_button.clicked.connect(self.start_lab)
        button_layout.addWidget(self.start_button)
        
        # Кнопка истории тестирования
        self.history_button = QPushButton('История тестирования')
        self.history_button.clicked.connect(self.show_history)
        button_layout.addWidget(self.history_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_labs(self):
        """Загрузка списка доступных лабораторных работ"""
        # Очищаем список
        self.labs_list.clear()
        
        # Получаем все лабораторные работы
        labs = self.questions_db.get_all_labs()
        
        # Добавляем в список
        for lab_id, name, description in labs:
            self.labs_list.addItem(f"{name} - {description}")

    def show_history(self):
        """Показать историю тестирования"""
        self.history_window = TestHistoryWindow(
            student_id=self.student_id,
            student_surname=self.student_surname,
            parent=self
        )
        WindowManager().show_window(self.history_window)

    def start_lab(self):
        """Начало тестирования выбранной лабораторной работы"""
        current_item = self.labs_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 
                              'Пожалуйста, выберите лабораторную работу')
            return

        # Получаем ID выбранной лабораторной работы
        lab_index = self.labs_list.row(current_item)
        labs = self.questions_db.get_all_labs()
        lab_id = labs[lab_index][0]

        # Проверяем, нет ли незавершенного теста
        results = self.questions_db.get_test_results(
            student_id=self.student_id, 
            lab_id=lab_id
        )
        
        result_id = None
        for result in results:
            if not result[4]:  # end_time is None
                reply = QMessageBox.question(
                    self,
                    'Незавершенный тест',
                    'У вас есть незавершенный тест. Хотите продолжить его?',
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    result_id = result[0]
                    break
                else:
                    # Создаем новый тест
                    break

        # Если нет незавершенного теста или пользователь отказался его продолжать
        if not result_id:
            result_id = self.questions_db.start_test(self.student_id, lab_id)
        
        # Открываем окно тестирования
        test_window = TestWindow(
            student_id=self.student_id,
            lab_id=lab_id,
            result_id=result_id,
            parent=self
        )
        WindowManager().show_window(test_window)
