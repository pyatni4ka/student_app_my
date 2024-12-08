"""Окно входа для студента"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from utils.student_db import StudentDB
from .lab_selection import LabSelectionWindow
import logging

class StudentLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_db = StudentDB()
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Вход в систему тестирования")
        self.setFixedSize(600, 500)  # Увеличили размер окна
        
        layout = QVBoxLayout()
        layout.setSpacing(25)  # Увеличили отступы между элементами
        layout.setContentsMargins(40, 40, 40, 40)  # Увеличили отступы по краям
        
        # Создаем шрифт для заголовков
        header_font = QFont()
        header_font.setPointSize(16)  # Увеличили размер шрифта
        header_font.setBold(True)
        
        # Создаем иконки для полей ввода
        surname_icon = QLabel()
        surname_icon.setPixmap(QIcon(":/icons/user.png").pixmap(32, 32))
        surname_icon.setFixedSize(40, 40)
        surname_icon.setStyleSheet("QLabel { padding: 5px; }")
        
        name_icon = QLabel()
        name_icon.setPixmap(QIcon(":/icons/user.png").pixmap(32, 32))
        name_icon.setFixedSize(40, 40)
        name_icon.setStyleSheet("QLabel { padding: 5px; }")
        
        group_icon = QLabel()
        group_icon.setPixmap(QIcon(":/icons/group.png").pixmap(32, 32))
        group_icon.setFixedSize(40, 40)
        group_icon.setStyleSheet("QLabel { padding: 5px; }")
        
        # Фамилия
        surname_container = QVBoxLayout()
        surname_container.setSpacing(8)  # Отступ между меткой и полем
        
        surname_label = QLabel("ФАМИЛИЯ")
        surname_label.setFont(header_font)
        surname_label.setStyleSheet("color: #2C3E50; margin-bottom: 5px;")
        
        self.surname_edit = QLineEdit()
        self.surname_edit.setFixedHeight(45)  # Увеличили высоту поля
        self.surname_edit.setMinimumWidth(400)  # Установили минимальную ширину
        self.surname_edit.setPlaceholderText("Введите фамилия")
        self.surname_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                font-size: 14pt;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        
        surname_input_layout = QHBoxLayout()
        surname_input_layout.addWidget(surname_icon)
        surname_input_layout.addWidget(self.surname_edit)
        surname_container.addLayout(surname_input_layout)
        
        surname_container.addWidget(surname_label)
        
        # Имя
        name_container = QVBoxLayout()
        name_container.setSpacing(8)
        
        name_label = QLabel("ИМЯ")
        name_label.setFont(header_font)
        name_label.setStyleSheet("color: #2C3E50; margin-bottom: 5px;")
        
        self.name_edit = QLineEdit()
        self.name_edit.setFixedHeight(45)  # Увеличили высоту поля
        self.name_edit.setMinimumWidth(400)  # Установили минимальную ширину
        self.name_edit.setPlaceholderText("Введите имя")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                font-size: 14pt;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        
        name_input_layout = QHBoxLayout()
        name_input_layout.addWidget(name_icon)
        name_input_layout.addWidget(self.name_edit)
        name_container.addLayout(name_input_layout)
        
        name_container.addWidget(name_label)
        
        # Группа
        group_container = QVBoxLayout()
        group_container.setSpacing(8)
        
        group_label = QLabel("ГРУППА")
        group_label.setFont(header_font)
        group_label.setStyleSheet("color: #2C3E50; margin-bottom: 5px;")
        
        self.group_edit = QLineEdit()
        self.group_edit.setFixedHeight(45)  # Увеличили высоту поля
        self.group_edit.setMinimumWidth(400)  # Установили минимальную ширину
        self.group_edit.setPlaceholderText("Введите группу")
        self.group_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                font-size: 14pt;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        
        group_input_layout = QHBoxLayout()
        group_input_layout.addWidget(group_icon)
        group_input_layout.addWidget(self.group_edit)
        group_container.addLayout(group_input_layout)
        
        group_container.addWidget(group_label)
        
        # Кнопка входа
        login_button = QPushButton("ВОЙТИ")
        login_button.setFixedSize(400, 55)  # Увеличили размер кнопки
        login_button.setFont(QFont('Arial', 14, QFont.Bold))  # Увеличили шрифт кнопки
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        login_button.clicked.connect(self.handle_login)
        
        # Добавляем виджеты в layout с правильным выравниванием
        layout.addStretch(1)
        layout.addLayout(surname_container)
        layout.addLayout(name_container)
        layout.addLayout(group_container)
        layout.addSpacing(20)
        
        # Центрируем кнопку
        button_container = QHBoxLayout()
        button_container.addStretch(1)
        button_container.addWidget(login_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)
        
        layout.addStretch(1)
        
        self.setLayout(layout)

    def open_lab_selection(self, student_id, first_name, last_name, group):
        """Открытие окна выбора лабораторной работы"""
        self.lab_selection = LabSelectionWindow(
            name=first_name,
            surname=last_name,
            group=group
        )
        self.lab_selection.show()
        self.hide()

    def handle_login(self):
        """Обработка входа студента"""
        surname = self.surname_edit.text().strip()
        name = self.name_edit.text().strip()
        group = self.group_edit.text().strip()
        
        # Валидация полей
        if not all([surname, name, group]):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")
            return
            
        # Проверка на спецсимволы
        if not all(x.isalpha() or x.isspace() for x in surname + name):
            QMessageBox.warning(self, "Ошибка", "Имя и фамилия могут содержать только буквы и пробелы")
            return
            
        # Проверка формата группы (например, ПС4-51)
        if not self.is_valid_group(group):
            QMessageBox.warning(self, "Ошибка", "Неверный формат группы. Пример: ПС4-51")
            return
            
        try:
            # Проверка существования студента в базе
            if not self.student_db.check_student(surname, name, group):
                QMessageBox.warning(self, "Ошибка", "Студент не найден в базе данных")
                return
                
            # Если все проверки пройдены, открываем окно выбора лабораторной
            self.accept()
            self.window_manager.show_window(
                LabSelectionWindow,
                student_info={'surname': surname, 'name': name, 'group': group}
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при входе: {str(e)}")
            logging.error(f"Ошибка при входе студента: {str(e)}", exc_info=True)
            
    def is_valid_group(self, group):
        """Проверка формата группы"""
        import re
        pattern = r'^[А-ЯЁ]{2}\d-\d{2}$'
        return bool(re.match(pattern, group))
