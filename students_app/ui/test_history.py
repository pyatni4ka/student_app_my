"""Окно истории тестирования"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from utils.questions_db import QuestionsDB
import datetime

class TestHistoryWindow(QWidget):
    def __init__(self, student_id, student_surname, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.student_surname = student_surname
        self.questions_db = QuestionsDB()
        
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle(f'История тестирования - {self.student_surname}')
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel(f'История тестирования студента {self.student_surname}')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Таблица с результатами
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Лабораторная работа',
            'Дата начала',
            'Дата завершения',
            'Баллы',
            'Статус'
        ])
        
        # Растягиваем столбцы
        header = self.table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, header.Stretch)
            
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_history(self):
        """Загрузка истории тестирования"""
        results = self.questions_db.get_test_results(student_id=self.student_id)
        
        # Очищаем таблицу
        self.table.setRowCount(0)
        
        # Заполняем таблицу
        for result in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Название лабораторной работы
            lab_name = QTableWidgetItem(result[2])
            self.table.setItem(row, 0, lab_name)
            
            # Дата начала
            start_time = datetime.datetime.fromisoformat(result[3])
            start_item = QTableWidgetItem(start_time.strftime('%Y-%m-%d %H:%M'))
            self.table.setItem(row, 1, start_item)
            
            # Дата завершения
            if result[4]:  # если тест завершен
                end_time = datetime.datetime.fromisoformat(result[4])
                end_item = QTableWidgetItem(end_time.strftime('%Y-%m-%d %H:%M'))
                self.table.setItem(row, 2, end_item)
            else:
                self.table.setItem(row, 2, QTableWidgetItem('-'))
            
            # Баллы
            points = result[5] if result[5] is not None else 0
            points_item = QTableWidgetItem(str(points))
            self.table.setItem(row, 3, points_item)
            
            # Статус
            status = 'Завершен' if result[4] else 'В процессе'
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 4, status_item)
