import sys
import os
import unittest
from datetime import datetime

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.export import DataExporter
from utils.database import Database

class TestCore(unittest.TestCase):
    def setUp(self):
        """Подготовка к тестам"""
        self.db = Database('test.db')
        self.test_data = [
            ['Иванов', 'Иван', 'ПИ-231', 'Лабораторная работа 1', 'Зачтено'],
            ['Петров', 'Петр', 'ПИ-232', 'Лабораторная работа 1', 'Зачтено']
        ]
        self.exporter = DataExporter(self.test_data)
        
        # Очищаем тестовую базу данных
        self.db.clear_all()
    
    def test_database_operations(self):
        """Тест операций с базой данных"""
        # Тест добавления студента
        student_data = {
            'group': 'ПИ-231',
            'name': 'Иван Иванов',
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.db.add_student(**student_data)
        
        # Проверяем, что студент добавлен
        students = self.db.get_all_students()
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0]['group'], student_data['group'])
        self.assertEqual(students[0]['name'], student_data['name'])
        
        # Тест поиска студента
        found_students = self.db.search_students('Иван')
        self.assertEqual(len(found_students), 1)
        self.assertEqual(found_students[0]['name'], student_data['name'])
        
        # Тест фильтрации по группе
        filtered_students = self.db.get_students_by_group('ПИ-231')
        self.assertEqual(len(filtered_students), 1)
        self.assertEqual(filtered_students[0]['group'], student_data['group'])
        
        # Тест получения списка групп
        groups = self.db.get_groups()
        self.assertIn('ПИ-231', groups)
    
    def test_export_functionality(self):
        """Тест функциональности экспорта"""
        # Тестируем экспорт в Excel
        excel_file = self.exporter.export_to_excel()
        self.assertTrue(os.path.exists(excel_file))
        os.remove(excel_file)
        
        # Тестируем экспорт в CSV
        csv_file = self.exporter.export_to_csv()
        self.assertTrue(os.path.exists(csv_file))
        os.remove(csv_file)
        
        # Тестируем экспорт в PDF
        pdf_file = self.exporter.export_to_pdf()
        self.assertTrue(os.path.exists(pdf_file))
        os.remove(pdf_file)
    
    def tearDown(self):
        """Очистка после тестов"""
        self.db.clear_all()
        # Удаляем тестовую базу данных
        if os.path.exists('test.db'):
            os.remove('test.db')

if __name__ == '__main__':
    unittest.main()
