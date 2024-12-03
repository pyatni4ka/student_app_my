from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView)
from PyQt6.QtCore import Qt
from ..base_window import BaseWindow
from core.database.manager import DatabaseManager
from .testing_window import TestingWindow

class LabSelectionWindow(BaseWindow):
    def __init__(self, student):
        self.student = student
        self.db = DatabaseManager()
        super().__init__()

    def setup_ui(self):
        self.setWindowTitle('Выбор лабораторной работы')
        self.setGeometry(100, 100, 800, 500)

        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Информация о студенте
        student_info = QLabel(
            f'Студент: {self.student.full_name}\n'
            f'Группа: {self.student.group}'
        )
        student_info.setObjectName('studentInfo')
        layout.addWidget(student_info)

        # Создаем таблицу лабораторных работ
        self.table = QTableWidget()
        self.table.setObjectName('labsTable')
        self.setup_table()
        layout.addWidget(self.table)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('Обновить список', self)
        refresh_btn.setObjectName('secondaryButton')
        refresh_btn.clicked.connect(self.load_labs)
        
        start_btn = QPushButton('Начать выбранную работу', self)
        start_btn.setObjectName('primaryButton')
        start_btn.clicked.connect(self.start_lab)
        
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(start_btn)
        layout.addLayout(buttons_layout)

    def setup_table(self):
        # Настройка таблицы
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            'Название', 'Описание', 'Статус', 'Последний результат'
        ])
        
        # Настройка заголовков
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Включаем сортировку
        self.table.setSortingEnabled(True)
        
        # Настраиваем выделение строк
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Подключаем двойной клик
        self.table.doubleClicked.connect(self.start_lab)
        
        self.load_labs()

    def load_labs(self):
        try:
            # Получаем список лабораторных работ
            labs = self.db.get_available_labs()
            
            self.table.setRowCount(len(labs))
            for i, lab in enumerate(labs):
                # Получаем последний результат для этой работы
                last_result = self.db.get_student_last_result(
                    self.student.id, lab.id
                )
                
                # Заполняем таблицу
                self.table.setItem(i, 0, QTableWidgetItem(lab.name))
                self.table.setItem(i, 1, QTableWidgetItem(lab.description))
                
                # Определяем статус
                status = 'Не начата'
                result = '-'
                if last_result:
                    status = 'Завершена'
                    result = f'{last_result.score:.1f}%'
                
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 2, status_item)
                
                result_item = QTableWidgetItem(result)
                result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 3, result_item)

        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при загрузке списка работ: {str(e)}')

    def start_lab(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            self.show_warning('Предупреждение', 'Выберите лабораторную работу!')
            return

        try:
            lab_name = self.table.item(current_row, 0).text()
            lab = self.db.get_lab_by_name(lab_name)
            
            self.testing_window = TestingWindow(self.student, lab)
            self.testing_window.show()
            self.hide()
            
        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при запуске теста: {str(e)}')
