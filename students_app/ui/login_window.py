"""Окно входа в систему"""
import os
import sys
import re
import json
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, pyqtSlot
)
from PyQt5.QtGui import QPixmap, QIcon, QKeyEvent, QColor, QFont
from ui.styles import STYLES
from ui.window_manager import WindowManager

class LoginWindow(QMainWindow):
    """Окно входа в систему"""
    
    # Сигналы для валидации
    validation_complete = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.setWindowTitle("Система тестирования | МГТУ им. Н.Э. Баумана")
        self.setFixedSize(1200, 700)  # Фиксированный размер окна
        self.setStyleSheet(STYLES)
        
        # Загружаем иконки
        icon_path = os.path.join("resources", "icons")
        self.setWindowIcon(QIcon(os.path.join(icon_path, "bmstu_logo.png")))
        
        # Словарь для хранения сообщений об ошибках
        self.error_labels = {}
        
        # Путь к файлу с сохраненными данными
        self.settings_file = os.path.join("resources", "settings.json")
        
        # Создаем эффект прозрачности для анимации
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)
        
        # Инициализируем интерфейс
        self.setup_ui()
        
        # Загружаем последнюю использованную группу
        self.load_last_group()
        
        # Анимация появления окна
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Создаем основной виджет и компоновщик
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создаем левую панель
        left_panel = QFrame()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 50, 50, 50)
        left_layout.setSpacing(20)
        
        # Добавляем логотип
        logo_label = QLabel()
        logo_label.setObjectName("logo")
        logo_pixmap = QPixmap(os.path.join("resources", "icons", "bmstu_logo.png"))
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(logo_label)
        
        # Добавляем заголовок
        title_label = QLabel("Система тестирования")
        title_label.setObjectName("title-label")
        title_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_label)
        
        # Добавляем подзаголовок
        subtitle_label = QLabel("МГТУ им. Н.Э. Баумана")
        subtitle_label.setObjectName("subtitle-label")
        subtitle_label.setFont(QFont("Segoe UI", 24))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(subtitle_label)
        
        # Добавляем описание
        description_label = QLabel("Лабораторный практикум\nпо электротехнике")
        description_label.setObjectName("welcome-label")
        description_label.setFont(QFont("Segoe UI", 18))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(description_label)
        
        main_layout.addWidget(left_panel)
        
        # Создаем правую панель
        right_panel = QFrame()
        right_panel.setObjectName("right-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setSpacing(20)
        
        # Создаем форму входа
        form_widget = QFrame()
        form_widget.setObjectName("form-widget")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Добавляем поля ввода
        for field_type, label_text in [
            ("surname", "Фамилия"),
            ("name", "Имя"),
            ("group", "Группа")
        ]:
            # Заголовок поля
            label = QLabel(label_text)
            label.setObjectName("input-label")
            form_layout.addWidget(label)
            
            # Контейнер для поля ввода и иконки
            input_container = QHBoxLayout()
            input_container.setSpacing(0)
            input_container.setContentsMargins(0, 0, 0, 0)
            
            # Иконка
            icon_label = QLabel()
            icon_label.setObjectName("icon")
            icon_name = "user.svg" if field_type in ["surname", "name"] else "group.svg"
            icon_pixmap = QPixmap(os.path.join("resources", "icons", icon_name))
            if not icon_pixmap.isNull():
                icon_pixmap = icon_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(icon_pixmap)
            input_container.addWidget(icon_label)
            
            # Поле ввода
            input_field = QLineEdit()
            input_field.setObjectName("input-field")
            if field_type == "group":
                input_field.setPlaceholderText("Например: ПС4-51")
                setattr(self, "group_input", input_field)
                input_field.textChanged.connect(self.validate_group)
            else:
                input_field.setPlaceholderText("Введите " + label_text.lower())
                setattr(self, f"{field_type}_input", input_field)
                input_field.textChanged.connect(
                    lambda text, field=input_field, type=field_type: 
                    self.validate_name(field, type)
                )
            input_container.addWidget(input_field)
            
            form_layout.addLayout(input_container)
            
            # Метка для ошибок
            error_label = QLabel()
            error_label.setObjectName("error-label")
            self.error_labels[field_type] = error_label
            form_layout.addWidget(error_label)
        
        right_layout.addWidget(form_widget)
        
        # Добавляем кнопки
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("login-button")
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)
        
        # Кнопка входа для преподавателя
        self.teacher_button = QPushButton("Вход для преподавателя")
        self.teacher_button.setObjectName("teacher-button")
        self.teacher_button.clicked.connect(self.handle_teacher_login)
        buttons_layout.addWidget(self.teacher_button)
        
        right_layout.addLayout(buttons_layout)
        
        # Добавляем текущий год
        year_label = QLabel(f"Текущий год: {datetime.now().year}")
        year_label.setObjectName("year-label")
        year_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(year_label)
        
        main_layout.addWidget(right_panel)
        
        # Добавляем эффект тени для окна
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    @pyqtSlot()
    def on_text_changed(self, text):
        """Обработчик изменения текста"""
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            if sender == self.group_input:
                self.validate_group()
            else:
                field_type = "surname" if sender == self.surname_input else "name"
                self.validate_name(sender, field_type)

    def animate_appearance(self):
        """Анимация появления окна"""
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
    
    def animate_exit(self, callback=None):
        """Анимация исчезновения окна"""
        self.exit_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.exit_animation.setDuration(500)
        self.exit_animation.setStartValue(1)
        self.exit_animation.setEndValue(0)
        self.exit_animation.setEasingCurve(QEasingCurve.InOutQuad)
        if callback:
            self.exit_animation.finished.connect(callback)
        self.exit_animation.start()
    
    def load_last_group(self):
        """Загрузка последней использованной группы"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Проверяем, что файл не пустой
                        settings = json.loads(content)
                        last_group = settings.get('last_group', '')
                        if last_group and self.is_valid_group(last_group):
                            self.group_input.setText(last_group)
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
    
    def save_last_group(self, group):
        """Сохранение последней использованной группы"""
        try:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Читаем существующие настройки или создаем новые
            settings = {}
            if os.path.exists(self.settings_file):
                try:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:  # Проверяем, что файл не пустой
                            settings = json.loads(content)
                except json.JSONDecodeError:
                    # Если файл поврежден, начинаем с пустого словаря
                    settings = {}
            
            # Обновляем настройки
            settings['last_group'] = group
            
            # Сохраняем настройки
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")
    
    def is_valid_group(self, group):
        """Проверка валидности номера группы"""
        valid_groups = ['ПС4-41', 'ПС4-51', 'ПС4-42', 'ПС4-52', 'ПС2-41', 'ПС2-51']
        return group in valid_groups
    
    @pyqtSlot()
    def validate_group(self) -> None:
        """Проверка группы"""
        text = self.group_input.text()
        if not text:
            self.error_labels["group"].setText("")
            self.group_input.setStyleSheet("")
            self.validation_complete.emit(False)
            return
            
        pattern = r'^[А-ЯЁ]{2}\d{1}-\d{2}[А-ЯЁ]?$'
        if not re.match(pattern, text):
            self.error_labels["group"].setText("Неверный формат группы")
            self.group_input.setStyleSheet("border-color: #dc3545;")
            self.validation_complete.emit(False)
            return
            
        self.error_labels["group"].setText("")
        self.group_input.setStyleSheet("border-color: #28a745;")
        self.validation_complete.emit(True)

    @pyqtSlot(QLineEdit, str)
    def validate_name(self, field: QLineEdit, field_type: str) -> None:
        """Проверка имени/фамилии"""
        text = field.text()
        if not text:
            self.error_labels[field_type].setText("")
            field.setStyleSheet("")
            self.validation_complete.emit(False)
            return
            
        if not text.replace(" ", "").isalpha():
            self.error_labels[field_type].setText("Допустимы только буквы")
            field.setStyleSheet("border-color: #dc3545;")
            self.validation_complete.emit(False)
            return
            
        self.error_labels[field_type].setText("")
        field.setStyleSheet("border-color: #28a745;")
        self.validation_complete.emit(True)

    def keyPressEvent(self, a0: Optional[QKeyEvent]) -> None:
        """Обработка нажатия клавиш"""
        if a0 and a0.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.handle_login()
        else:
            super().keyPressEvent(a0)

    def show_error(self, field_type, message):
        """Показать сообщение об ошибке"""
        self.error_labels[field_type].setText(message)
        
    def clear_error(self, field_type):
        """Очистить сообщение об ошибке"""
        self.error_labels[field_type].clear()
        
    def validate_all(self):
        """Проверка всех полей"""
        return all([
            self.validate_name(self.surname_input, "surname"),
            self.validate_name(self.name_input, "name"),
            self.validate_group()
        ])
        
    @pyqtSlot()
    def handle_login(self) -> None:
        """Обработка входа студента"""
        if not self.validate_all():
            return

        student_data = {
            'name': self.name_input.text().strip(),
            'surname': self.surname_input.text().strip(),
            'group': self.group_input.text().strip().upper()
        }
        
        # Переход к окну выбора лабораторных работ
        from ui.lab_selection import LabSelectionWindow
        lab_selection = LabSelectionWindow(**student_data)
        WindowManager().show_window(lab_selection)
    
    @pyqtSlot()
    def handle_teacher_login(self) -> None:
        """Обработка входа для преподавателя"""
        from ui.teacher_login_window import TeacherLoginWindow
        WindowManager().show_window(TeacherLoginWindow)
