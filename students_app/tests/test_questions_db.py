"""Тесты для модуля работы с базой данных вопросов"""
import unittest
from utils.questions_db import QuestionsDB

class TestQuestionsDB(unittest.TestCase):
    """Тесты для класса QuestionsDB"""

    def setUp(self):
        """Подготовка к тестам"""
        self.db = QuestionsDB(':memory:')
        self.db.create_tables()

    def tearDown(self):
        """Очистка после тестов"""
        self.db.close()

    def test_get_questions(self):
        """Тест получения вопросов"""
        # Проверяем получение вопросов по типам
        theory_questions = self.db.get_questions('theory')
        practice_questions = self.db.get_questions('practice')
        graphics_questions = self.db.get_questions('graphics')

        # Проверяем что получаем списки
        self.assertIsInstance(theory_questions, list)
        self.assertIsInstance(practice_questions, list)
        self.assertIsInstance(graphics_questions, list)

    def test_get_random_questions(self):
        """Тест получения случайных вопросов"""
        lab_id = 1
        questions = self.db.get_random_questions(lab_id)

        # Проверяем что получаем словарь
        self.assertIsInstance(questions, dict)

        # Проверяем наличие всех типов вопросов
        self.assertIn('theory', questions)
        self.assertIn('practice', questions)
        self.assertIn('graphics', questions)

        # Проверяем количество вопросов
        self.assertEqual(len(questions['theory']), 2)
        self.assertEqual(len(questions['practice']), 2)
        self.assertEqual(len(questions['graphics']), 1)

    def test_get_lab_details(self):
        """Тест получения информации о лабораторной работе"""
        lab_id = 1
        lab_details = self.db.get_lab_details(lab_id)

        # Проверяем что получаем словарь
        self.assertIsInstance(lab_details, dict)

        # Проверяем наличие необходимых полей
        self.assertIn('title', lab_details)
        self.assertIn('description', lab_details)

    def test_invalid_question_type(self):
        """Тест обработки неверного типа вопроса"""
        with self.assertRaises(ValueError):
            self.db.get_questions('invalid_type')

    def test_invalid_lab_id(self):
        """Тест обработки неверного ID лабораторной работы"""
        with self.assertRaises(ValueError):
            self.db.get_lab_details(-1)

    def test_empty_database(self):
        """Тест работы с пустой базой данных"""
        # Создаем новую пустую базу
        empty_db = QuestionsDB(':memory:')
        empty_db.create_tables()

        # Проверяем что получаем пустые списки/словари
        self.assertEqual(empty_db.get_questions('theory'), [])
        self.assertEqual(empty_db.get_random_questions(1), {'theory': [], 'practice': [], 'graphics': []})

        empty_db.close()

if __name__ == '__main__':
    unittest.main()
