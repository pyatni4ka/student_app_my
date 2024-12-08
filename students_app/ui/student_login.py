"""Окно входа для студента"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox)
from utils.student_db import StudentDB
from .lab_selection import LabSelectionWindow

class StudentLoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_db = StudentDB()
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle('Вход для студента')
        layout = QVBoxLayout()

        # Поля ввода
        self.last_name_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.group_edit = QLineEdit()

        # Добавляем поля и метки
        layout.addWidget(QLabel('Фамилия:'))
        layout.addWidget(self.last_name_edit)
        layout.addWidget(QLabel('Имя:'))
        layout.addWidget(self.first_name_edit)
        layout.addWidget(QLabel('Группа:'))
        layout.addWidget(self.group_edit)

        # Кнопка входа
        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def open_lab_selection(self, student_id, first_name, last_name, group):
        """Открытие окна выбора лабораторной работы"""
        self.lab_selection = LabSelectionWindow(
            student_id=student_id,
            student_name=f"{last_name} {first_name}",
            student_group=group
        )
        self.lab_selection.show()
        self.hide()

    def handle_login(self):
        """Обработка входа студента"""
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        group = self.group_edit.text().strip()

        # Проверяем заполнение полей
        if not all([first_name, last_name, group]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля')
            return

        # Проверяем корректность группы
        if not self.student_db.validate_group(group):
            QMessageBox.warning(self, 'Ошибка', 
                              'Неверный формат группы.\nПример: ПС4-51 или ПС4-42')
            return

        # Ищем студента в базе
        student = self.student_db.find_student(first_name, last_name, group)

        if student:
            # Студент найден
            student_id, current_group = student
            needs_update, new_group = self.student_db.check_and_update_semester(
                student_id, current_group
            )

            if needs_update:
                # Спрашиваем о переходе на следующий семестр
                reply = QMessageBox.question(
                    self,
                    'Обновление семестра',
                    f'Вы перешли на новый семестр?\nВаша новая группа: {new_group}',
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self.student_db.update_student_group(student_id, new_group)
                    group = new_group
                    QMessageBox.information(
                        self, 'Успех', 
                        f'Группа обновлена на {new_group}'
                    )
                else:
                    return

            # Открываем окно выбора лабораторной работы
            self.open_lab_selection(student_id, first_name, last_name, group)
            
        else:
            # Студент не найден, предлагаем создать новую учетную запись
            reply = QMessageBox.question(
                self,
                'Создание учетной записи',
                'Учетная запись не найдена. Создать новую?',
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                student_id = self.student_db.add_student(first_name, last_name, group)
                QMessageBox.information(
                    self, 'Успех', 
                    'Учетная запись успешно создана'
                )
                # Открываем окно выбора лабораторной работы
                self.open_lab_selection(student_id, first_name, last_name, group)
            else:
                return
