"""Окно входа в систему"""
import os
import re
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox, QGraphicsOpacityEffect, QFileDialog
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, pyqtSignal
)
from PyQt5.QtGui import QPixmap, QIcon, QKeyEvent
from PyQt5 import uic
from ui.lab_selection import LabSelectionWindow
from database.db_manager import DatabaseManager
from loguru import logger

class LoginWindow(QMainWindow):
    """Окно входа в систему"""

    # Сигналы для валидации
    validation_complete = pyqtSignal(bool)

    def __init__(self, db_manager: DatabaseManager, parent=None, timestamp: str = '2024-12-09T11:39:27+03:00'):
        super().__init__(parent)

        # Load the UI file
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'forms', 'login_window.ui'), self)

        # Загружаем логотип
        logo_label = self.findChild(QLabel, 'logo_label')
        logo_path = os.path.join("resources", "icons", "bmstu_logo.png")
        if os.path.exists(logo_path):
            try:
                logo_pixmap = QPixmap(logo_path)
                logo_label.setPixmap(logo_pixmap)
            except Exception as e:
                logger.error(f"Ошибка при загрузке логотипа: {e}")

        # Инициализация базы данных
        self.db_manager = db_manager

        # Словарь для хранения сообщений об ошибках
        self.error_labels = {}

        # Путь к файлу с сохраненными данными
        self.settings_file = os.path.join("resources", "settings.json")

        # Создаем эффект прозрачности для анимации
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)

        # Загружаем последнюю использованную группу
        self.load_last_group()

        # Анимация появления окна
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        # Настройки окна
        self.setWindowTitle("Система тестирования | МГТУ им. Н.Э. Баумана")
        self.setFixedSize(1200, 700)  # Фиксированный размер окна

        # Загружаем иконки
        icon_path = os.path.join("resources", "icons")
        icon_file = os.path.join(icon_path, "bmstu_logo.png")
        if os.path.exists(icon_file):
            try:
                self.setWindowIcon(QIcon(icon_file))
            except Exception as e:
                logger.error(f"Ошибка при загрузке иконки окна: {e}")

        # Устанавливаем фокус на поле фамилии
        self.findChild(QLineEdit, 'surname_input').setFocus()

        # Подключаем валидацию полей
        self.findChild(QLineEdit, 'surname_input').textChanged.connect(self.validate_surname)
        self.findChild(QLineEdit, 'name_input').textChanged.connect(self.validate_name)
        self.findChild(QLineEdit, 'group_input').textChanged.connect(self.validate_group)

        # Remove teacher login button if exists
        teacher_button = self.findChild(QPushButton, 'teacher_button')
        if teacher_button:
            teacher_button.hide()
            teacher_button.deleteLater()

        # Подключаем кнопку входа
        self.login_button = self.findChild(QPushButton, 'login_button')
        if self.login_button:
            self.login_button.clicked.connect(self.validate_and_login)

        # Подключаем кнопку экспорта PDF
        self.export_pdf_button = self.findChild(QPushButton, 'export_pdf_button')
        if self.export_pdf_button:
            self.export_pdf_button.clicked.connect(self.export_to_pdf)

        # Устанавливаем текущую локальную дату и время
        self.current_time = datetime.now().isoformat() + '+03:00'

        logger.info("Окно входа инициализировано")

    def validate_surname(self, text: str = None) -> bool:
        """Валидация фамилии"""
        if text is None:
            text = self.findChild(QLineEdit, 'surname_input').text().strip()
        error_label = self.findChild(QLabel, 'surname_error')
        if not error_label:
            return True

        if not text:
            error_label.setText("Поле обязательно для заполнения")
            return False

        if not re.match(r'^[А-ЯЁ][а-яё]+(-[А-ЯЁ][а-яё]+)?$', text):
            error_label.setText("Только русские буквы, первая заглавная")
            return False

        error_label.setText("")
        return True

    def validate_name(self, text: str = None) -> bool:
        """Валидация имени"""
        if text is None:
            text = self.findChild(QLineEdit, 'name_input').text().strip()
        error_label = self.findChild(QLabel, 'name_error')
        if not error_label:
            return True

        if not text:
            error_label.setText("Поле обязательно для заполнения")
            return False

        if not re.match(r'^[А-ЯЁ][а-яё]+(-[А-ЯЁ][а-яё]+)?$', text):
            error_label.setText("Только русские буквы, первая заглавная")
            return False

        error_label.setText("")
        return True

    def validate_group(self, text: str = None) -> bool:
        """Валидация номера группы"""
        if text is None:
            text = self.findChild(QLineEdit, 'group_input').text()
        text = text.strip().upper()

        error_label = self.findChild(QLabel, 'group_error')
        if not error_label:
            return True

        # Проверка на пустое значение
        if not text:
            error_label.setText("Поле обязательно для заполнения")
            return False

        # Проверка формата
        if not re.match(r'^[А-Я]{2}\d{1,2}-\d{2}[А-Я]?$', text):
            error_label.setText("Формат: ПС4-51")
            return False

        error_label.setText("")
        return True

    def show_error(self, message: str):
        """Показать сообщение об ошибке"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText(message)
        error_box.exec_()

    def validate_and_login(self):
        """Проверка введенных данных и вход в систему"""
        group = self.findChild(QLineEdit, 'group_input').text().strip()
        surname = self.findChild(QLineEdit, 'surname_input').text().strip()
        name = self.findChild(QLineEdit, 'name_input').text().strip()

        # Проверка наличия всех данных
        if not all([group, surname, name]):
            self.show_error("Пожалуйста, заполните все поля")
            return

        # Проверка формата группы
        if not re.match(r'^[А-Я]{2}\d{1,2}-\d{2}[А-Я]?$', group):
            self.show_error("Неверный формат группы (например: ПС4-51)")
            self.findChild(QLineEdit, 'group_input').setFocus()
            return

        # Создаем имя пользователя
        username = f"{surname} {name}"

        # Проверяем существует ли пользователь
        user = self.db_manager.verify_user(username)

        if user is None:
            # Если пользователя нет, создаем новую учетную запись
            if self.create_new_account(username, group):
                QMessageBox.information(self, "Успех", "Учетная запись успешно создана!")
                user = self.db_manager.verify_user(username)
            else:
                self.show_error("Не удалось создать учетную запись")
                return

        # Если все проверки пройдены, сохраняем данные и открываем главное окно
        self.save_last_group(group)

        # Открываем окно выбора лабораторных работ
        self.lab_window = LabSelectionWindow(user, self.db_manager)
        self.lab_window.show()
        self.close()

    def create_new_account(self, username: str, group: str) -> bool:
        """Создание новой учетной записи"""
        try:
            # В данном случае пароль не нужен, так как авторизация по ФИО
            return self.db_manager.add_user(username=username,
                                          password="",
                                          group_number=group,
                                          role='student')
        except Exception as e:
            logger.error(f"Ошибка при создании учетной записи: {e}")
            return False

    def load_last_group(self) -> None:
        """Загрузка последней использованной группы"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    last_group = settings.get('last_group', '')
                    if last_group:
                        group_input = self.findChild(QLineEdit, 'group_input')
                        if group_input:
                            group_input.setText(last_group)
        except Exception as e:
            logger.error(f"Ошибка при загрузке последней группы: {e}")

    def save_last_group(self, group: str) -> None:
        """Сохранение последней использованной группы"""
        try:
            settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            settings['last_group'] = group
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Ошибка при сохранении последней группы: {e}")

    def export_to_pdf(self) -> None:
        """Экспорт данных в PDF"""
        try:
            group = self.findChild(QLineEdit, 'group_input').text().strip()
            surname = self.findChild(QLineEdit, 'surname_input').text().strip()
            name = self.findChild(QLineEdit, 'name_input').text().strip()
            if not all([group, surname, name]):
                self.show_error("Заполните все поля перед экспортом")
                return
            file_dialog = QFileDialog(self)
            file_dialog.setDefaultSuffix("pdf")
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Сохранить PDF",
                f"{surname}_{name}_{group}.pdf",
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            c = canvas.Canvas(file_path, pagesize=A4)
            c.setTitle(f"Данные студента {surname} {name}")
            c.drawString(100, 750, f"Группа: {group}")
            c.drawString(100, 730, f"Фамилия: {surname}")
            c.drawString(100, 710, f"Имя: {name}")
            c.drawString(100, 690, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
            c.save()
            QMessageBox.information(self, "Успех", "PDF файл успешно создан!")
        except Exception as e:
            logger.error(f"Ошибка при экспорте в PDF: {e}")
            self.show_error("Не удалось создать PDF файл")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.validate_and_login()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        """Обработка закрытия окна"""
        group = self.findChild(QLineEdit, 'group_input').text().strip()
        if group:
            self.save_last_group(group)
        event.accept()
