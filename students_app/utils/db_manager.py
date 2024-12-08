"""Модуль для прямого управления базой данных через SQLite3"""
import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name='questions.db'):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Успешное подключение к базе данных {self.db_name}")
        except sqlite3.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
    
    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")
    
    def execute_query(self, query, parameters=None):
        """Выполнение SQL запроса"""
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return False
    
    def fetch_all(self, query, parameters=None):
        """Получение всех результатов запроса"""
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    def fetch_one(self, query, parameters=None):
        """Получение одной строки результата"""
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
            return None

    def get_questions_for_lab(self, lab_id):
        """Получение всех вопросов для конкретной лабораторной работы"""
        query = '''
        SELECT question_type, question_text, correct_answer, image_path 
        FROM questions 
        WHERE lab_id = ?
        '''
        return self.fetch_all(query, (lab_id,))
    
    def add_question(self, lab_id, q_type, text, answer, image_path=None):
        """Добавление нового вопроса"""
        query = '''
        INSERT INTO questions (lab_id, question_type, question_text, correct_answer, image_path)
        VALUES (?, ?, ?, ?, ?)
        '''
        return self.execute_query(query, (lab_id, q_type, text, answer, image_path))
    
    def update_question(self, question_id, text, answer, image_path=None):
        """Обновление существующего вопроса"""
        query = '''
        UPDATE questions 
        SET question_text = ?, correct_answer = ?, image_path = ?
        WHERE id = ?
        '''
        return self.execute_query(query, (text, answer, image_path, question_id))
    
    def delete_question(self, question_id):
        """Удаление вопроса"""
        query = 'DELETE FROM questions WHERE id = ?'
        return self.execute_query(query, (question_id,))
    
    def get_all_labs(self):
        """Получение списка всех лабораторных работ"""
        query = 'SELECT id, name, description FROM labs'
        return self.fetch_all(query)
    
    def add_lab(self, name, description):
        """Добавление новой лабораторной работы"""
        query = 'INSERT INTO labs (name, description) VALUES (?, ?)'
        return self.execute_query(query, (name, description))
    
    def update_lab(self, lab_id, name, description):
        """Обновление информации о лабораторной работе"""
        query = 'UPDATE labs SET name = ?, description = ? WHERE id = ?'
        return self.execute_query(query, (name, description, lab_id))
    
    def delete_lab(self, lab_id):
        """Удаление лабораторной работы и всех связанных вопросов"""
        try:
            # Удаляем связанные вопросы
            self.execute_query('DELETE FROM questions WHERE lab_id = ?', (lab_id,))
            # Удаляем саму лабораторную работу
            self.execute_query('DELETE FROM labs WHERE id = ?', (lab_id,))
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении лабораторной работы: {e}")
            return False

if __name__ == '__main__':
    # Пример использования
    db = DatabaseManager('questions.db')
    db.connect()
    
    # Получаем список всех лабораторных работ
    labs = db.get_all_labs()
    print("\nСписок лабораторных работ:")
    for lab in labs:
        print(f"ID: {lab[0]}, Название: {lab[1]}, Описание: {lab[2]}")
        
        # Получаем вопросы для каждой лабораторной
        questions = db.get_questions_for_lab(lab[0])
        print("\nВопросы:")
        for q in questions:
            print(f"Тип: {q[0]}, Вопрос: {q[1]}")
        print("-" * 50)
    
    db.disconnect()
