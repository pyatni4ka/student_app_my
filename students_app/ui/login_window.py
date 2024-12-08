"""Окно входа в систему"""
import os
import sys
import re
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QIcon, QKeyEvent, QColor
from ui.styles import STYLES
from ui.window_manager import WindowManager
from datetime import datetime

class LoginWindow(QMainWindow):
    """Окно входа в систему"""
    
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.setWindowTitle("Система тестирования | МГТУ им. Н.Э. Баумана")
        self.setMinimumSize(900, 600)
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
        # Устанавливаем иконку окна
        self.setWindowIcon(QIcon(os.path.join("resources", "icons", "bmstu_logo.png")))
        
        # Создаем основной виджет и компоновщик
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создаем левую панель
        left_panel = QWidget()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Добавляем логотип
        logo_label = QLabel()
        logo_label.setObjectName("logo")
        logo_pixmap = QPixmap(os.path.join("resources", "icons", "bmstu_logo.png"))
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label)
        
        # Добавляем заголовок
        title_label = QLabel("Система тестирования\nМГТУ им. Н.Э. Баумана")
        title_label.setObjectName("title-label")
        left_layout.addWidget(title_label)
        
        # Добавляем подзаголовок
        subtitle_label = QLabel("Лабораторный практикум\nпо Электротехнике")
        subtitle_label.setObjectName("subtitle-label")
        left_layout.addWidget(subtitle_label)
        
        # Добавляем приветственный текст
        welcome_label = QLabel("Добро пожаловать в систему тестирования!\nЗдесь вы можете пройти тестирование по лабораторным\nработам и получить оценку своих знаний.")
        welcome_label.setObjectName("welcome-label")
        left_layout.addWidget(welcome_label)
        
        main_layout.addWidget(left_panel)
        
        # Создаем правую панель
        right_panel = QWidget()
        right_panel.setObjectName("right-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(5)
        
        # Создаем контейнер для поля фамилии
        surname_label = QLabel("Фамилия:")
        surname_label.setObjectName("input-label")
        right_layout.addWidget(surname_label)
        
        surname_container = QHBoxLayout()
        surname_container.setSpacing(10)
        
        # Добавляем иконку пользователя
        surname_icon = QLabel()
        surname_icon.setObjectName("icon")
        surname_icon.setAccessibleName("icon")
        surname_pixmap = QPixmap(os.path.join("resources", "icons", "user.svg"))
        if not surname_pixmap.isNull():
            surname_pixmap = surname_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            surname_icon.setPixmap(surname_pixmap)
        surname_container.addWidget(surname_icon)
        
        # Добавляем поле фамилии
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Иванов")
        self.surname_input.setObjectName("input-field")
        self.surname_input.textChanged.connect(lambda: self.validate_name(self.surname_input, "surname"))
        surname_container.addWidget(self.surname_input)
        right_layout.addLayout(surname_container)
        
        self.error_labels["surname"] = QLabel()
        self.error_labels["surname"].setObjectName("error-label")
        right_layout.addWidget(self.error_labels["surname"])
        
        # Создаем контейнер для поля имени
        name_label = QLabel("Имя:")
        name_label.setObjectName("input-label")
        right_layout.addWidget(name_label)
        
        name_container = QHBoxLayout()
        name_container.setSpacing(10)
        
        # Добавляем иконку пользователя
        name_icon = QLabel()
        name_icon.setObjectName("icon")
        name_icon.setAccessibleName("icon")
        name_pixmap = QPixmap(os.path.join("resources", "icons", "user.svg"))
        if not name_pixmap.isNull():
            name_pixmap = name_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            name_icon.setPixmap(name_pixmap)
        name_container.addWidget(name_icon)
        
        # Добавляем поле имени
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Иван")
        self.name_input.setObjectName("input-field")
        self.name_input.textChanged.connect(lambda: self.validate_name(self.name_input, "name"))
        name_container.addWidget(self.name_input)
        right_layout.addLayout(name_container)
        
        self.error_labels["name"] = QLabel()
        self.error_labels["name"].setObjectName("error-label")
        right_layout.addWidget(self.error_labels["name"])
        
        # Создаем контейнер для поля группы
        group_label = QLabel("Группа:")
        group_label.setObjectName("input-label")
        right_layout.addWidget(group_label)
        
        group_container = QHBoxLayout()
        group_container.setSpacing(10)
        
        # Добавляем иконку группы
        group_icon = QLabel()
        group_icon.setObjectName("icon")
        group_icon.setAccessibleName("icon")
        group_pixmap = QPixmap(os.path.join("resources", "icons", "group.svg"))
        if not group_pixmap.isNull():
            group_pixmap = group_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            group_icon.setPixmap(group_pixmap)
        group_container.addWidget(group_icon)
        
        # Добавляем поле группы
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("ПС4-51")
        self.group_input.setObjectName("input-field")
        self.group_input.textChanged.connect(self.validate_group)
        group_container.addWidget(self.group_input)
        right_layout.addLayout(group_container)
        
        self.error_labels["group"] = QLabel()
        self.error_labels["group"].setObjectName("error-label")
        right_layout.addWidget(self.error_labels["group"])
        
        # Добавляем текущий год
        year_label = QLabel(f"Текущий год: {datetime.now().year}")
        year_label.setObjectName("year-label")
        year_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(year_label)
        
        # Добавляем кнопки
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("login-button")
        self.login_button.clicked.connect(self.handle_login)
        right_layout.addWidget(self.login_button)
        
        self.teacher_button = QPushButton("Вход для преподавателя")
        self.teacher_button.setObjectName("teacher-button")
        self.teacher_button.clicked.connect(self.handle_teacher_login)
        right_layout.addWidget(self.teacher_button)
        
        main_layout.addWidget(right_panel)
        
        # Добавляем эффект тени для окна
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
        
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
    
    def validate_name(self, input_field, field_type):
        """Валидация имени/фамилии"""
        text = input_field.text()
        if not text:
            self.show_error(field_type, "Поле обязательно для заполнения")
            return False
        if not re.match(r'^[А-ЯЁа-яё-]+$', text):
            self.show_error(field_type, "Используйте только русские буквы")
            return False
        self.clear_error(field_type)
        return True
        
    def validate_group(self):
        """Валидация номера группы"""
        text = self.group_input.text()
        if not text:
            self.show_error("group", "Поле обязательно для заполнения")
            return False
            
        # Паттерн для проверки формата ПС{2,4}-{41,42,51,52}
        if not re.match(r'^ПС[24]-[45][12]$', text):
            self.show_error("group", "Формат: ПС4-51 или ПС2-41")
            return False
            
        # Проверка допустимых комбинаций
        valid_groups = ['ПС4-41', 'ПС4-51', 'ПС4-42', 'ПС4-52', 'ПС2-41', 'ПС2-51']
        if text not in valid_groups:
            self.show_error("group", "Недопустимый номер группы")
            return False
            
        self.clear_error("group")
        return True
        
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
        
    def handle_login(self):
        """Обработка входа студента"""
        if self.validate_all():
            # Сохраняем группу
            self.save_last_group(self.group_input.text())
            
            # Анимация выхода перед показом сообщения и переходом к следующему окну
            def show_welcome():
                QMessageBox.information(
                    self,
                    "Успешный вход",
                    f"Добро пожаловать, {self.name_input.text()} {self.surname_input.text()}!"
                )
                # Переход к окну выбора лабораторных работ
                from ui.lab_selection import LabSelectionWindow
                lab_selection = LabSelectionWindow(
                    student_name=self.name_input.text(),
                    student_surname=self.surname_input.text(),
                    student_group=self.group_input.text()
                )
                WindowManager().show_window(lab_selection)
            
            self.animate_exit(show_welcome)
    
    def handle_teacher_login(self):
        """Обработка входа для преподавателя"""
        from ui.teacher_login_window import TeacherLoginWindow
        WindowManager().show_window(TeacherLoginWindow)

    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Определяем, какое поле сейчас в фокусе
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QLineEdit):
                # Если это последнее поле, выполняем вход
                if focused_widget == self.group_input:
                    self.handle_login()
                # Иначе переходим к следующему полю
                else:
                    self.focusNextChild()
        else:
            super().keyPressEvent(event)
