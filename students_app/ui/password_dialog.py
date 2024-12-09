from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import os
from ui import styles

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Загружаем UI
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'forms', 'password_dialog.ui'), self)

        # Применяем стили
        self.password_label.setStyleSheet(styles.LABEL_STYLE)
        self.password_input.setStyleSheet(styles.INPUT_STYLE)
        self.ok_button.setStyleSheet(styles.BUTTON_STYLE)
        self.cancel_button.setStyleSheet(styles.BUTTON_STYLE)

        # Подключаем сигналы
        self.ok_button.clicked.connect(self.check_password)
        self.cancel_button.clicked.connect(self.reject)

        # Устанавливаем фокус на поле пароля
        self.password_input.setFocus()

    def check_password(self):
        """Проверка пароля"""
        if self.password_input.text() == "admin":
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль")
            self.password_input.clear()
            self.password_input.setFocus()
