"""Окно входа для студента"""
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import os
import re
import logging
from pathlib import Path

from utils.student_db import StudentDB
from .lab_selection import LabSelectionWindow

# Путь к UI файлу
UI_PATH = Path(os.path.dirname(__file__)) / "student_login.ui"

class StudentLoginDialog(QDialog):
    """Класс окна входа для студента"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_db = StudentDB()

        # Загружаем UI
        uic.loadUi(UI_PATH, self)

        # Подключаем обработчики событий
        self.login_button.clicked.connect(self.handle_login)
        self.surname_edit.returnPressed.connect(self.handle_login)
        self.name_edit.returnPressed.connect(self.handle_login)
        self.group_edit.returnPressed.connect(self.handle_login)

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
        pattern = r'^[А-ЯЁ]{2}\d-\d{2}$'
        return bool(re.match(pattern, group))
