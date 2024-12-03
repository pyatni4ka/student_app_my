from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QPushButton, QFrame, QHeaderView)
from PyQt6.QtCore import Qt
from ..base_window import BaseWindow
from core.database.manager import DatabaseManager

class TeacherDatabaseWindow(BaseWindow):
    def __init__(self):
        self.db = DatabaseManager()
        super().__init__()

    def setup_ui(self):
        self.setWindowTitle('База данных результатов (Преподаватель)')
        self.setGeometry(100, 100, 1000, 600)

        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Панель фильтров
        filter_frame = QFrame()
        filter_frame.setObjectName('filterFrame')
        filter_layout = QHBoxLayout(filter_frame)

        # Фильтр по группе
        self.group_filter = QComboBox()
        self.group_filter.setObjectName('filterCombo')
        self.group_filter.setMinimumWidth(200)
        filter_layout.addWidget(self.group_filter)

        # Фильтр по лабораторной работе
        self.lab_filter = QComboBox()
        self.lab_filter.setObjectName('filterCombo')
        self.lab_filter.setMinimumWidth(200)
        filter_layout.addWidget(self.lab_filter)

        # Кнопка применения фильтров
        apply_btn = QPushButton('Применить фильтры')
        apply_btn.setObjectName('primaryButton')
        apply_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_btn)

        # Кнопка сброса фильтров
        reset_btn = QPushButton('Сбросить фильтры')
        reset_btn.setObjectName('secondaryButton')
        reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_btn)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setObjectName('resultsTable')
        self.setup_table()
        layout.addWidget(self.table)

        # Загружаем данные для фильтров и таблицы
        self.load_filters()
        self.load_results()

    def setup_table(self):
        columns = [
            'Студент',
            'Группа',
            'Лабораторная работа',
            'Дата',
            'Результат',
            'Правильных ответов',
            'Время выполнения'
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Настройка заголовков
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Студент
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Группа
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Лаб. работа
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Дата
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Результат
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Прав. ответов
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Время

        # Настройка выделения и сортировки
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)

    def load_filters(self):
        try:
            # Загружаем список групп
            groups = self.db.get_all_groups()
            self.group_filter.addItem('Все группы')
            self.group_filter.addItems([g.name for g in groups])

            # Загружаем список лабораторных работ
            labs = self.db.get_all_labs()
            self.lab_filter.addItem('Все работы')
            self.lab_filter.addItems([l.name for l in labs])

        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при загрузке фильтров: {str(e)}')

    def load_results(self):
        try:
            # Получаем выбранные фильтры
            group = self.group_filter.currentText()
            if group == 'Все группы':
                group = None

            lab_name = self.lab_filter.currentText()
            lab_id = None
            if lab_name != 'Все работы':
                lab = self.db.get_lab_by_name(lab_name)
                lab_id = lab.id if lab else None

            # Получаем результаты с учетом фильтров
            results = self.db.get_all_results(group, lab_id)

            # Заполняем таблицу
            self.table.setRowCount(len(results))
            for i, result in enumerate(results):
                # Студент
                self.table.setItem(i, 0, QTableWidgetItem(result.student.full_name))
                # Группа
                self.table.setItem(i, 1, QTableWidgetItem(result.student.group))
                # Лабораторная работа
                self.table.setItem(i, 2, QTableWidgetItem(result.lab_work.name))
                # Дата
                self.table.setItem(i, 3, 
                    QTableWidgetItem(result.end_time.strftime("%d.%m.%Y %H:%M"))
                )
                # Результат
                score_item = QTableWidgetItem(f'{result.score:.1f}%')
                score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 4, score_item)
                # Правильных ответов
                correct = sum(1 for a in result.answers if a.is_correct)
                correct_item = QTableWidgetItem(f'{correct}/5')
                correct_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 5, correct_item)
                # Время выполнения
                duration = result.end_time - result.start_time
                minutes = duration.seconds // 60
                seconds = duration.seconds % 60
                time_item = QTableWidgetItem(f'{minutes:02d}:{seconds:02d}')
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 6, time_item)

        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при загрузке результатов: {str(e)}')

    def apply_filters(self):
        self.load_results()

    def reset_filters(self):
        self.group_filter.setCurrentText('Все группы')
        self.lab_filter.setCurrentText('Все работы')
        self.load_results()
