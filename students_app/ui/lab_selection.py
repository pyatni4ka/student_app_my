"""Окно выбора лабораторных работ"""
import os
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QDateEdit, QDialog, QLabel)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from database.db_manager import DatabaseManager
from loguru import logger
from .lab_test_window import LabTestWindow
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class ExportDialog(QDialog):
    """Диалог для выбора периода экспорта"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор периода")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Выбор даты начала
        start_layout = QHBoxLayout()
        start_label = QLabel("Дата начала:")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_date)

        # Выбор даты конца
        end_layout = QHBoxLayout()
        end_label = QLabel("Дата конца:")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_date)

        # Кнопки
        button_layout = QHBoxLayout()
        export_button = QPushButton("Экспорт")
        export_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(export_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addLayout(button_layout)

class LabSelectionWindow(QMainWindow):
    """Окно выбора лабораторных работ"""

    def __init__(self, user_data: dict, db_manager: DatabaseManager):
        super().__init__()
        self.username = user_data.get('username', '')
        self.group = user_data.get('group_number', '')
        self.db_manager = db_manager
        self.user_data = user_data

        # Настройка окна
        self.setWindowTitle("Выбор лабораторной работы")
        self.setMinimumSize(800, 600)

        # Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Создаем верхнюю панель с информацией
        self.create_info_panel()
        main_layout.addWidget(self.info_panel)

        # Создаем таблицу лабораторных работ
        self.create_labs_table()
        main_layout.addWidget(self.labs_table)

        # Создаем нижнюю панель с кнопками
        self.create_button_panel()
        main_layout.addWidget(self.button_panel)

        # Применяем стили
        self.apply_styles()

        # Загружаем данные
        self.load_labs_data()

        logger.info("Окно выбора лабораторных работ инициализировано")

    def create_info_panel(self):
        """Создание панели с информацией о пользователе"""
        self.info_panel = QFrame()
        self.info_panel.setFrameShape(QFrame.StyledPanel)

        layout = QHBoxLayout(self.info_panel)
        layout.setContentsMargins(15, 10, 15, 10)

        # Информация о студенте
        student_info = QLabel(f"Студент: {self.username} | Группа: {self.group}")
        student_info.setFont(QFont('Segoe UI', 10))

        # Текущая дата
        current_date = QLabel(f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
        current_date.setFont(QFont('Segoe UI', 10))

        layout.addWidget(student_info)
        layout.addStretch()
        layout.addWidget(current_date)

    def create_labs_table(self):
        """Создание таблицы лабораторных работ"""
        self.labs_table = QTableWidget()
        self.labs_table.setColumnCount(5)

        # Заголовки столбцов
        headers = ["№", "Тема", "Статус", "Дата сдачи", "Оценка"]
        self.labs_table.setHorizontalHeaderLabels(headers)

        # Настройка внешнего вида таблицы
        self.labs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.labs_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.labs_table.setAlternatingRowColors(True)
        self.labs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.labs_table.setSelectionMode(QTableWidget.SingleSelection)
        self.labs_table.verticalHeader().setVisible(False)

        # Подключаем обработчик выбора строки
        self.labs_table.itemDoubleClicked.connect(self.start_test)

        # Устанавливаем фиксированную ширину для некоторых столбцов
        self.labs_table.setColumnWidth(0, 40)  # №
        self.labs_table.setColumnWidth(2, 100)  # Статус
        self.labs_table.setColumnWidth(3, 100)  # Дата
        self.labs_table.setColumnWidth(4, 80)   # Оценка

    def create_button_panel(self):
        """Создание панели с кнопками"""
        self.button_panel = QFrame()
        layout = QHBoxLayout(self.button_panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Кнопка обновления
        refresh_button = QPushButton("Обновить")
        refresh_button.setFixedWidth(100)
        refresh_button.clicked.connect(self.refresh_labs)

        # Кнопка выхода
        logout_button = QPushButton("Выйти")
        logout_button.setFixedWidth(100)
        logout_button.clicked.connect(self.logout)

        # Добавляем кнопку экспорта для преподавателя
        if self.user_data.get('role') == 'teacher':
            export_button = QPushButton("Экспорт результатов")
            export_button.clicked.connect(self.export_results)
            export_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            layout.addWidget(export_button)

        layout.addWidget(refresh_button)
        layout.addStretch()
        layout.addWidget(logout_button)

    def logout(self):
        """Обработчик выхода"""
        from ui.login_window import LoginWindow
        from ui.window_manager import WindowManager
        self.close()
        window_manager = WindowManager()
        window_manager.show_window(LoginWindow)

    def apply_styles(self):
        """Применение стилей к элементам окна"""
        # Стили для панели информации
        self.info_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QLabel {
                color: #333;
            }
        """)

        # Стили для таблицы
        self.labs_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)

        # Стили для кнопок
        self.button_panel.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def load_labs_data(self):
        """Загрузка данных о лабораторных работах"""
        self.refresh_labs()

    def start_test(self, item):
        """Запуск теста для выбранной лабораторной работы"""
        row = item.row()
        lab_number = int(self.labs_table.item(row, 0).text().replace('ЛР', ''))
        lab_topic = self.labs_table.item(row, 1).text()

        # Создаем окно тестирования
        self.test_window = LabTestWindow(
            user_data=self.user_data,
            lab_number=lab_number,
            lab_topic=lab_topic,
            db_manager=self.db_manager
        )
        self.test_window.show()
        self.close()

    def export_results(self):
        """Экспорт результатов тестов за выбранный период"""
        dialog = ExportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            start_date = dialog.start_date.date().toString("yyyy-MM-dd")
            end_date = dialog.end_date.date().toString("yyyy-MM-dd")

            # Получаем результаты за период
            results = self.db_manager.get_test_results(start_date, end_date)

            if not results:
                QMessageBox.warning(self, "Предупреждение",
                                  "Нет результатов за выбранный период")
                return

            # Создаем PDF отчет
            filename = f"results_{start_date}_{end_date}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []

            # Заголовок
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"Отчет по результатам тестирования\n"
                                   f"Период: {start_date} - {end_date}",
                                   styles['Title']))

            # Данные таблицы
            data = [['Студент', 'Группа', 'Лаб. работа', 'Баллы', 'Макс. баллов',
                    'Время (мин)', 'Дата']]

            for result in results:
                time_minutes = result['time_spent'] // 60
                data.append([
                    result['username'],
                    result['group_number'],
                    str(result['lab_number']),
                    str(result['score']),
                    str(result['max_score']),
                    str(time_minutes),
                    result['completed_at'].split()[0]
                ])

            # Создаем таблицу
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)

            # Генерируем PDF
            try:
                doc.build(elements)
                QMessageBox.information(self, "Успех",
                                      f"Отчет сохранен в файл {filename}")

                # Открываем файл
                os.startfile(filename)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Ошибка при создании отчета: {str(e)}")

    def show(self):
        """Показ окна"""
        super().show()
        # Обновляем таблицу при каждом показе окна
        self.refresh_labs()

    def refresh_labs(self):
        """Обновление списка лабораторных работ"""
        try:
            # Получаем список лабораторных работ
            labs = self.db_manager.get_labs_with_results(self.user_data['id'])

            # Очищаем таблицу
            self.labs_table.setRowCount(0)

            # Заполняем таблицу данными
            for row, lab in enumerate(labs):
                self.labs_table.insertRow(row)

                # Номер лабораторной
                lab_number = QTableWidgetItem(f"ЛР{lab['lab_number']}")
                lab_number.setTextAlignment(Qt.AlignCenter)
                self.labs_table.setItem(row, 0, lab_number)

                # Название
                title = QTableWidgetItem(lab['title'])
                title.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.labs_table.setItem(row, 1, title)

                # Статус
                status_text = {
                    'not_started': 'Не начата',
                    'in_progress': 'В процессе',
                    'completed': 'Завершена'
                }.get(lab['status'], lab['status'])

                status = QTableWidgetItem(status_text)
                status.setTextAlignment(Qt.AlignCenter)

                # Устанавливаем цвет фона в зависимости от статуса
                if lab['status'] == 'completed':
                    status.setBackground(QColor('#d4edda'))  # Зеленый
                elif lab['status'] == 'in_progress':
                    status.setBackground(QColor('#fff3cd'))  # Желтый
                else:
                    status.setBackground(QColor('#f8f9fa'))  # Серый

                self.labs_table.setItem(row, 2, status)

                # Дата сдачи
                submission_date = lab.get('submission_date', '')
                if submission_date:
                    date = QTableWidgetItem(submission_date.split()[0])
                else:
                    date = QTableWidgetItem('-')
                date.setTextAlignment(Qt.AlignCenter)
                self.labs_table.setItem(row, 3, date)

                # Оценка
                points = lab.get('points', 0)
                if points > 0:
                    grade = QTableWidgetItem(str(points))
                else:
                    grade = QTableWidgetItem('-')
                grade.setTextAlignment(Qt.AlignCenter)
                self.labs_table.setItem(row, 4, grade)

            # Устанавливаем размер строк по содержимому
            self.labs_table.resizeRowsToContents()

        except Exception as e:
            logger.error(f"Ошибка при обновлении списка лабораторных работ: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить список лабораторных работ")
