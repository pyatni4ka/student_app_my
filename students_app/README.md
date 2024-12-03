# Система тестирования студентов

Приложение для проведения тестирования студентов по лабораторным работам.

## Особенности

- Регистрация студентов с указанием ФИО, группы и года поступления
- Выбор доступных лабораторных работ
- Тестирование с таймером (20 минут)
- Случайный выбор вопросов (2 теоретических, 2 практических, 1 графический)
- История результатов для студентов
- Панель администратора для преподавателей с полной статистикой

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте конфигурацию:
- Создайте файл `.env` на основе `.env.example`
- Укажите необходимые параметры (пароль преподавателя, путь к базе данных и т.д.)

## Запуск

```bash
python main.py
```

## Структура проекта

```
students_app/
├── core/                   # Ядро приложения
│   └── database/          # Работа с базой данных
├── ui/                    # Пользовательский интерфейс
│   ├── windows/          # Окна приложения
│   └── base_window.py    # Базовый класс окна
├── styles/               # Стили приложения
├── config.py            # Конфигурация
├── main.py              # Точка входа
└── requirements.txt     # Зависимости
```

## Требования

- Python 3.8+
- PyQt6
- SQLAlchemy
- python-dotenv

## Для преподавателей

Доступ к базе данных результатов:
1. Нажмите кнопку "База данных (для преподавателя)" в окне регистрации
2. Введите пароль преподавателя
3. Используйте фильтры для анализа результатов студентов

## Разработка

При разработке использовались:
- PyQt6 для создания графического интерфейса
- SQLAlchemy для работы с базой данных
- Современный дизайн с использованием QSS стилей