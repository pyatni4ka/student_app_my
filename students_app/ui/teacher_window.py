"""Окно для преподавателя"""
import os
import sys
import logging
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QMenu,
    QComboBox, QToolBar, QAction, QFileDialog, QDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QTextDocument, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from utils.export import DataExporter
from utils.archive_manager import ArchiveManager
from ui.window_manager import WindowManager
from ui.stats_window import StatsWindow

logger = logging.getLogger(__name__)

class ArchiveDialog(QDialog):
    """Диалог просмотра архива"""
    def __init__(self, archived_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Архив")
        self.setMinimumSize(800, 600)
        self.setup_ui(archived_data)
    
    def setup_ui(self, archived_data):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # +1 для даты архивации
        self.table.setHorizontalHeaderLabels([
            "Фамилия", "Имя", "Группа", "Год", "Лабораторная работа", 
            "Результат", "Дата архивации"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Заполняем таблицу
        self.table.setRowCount(len(archived_data))
        for i, item in enumerate(archived_data):
            data = item["data"]
            for j, value in enumerate(data):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            # Добавляем дату архивации
            self.table.setItem(i, 6, QTableWidgetItem(item["archive_date"]))
        
        layout.addWidget(self.table)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class TeacherWindow(QMainWindow):
    """Класс окна преподавателя"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система тестирования | МГТУ им. Н.Э. Баумана")
        self.setMinimumSize(1200, 800)
        
        # Инициализируем архив
        self.archive_manager = ArchiveManager()
        
        # Инициализируем компоненты
        self.init_ui_components()
        
        # Настраиваем автосохранение
        self.setup_autosave()
        
        # Обновляем данные
        self.update_table()
    
    def init_ui_components(self):
        """Инициализация компонентов интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Создаем верхнюю панель с информацией
        self.setup_header(main_layout)
        
        # Создаем панель инструментов
        self.setup_toolbar()
        
        # Создаем поиск
        self.setup_search(main_layout)
        
        # Создаем таблицу результатов
        self.setup_table(main_layout)
        
        # Создаем панель с кнопками
        self.setup_buttons(main_layout)
    
    def setup_header(self, layout):
        """Настройка заголовка"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавляем логотип
        logo_label = QLabel()
        logo_label.setObjectName("logo-small")
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "resources", "icons", "bmstu_logo.svg")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(
                QSize(200, 200),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("МГТУ")
            logo_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(logo_label)
        
        # Добавляем заголовок
        title_label = QLabel("Панель преподавателя")
        title_label.setObjectName("header-title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Добавляем селектор семестра
        semester_label = QLabel("Семестр:")
        self.semester_combo = QComboBox()
        self.semester_combo.addItems(["Весенний 2024", "Осенний 2024"])
        self.semester_combo.currentTextChanged.connect(self.update_table)
        
        header_layout.addWidget(semester_label)
        header_layout.addWidget(self.semester_combo)
        
        # Добавляем кнопку выхода
        self.logout_button = QPushButton("Выйти")
        self.logout_button.setObjectName("logout-button")
        self.logout_button.clicked.connect(self.handle_logout)
        header_layout.addWidget(self.logout_button)
        
        layout.addWidget(header)
    
    def setup_toolbar(self):
        """Настройка панели инструментов"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Добавляем действия
        actions = [
            ("Статистика", "stats.svg", self.show_stats),
            ("Печать", "print.svg", self.handle_print),
            ("Фильтры", "filter.svg", self.show_filters),
            ("Архив", "archive.svg", self.show_archive)
        ]
        
        for title, icon, handler in actions:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "resources", "icons", icon)
            action = QAction(QIcon(icon_path), title, self)
            action.triggered.connect(handler)
            toolbar.addAction(action)
    
    def setup_search(self, layout):
        """Настройка поиска"""
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по всем полям...")
        self.search_input.textChanged.connect(self.filter_table)
        
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
    
    def setup_table(self, layout):
        """Настройка таблицы результатов"""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Фамилия", "Имя", "Группа", "Год", "Лабораторная работа", "Результат"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.MultiSelection)
        
        layout.addWidget(self.results_table)
    
    def setup_buttons(self, layout):
        """Настройка кнопок"""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Кнопка экспорта
        self.export_button = QPushButton("Экспорт")
        self.export_button.setObjectName("export-button")
        
        self.export_menu = QMenu(self)
        export_formats = {
            "PDF": "Экспортировать в PDF",
            "Excel": "Экспортировать в Excel",
            "CSV": "Экспортировать в CSV"
        }
        
        for format_name, display_text in export_formats.items():
            action = self.export_menu.addAction(display_text)
            action.triggered.connect(lambda checked, f=format_name: self.handle_export(f))
        
        self.export_button.setMenu(self.export_menu)
        buttons_layout.addWidget(self.export_button)
        
        # Кнопка архивации
        archive_button = QPushButton("Архивировать выбранное")
        archive_button.clicked.connect(self.archive_selected)
        buttons_layout.addWidget(archive_button)
        
        buttons_layout.addStretch()
        layout.addWidget(buttons_widget)
    
    def setup_autosave(self):
        """Настройка автосохранения"""
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(300000)  # Каждые 5 минут
    
    def update_table(self):
        """Обновление данных таблицы"""
        test_data = [
            ["Иванов", "Иван Иванович", "ИУ7-54Б", "2024", "Лабораторная работа №1", "85%"],
            ["Петров", "Петр Петрович", "ИУ7-54Б", "2024", "Лабораторная работа №1", "92%"],
            ["Сидоров", "Сергей Сергеевич", "ИУ7-54Б", "2024", "Лабораторная работа №2", "78%"]
        ]
        
        self.results_table.setRowCount(len(test_data))
        for i, row_data in enumerate(test_data):
            for j, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if j == 4:  # Lab work column
                    item.setData(Qt.ItemDataRole.UserRole, int(value.split("№")[1]))
                elif j == 5:  # Result column
                    item.setData(Qt.ItemDataRole.UserRole, float(value.strip("%")))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.results_table.setItem(i, j, item)
    
    def get_selected_data(self):
        """Получение выбранных данных"""
        selected_rows = set(item.row() for item in self.results_table.selectedItems())
        if not selected_rows:
            return self.get_all_data()
        
        data = []
        for row in selected_rows:
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data
    
    def get_all_data(self):
        """Получение всех данных из таблицы"""
        data = []
        for row in range(self.results_table.rowCount()):
            if not self.results_table.isRowHidden(row):
                row_data = []
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
        return data
    
    def filter_table(self):
        """Фильтрация таблицы по поисковому запросу"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.results_table.rowCount()):
            show_row = False
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.results_table.setRowHidden(row, not show_row)
    
    def show_stats(self):
        """Показать окно статистики"""
        data = self.get_all_data()
        stats_window = StatsWindow(data, self)
        stats_window.exec_()
    
    def handle_print(self):
        """Обработка печати"""
        try:
            dialog = QFileDialog(self, "Сохранить как PDF")
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            dialog.setNameFilter("PDF файлы (*.pdf)")
            result = dialog.exec_()
            filename = None
            if result == QFileDialog.Accepted:
                filename = dialog.selectedFiles()[0]
                if filename:
                    printer = QPrinter(QPrinter.HighResolution)
                    printer.setOutputFileName(filename)
                    data = self.get_selected_data()
                    
                    # Создаем HTML для печати
                    html = "<table border='1' cellspacing='0' cellpadding='4' width='100%'>"
                    
                    # Заголовки
                    html += "<tr>"
                    for col in range(self.results_table.columnCount()):
                        header = self.results_table.horizontalHeaderItem(col).text()
                        html += f"<th>{header}</th>"
                    html += "</tr>"
                    
                    # Данные
                    for row_data in data:
                        html += "<tr>"
                        for cell in row_data:
                            html += f"<td>{cell}</td>"
                        html += "</tr>"
                    
                    html += "</table>"
                    
                    # Печать
                    document = QTextDocument()
                    document.setHtml(html)
                    document.print_(printer)
                    
        except Exception as e:
            logger.error("Ошибка при печати", exc_info=True)
            QMessageBox.critical(self, "Ошибка", str(e), QMessageBox.Ok)
    
    def show_filters(self):
        """Показать диалог фильтров"""
        # TODO: Реализовать фильтры
        QMessageBox.information(self, "Фильтры", "Фильтры будут доступны в следующей версии")
    
    def show_archive(self):
        """Показать архив"""
        archived_data = self.archive_manager.get_archived_items()
        dialog = ArchiveDialog(archived_data, self)
        dialog.exec_()
    
    def archive_selected(self):
        """Архивировать выбранные строки"""
        selected_rows = set(item.row() for item in self.results_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", 
                              "Выберите строки для архивации")
            return
        
        data_to_archive = []
        rows_to_remove = []
        
        for row in selected_rows:
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                row_data.append(item.text() if item else "")
            data_to_archive.append(row_data)
            rows_to_remove.append(row)
        
        # Архивируем данные
        self.archive_manager.archive_items(data_to_archive)
        
        # Удаляем строки из таблицы
        for row in sorted(rows_to_remove, reverse=True):
            self.results_table.removeRow(row)
        
        QMessageBox.information(self, "Успех", 
                              f"Архивировано строк: {len(data_to_archive)}")
    
    def handle_logout(self):
        """Обработка выхода из аккаунта преподавателя"""
        try:
            from ui.login_window import LoginWindow
            WindowManager().show_window(LoginWindow)
        except Exception as e:
            error_msg = f"Ошибка при возврате к окну входа: {str(e)}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(self, "Ошибка", error_msg, QMessageBox.Ok)
    
    def handle_export(self, format_name):
        """Обработка экспорта результатов"""
        try:
            data = self.get_selected_data()
            exporter = DataExporter(data)
            
            if format_name == "Excel":
                filename = exporter.export_to_excel()
            else:  # PDF
                filename = exporter.export_to_pdf()
            
            if filename:
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Данные успешно экспортированы в файл:\n{filename}",
                    QMessageBox.Ok
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при экспорте данных: {str(e)}",
                QMessageBox.Ok
            )
    
    def autosave(self):
        """Автосохранение состояния"""
        # TODO: Реализовать автосохранение
        logger.debug("Автосохранение выполнено")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from ui.styles import STYLES
    
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES)
    
    window = TeacherWindow()
    window.show()
    
    sys.exit(app.exec_())
