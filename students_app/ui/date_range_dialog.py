from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QDate
from PyQt5 import uic
import os
from ui import styles

class DateRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Загружаем UI
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'forms', 'date_range_dialog.ui'), self)

        # Применяем стили
        self.start_date_label.setStyleSheet(styles.LABEL_STYLE)
        self.end_date_label.setStyleSheet(styles.LABEL_STYLE)
        self.start_date.setStyleSheet(styles.INPUT_STYLE)
        self.end_date.setStyleSheet(styles.INPUT_STYLE)
        self.save_button.setStyleSheet(styles.BUTTON_STYLE)
        self.exit_button.setStyleSheet(styles.BUTTON_STYLE)

        # Устанавливаем начальные даты
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())

        # Подключаем сигналы
        self.save_button.clicked.connect(self.accept)
        self.exit_button.clicked.connect(self.reject)

    def get_date_range(self):
        """Возвращает выбранный диапазон дат"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        return start_date, end_date
