from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from ..base_window import BaseWindow
from core.database.manager import DatabaseManager

class ResultsWindow(BaseWindow):
    def __init__(self, student, test_result):
        self.student = student
        self.test_result = test_result
        self.db = DatabaseManager()
        super().__init__()

    def setup_ui(self):
        self.setWindowTitle('Результаты тестирования')
        self.setGeometry(100, 100, 800, 600)

        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Информация о студенте
        student_frame = QFrame()
        student_frame.setObjectName('studentInfoFrame')
        student_layout = QVBoxLayout(student_frame)

        student_info = QLabel(
            f'Студент: {self.student.full_name}\n'
            f'Группа: {self.student.group}'
        )
        student_info.setObjectName('studentInfo')
        student_layout.addWidget(student_info)

        layout.addWidget(student_frame)

        # Результат текущего теста
        result_frame = QFrame()
        result_frame.setObjectName('resultFrame')
        result_layout = QVBoxLayout(result_frame)

        # Заголовок результата
        result_header = QLabel(f'Результаты работы "{self.test_result.lab_work.name}"')
        result_header.setObjectName('resultHeader')
        result_layout.addWidget(result_header)

        # Детали результата
        result_details = QLabel(
            f'Набрано баллов: {self.test_result.score:.1f}%\n'
            f'Время выполнения: {self.format_duration()}\n'
            f'Дата: {self.test_result.end_time.strftime("%d.%m.%Y %H:%M")}'
        )
        result_details.setObjectName('resultDetails')
        result_layout.addWidget(result_details)

        layout.addWidget(result_frame)

        # История результатов
        history_frame = QFrame()
        history_frame.setObjectName('historyFrame')
        history_layout = QVBoxLayout(history_frame)

        history_label = QLabel('История результатов:')
        history_label.setObjectName('historyHeader')
        history_layout.addWidget(history_label)

        self.history_table = QTableWidget()
        self.history_table.setObjectName('historyTable')
        self.setup_history_table()
        history_layout.addWidget(self.history_table)

        layout.addWidget(history_frame)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        new_test_btn = QPushButton('Пройти другой тест')
        new_test_btn.setObjectName('primaryButton')
        new_test_btn.clicked.connect(self.start_new_test)
        
        close_btn = QPushButton('Завершить работу')
        close_btn.setObjectName('secondaryButton')
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(new_test_btn)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)

    def setup_history_table(self):
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            'Лабораторная работа',
            'Дата',
            'Результат',
            'Время выполнения'
        ])

        # Настройка заголовков
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.load_history()

    def load_history(self):
        try:
            # Получаем историю результатов
            results = self.db.get_student_results(self.student.id)
            
            self.history_table.setRowCount(len(results))
            for i, result in enumerate(results):
                self.history_table.setItem(
                    i, 0, QTableWidgetItem(result.lab_work.name)
                )
                self.history_table.setItem(
                    i, 1, 
                    QTableWidgetItem(
                        result.end_time.strftime("%d.%m.%Y %H:%M")
                    )
                )
                
                score_item = QTableWidgetItem(f'{result.score:.1f}%')
                score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setItem(i, 2, score_item)
                
                duration = self.format_duration(result)
                duration_item = QTableWidgetItem(duration)
                duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setItem(i, 3, duration_item)
                
        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при загрузке истории: {str(e)}')

    def format_duration(self, result=None):
        if result is None:
            result = self.test_result
            
        duration = result.end_time - result.start_time
        minutes = duration.seconds // 60
        seconds = duration.seconds % 60
        return f'{minutes:02d}:{seconds:02d}'

    def start_new_test(self):
        from .lab_selection_window import LabSelectionWindow
        self.lab_window = LabSelectionWindow(self.student)
        self.lab_window.show()
        self.close()
