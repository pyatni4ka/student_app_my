"""Окно выбора лабораторной работы"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                           QPushButton, QMessageBox, QDesktopWidget, QHBoxLayout)
from PyQt5.QtCore import Qt
from utils.questions_db import QuestionsDB
from .test_history import TestHistoryWindow
from .test_window import TestWindow
from .window_manager import WindowManager

class LabSelectionWindow(QWidget):
    def __init__(self, name, surname, group, parent=None):
        super().__init__(parent)
        self.student_name = name
        self.student_surname = surname
        self.student_group = group
        self.student_id = f"{surname}_{name}_{group}"  # Упрощенный идентификатор
        self.questions_db = QuestionsDB()
        self.setup_ui()
        self.load_labs()
        self.showFullScreen()  # Разворачиваем окно на весь экран

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle('Выбор лабораторной работы')
        self.setMinimumWidth(1920)  # Устанавливаем минимальную ширину для FullHD
        self.setMinimumHeight(1080)  # Устанавливаем минимальную высоту для FullHD
        
        # Создаем основной вертикальный layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Добавляем отступы
        layout.setSpacing(20)  # Увеличиваем расстояние между элементами

        # Информация о студенте
        student_info = QLabel(f'Студент: {self.student_name} {self.student_surname}\nГруппа: {self.student_group}')
        student_info.setAlignment(Qt.AlignCenter)
        student_info.setStyleSheet("QLabel { font-size: 18pt; }")
        layout.addWidget(student_info)

        # Заголовок списка лабораторных работ
        labs_label = QLabel('Доступные лабораторные работы:')
        labs_label.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; }")
        layout.addWidget(labs_label)

        # Список лабораторных работ
        self.labs_list = QListWidget()
        self.labs_list.setStyleSheet("""
            QListWidget {
                font-size: 14pt;
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.labs_list.itemDoubleClicked.connect(self.start_lab)
        layout.addWidget(self.labs_list)

        # Создаем горизонтальный layout для кнопок
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # Расстояние между кнопками
        
        # Кнопка возврата в главное меню
        self.back_button = QPushButton('Вернуться в главное меню')
        self.back_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                padding: 10px 20px;
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.back_button.clicked.connect(self.return_to_main)
        button_layout.addWidget(self.back_button)
        
        # Кнопка начала тестирования
        self.start_button = QPushButton('Начать тестирование')
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                padding: 10px 20px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
        """)
        self.start_button.clicked.connect(self.start_lab)
        button_layout.addWidget(self.start_button)
        
        # Кнопка истории тестирования
        self.history_button = QPushButton('История тестирования')
        self.history_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                padding: 10px 20px;
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #0b590b;
            }
        """)
        self.history_button.clicked.connect(self.show_history)
        button_layout.addWidget(self.history_button)

        # Добавляем layout с кнопками в основной layout
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def return_to_main(self):
        """Возврат в главное меню"""
        from .login_window import LoginWindow
        WindowManager().show_window(LoginWindow, parent=self)
        self.close()

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
