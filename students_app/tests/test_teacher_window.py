import sys
import os
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.teacher_window import TeacherWindow
from tests.test_base import QtTestCase

class TestTeacherWindow(QtTestCase):
    def setUp(self):
        self.teacher_window = TeacherWindow()

    def test_window_components(self):
        """Тест наличия всех основных компонентов окна преподавателя"""
        # Проверка наличия основных виджетов
        self.assertIsNotNone(self.teacher_window.student_table)
        self.assertIsNotNone(self.teacher_window.search_input)
        self.assertIsNotNone(self.teacher_window.filter_group_combo)
        
    def test_table_columns(self):
        """Тест наличия всех необходимых столбцов в таблице"""
        headers = []
        for i in range(self.teacher_window.student_table.columnCount()):
            headers.append(self.teacher_window.student_table.horizontalHeaderItem(i).text())
        
        required_headers = ["Группа", "ФИО", "Дата"]
        for header in required_headers:
            self.assertIn(header, headers)

    def test_search_functionality(self):
        """Тест функциональности поиска"""
        # Добавляем тестовые данные в таблицу
        test_data = [
            ("ПИ-231", "Иван Иванов", "2023-12-08"),
            ("ПИ-232", "Петр Петров", "2023-12-08")
        ]
        for group, name, date in test_data:
            self.teacher_window.add_student_to_table(group, name, date)
        
        # Тестируем поиск
        self.enter_text(self.teacher_window.search_input, "Иван")
        self.assertEqual(self._get_visible_rows(), 1)

    def test_filter_functionality(self):
        """Тест функциональности фильтрации по группам"""
        # Добавляем тестовые данные
        test_data = [
            ("ПИ-231", "Иван Иванов", "2023-12-08"),
            ("ПИ-232", "Петр Петров", "2023-12-08")
        ]
        for group, name, date in test_data:
            self.teacher_window.add_student_to_table(group, name, date)
        
        # Выбираем группу в фильтре
        self.select_combo_item(self.teacher_window.filter_group_combo, "ПИ-231")
        self.assertEqual(self._get_visible_rows(), 1)

    def test_export_functionality(self):
        """Тест функциональности экспорта данных"""
        # Добавляем тестовые данные
        self.teacher_window.add_student_to_table("ПИ-231", "Иван Иванов", "2023-12-08")
        
        # Проверяем наличие кнопки экспорта
        export_button = None
        for button in self.teacher_window.findChildren(QPushButton):
            if "Экспорт" in button.text():
                export_button = button
                break
        self.assertIsNotNone(export_button)

    def _get_visible_rows(self):
        """Подсчет видимых строк в таблице"""
        return sum(1 for row in range(self.teacher_window.student_table.rowCount())
                  if not self.teacher_window.student_table.isRowHidden(row))

    def tearDown(self):
        self.teacher_window.close()

if __name__ == '__main__':
    unittest.main()
