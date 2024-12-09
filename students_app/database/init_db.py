"""Скрипт для инициализации базы данных"""
from db_manager import DatabaseManager

def init_database():
    """Инициализация базы данных тестовыми данными"""
    db = DatabaseManager()

    # Добавляем тестового пользователя
    db.add_user(
        username="test_user",
        password="test123",
        group_number="ИУ7-51Б",
        role="student"
    )

    # Добавляем тестовые лабораторные работы
    labs = [
        {
            "title": "Лабораторная работа №1",
            "description": "Основы программирования на Python. Работа с базовыми типами данных, условными операторами и циклами.",
            "max_points": 100
        },
        {
            "title": "Лабораторная работа №2",
            "description": "Функции в Python. Создание и использование функций, передача параметров, возвращаемые значения.",
            "max_points": 100
        },
        {
            "title": "Лабораторная работа №3",
            "description": "Объектно-ориентированное программирование. Классы, объекты, наследование, полиморфизм.",
            "max_points": 100
        },
        {
            "title": "Лабораторная работа №4",
            "description": "Работа с файлами и исключениями. Чтение и запись файлов, обработка ошибок.",
            "max_points": 100
        }
    ]

    # Добавляем лабораторные работы в базу данных
    for lab in labs:
        db.cursor.execute('''
            INSERT INTO labs (title, description, max_points)
            VALUES (?, ?, ?)
        ''', (lab["title"], lab["description"], lab["max_points"]))

    db.conn.commit()

if __name__ == "__main__":
    init_database()
    print("База данных успешно инициализирована")
