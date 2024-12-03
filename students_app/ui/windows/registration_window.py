from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QInputDialog)
from PyQt6.QtCore import Qt
from ..base_window import BaseWindow
from core.database.manager import DatabaseManager
from .lab_selection_window import LabSelectionWindow
from .teacher_database_window import TeacherDatabaseWindow

class RegistrationWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle('Регистрация студента')
        self.setGeometry(100, 100, 400, 300)

        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header с кнопкой преподавателя
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        teacher_btn = QPushButton('База данных (для преподавателя)', self)
        teacher_btn.setObjectName('teacherButton')
        teacher_btn.clicked.connect(self.show_teacher_database)
        header_layout.addWidget(teacher_btn)
        layout.addLayout(header_layout)

        # Форма регистрации
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        # Создаем поля ввода с подписями
        fields = [
            ('surname_edit', 'Фамилия:'),
            ('name_edit', 'Имя:'),
            ('group_edit', 'Группа:'),
            ('year_edit', 'Год поступления:')
        ]

        for field_name, label_text in fields:
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setObjectName('formLabel')
            edit = QLineEdit()
            edit.setObjectName('formInput')
            setattr(self, field_name, edit)
            
            field_layout.addWidget(label)
            field_layout.addWidget(edit)
            form_layout.addLayout(field_layout)

        layout.addLayout(form_layout)

        # Кнопка регистрации
        register_btn = QPushButton('Начать работу', self)
        register_btn.setObjectName('primaryButton')
        register_btn.clicked.connect(self.register_student)
        layout.addWidget(register_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Добавляем растяжку в конец
        layout.addStretch()

    def register_student(self):
        # Получаем данные из полей
        surname = self.surname_edit.text().strip()
        name = self.name_edit.text().strip()
        group = self.group_edit.text().strip()
        year = self.year_edit.text().strip()

        # Проверяем заполнение полей
        if not all([surname, name, group, year]):
            self.show_warning('Ошибка', 'Все поля должны быть заполнены!')
            return

        try:
            # Сохраняем данные студента
            student = self.db.add_student(
                full_name=f"{surname} {name}",
                group=group,
                admission_year=int(year)
            )
            
            # Открываем окно выбора лабораторной работы
            self.lab_window = LabSelectionWindow(student)
            self.lab_window.show()
            self.hide()
            
        except ValueError:
            self.show_error('Ошибка', 'Год поступления должен быть числом!')
        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при регистрации: {str(e)}')

    def show_teacher_database(self):
        password, ok = QInputDialog.getText(
            self, 'Авторизация', 
            'Введите пароль преподавателя:', 
            QLineEdit.EchoMode.Password
        )
        if ok:
            # TODO: Реализовать безопасную проверку пароля
            if password == "teacher_password":  # Временное решение
                self.teacher_window = TeacherDatabaseWindow()
                self.teacher_window.show()
            else:
                self.show_warning('Ошибка', 'Неверный пароль!')
