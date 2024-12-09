"""Модуль для экспорта данных в PDF"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def export_to_pdf(filename: str, headers: list, data: list, title: str = None):
    """
    Экспорт данных в PDF файл

    Args:
        filename (str): Путь к файлу для сохранения
        headers (list): Заголовки таблицы
        data (list): Данные для таблицы (список списков)
        title (str, optional): Заголовок отчета
    """
    # Регистрируем шрифт для поддержки кириллицы
    pdfmetrics.registerFont(TTFont('TimesNewRoman', 'C:\\Windows\\Fonts\\times.ttf'))

    # Создаем PDF документ
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Устанавливаем шрифт
    c.setFont("TimesNewRoman", 16)

    # Добавляем заголовок, если он есть
    if title:
        # Разбиваем заголовок на строки
        title_lines = title.split('\n')
        y = height - 50
        for line in title_lines:
            c.drawCentredString(width/2, y, line)
            y -= 20
    else:
        y = height - 50

    # Создаем таблицу
    table_data = [headers] + data

    # Вычисляем ширину колонок
    col_widths = [width/len(headers) - 20] * len(headers)

    # Создаем таблицу
    table = Table(table_data, colWidths=col_widths)

    # Стиль таблицы
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'TimesNewRoman', 10),
        ('FONT', (0, 0), (-1, 0), 'TimesNewRoman', 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'TimesNewRoman-Bold'),
    ]))

    # Отрисовываем таблицу
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, y - 20 - (len(data) + 1) * 20)

    # Добавляем номера страниц
    c.setFont("TimesNewRoman", 10)
    c.drawRightString(width - 30, 30, "Страница 1")

    # Сохраняем документ
    c.save()
