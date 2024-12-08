import unittest
import os
from utils.questions_db import QuestionsDB

class TestQuestionsDB(unittest.TestCase):
    def setUp(self):
        """Подготовка к тестам"""
        self.db = QuestionsDB('test_questions.db')
    
    def test_lab_questions(self):
        """Тест получения вопросов для лабораторной работы"""
        # Проверяем каждую лабораторную работу
        for lab_id in range(1, 4):
            questions = self.db.get_random_questions(lab_id)
            
            # Проверяем наличие всех типов вопросов
            self.assertEqual(len(questions['theory']), 2, f"Должно быть 2 теоретических вопроса для лабораторной {lab_id}")
            self.assertEqual(len(questions['practice']), 2, f"Должно быть 2 практических задания для лабораторной {lab_id}")
            self.assertIsNotNone(questions['graphics'], f"Должен быть 1 графический вопрос для лабораторной {lab_id}")
            
            # Проверяем структуру вопросов
            for q in questions['theory']:
                self.assertEqual(len(q), 2, "Теоретический вопрос должен содержать текст и ответ")
            
            for q in questions['practice']:
                self.assertEqual(len(q), 2, "Практическое задание должно содержать текст и ответ")
            
            self.assertEqual(len(questions['graphics']), 3, "Графический вопрос должен содержать текст, ответ и путь к изображению")
    
    def test_lab_info(self):
        """Тест получения информации о лабораторной работе"""
        for lab_id in range(1, 4):
            info = self.db.get_lab_info(lab_id)
            self.assertIsNotNone(info, f"Должна быть информация о лабораторной {lab_id}")
            self.assertEqual(len(info), 2, "Информация должна содержать название и описание")
    
    def test_all_labs(self):
        """Тест получения списка всех лабораторных работ"""
        labs = self.db.get_all_labs()
        self.assertEqual(len(labs), 3, "Должно быть 3 лабораторные работы")
        for lab in labs:
            self.assertEqual(len(lab), 3, "Каждая запись должна содержать id, название и описание")
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists('test_questions.db'):
            os.remove('test_questions.db')

if __name__ == '__main__':
    unittest.main()
