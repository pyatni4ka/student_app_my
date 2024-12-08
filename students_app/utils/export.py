"""Модуль для экспорта данных в различные форматы"""
import os
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Регистрируем шрифт DejaVu (поддерживает кириллицу)
FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                        "resources", "fonts", "DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))

class DataExporter:
    """Класс для экспорта данных"""
    
    def __init__(self, data):
        """
        Инициализация экспортера
        
        Args:
            data: список списков с данными [[фамилия, имя, группа, работа, результат], ...]
        """
        self.data = data
        self.headers = ["Фамилия", "Имя", "Группа", "Лабораторная работа", "Результат"]
        self.current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем директорию для экспорта, если её нет
        self.export_dir = os.path.join(os.path.expanduser("~"), "Загрузки", "Результаты тестирования")
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_excel(self):
        """Экспорт в Excel"""
        filename = os.path.join(self.export_dir, f"результаты_{self.current_time}.xlsx")
        
        # Создаем DataFrame
        df = pd.DataFrame(self.data, columns=self.headers)
        
        # Создаем writer для Excel
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Результаты', index=False)
            
            # Получаем рабочий лист
            worksheet = writer.sheets['Результаты']
            
            # Настраиваем ширину колонок
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.set_column(i, i, max_length + 2)
            
            # Добавляем форматирование
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9',
                'border': 1
            })
            
            # Применяем формат к заголовкам
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        return filename
    
    def export_to_csv(self):
        """Экспорт в CSV"""
        filename = os.path.join(self.export_dir, f"результаты_{self.current_time}.csv")
        
        # Создаем DataFrame и сохраняем в CSV
        df = pd.DataFrame(self.data, columns=self.headers)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return filename
    
    def export_to_pdf(self):
        """Экспорт в PDF"""
        filename = os.path.join(self.export_dir, f"результаты_{self.current_time}.pdf")
        
        # Создаем PDF документ
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        # Создаем стиль для заголовка с указанием шрифта
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='DejaVuSans',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30,
            leading=20
        )
        
        # Создаем элементы документа
        elements = []
        
        # Добавляем заголовок
        title = Paragraph("Результаты тестирования", title_style)
        elements.append(title)
        
        # Добавляем дату
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20,
            leading=15
        )
        date_text = Paragraph(
            f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            date_style
        )
        elements.append(date_text)
        
        # Создаем стиль для ячеек таблицы
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=12,
            textColor=colors.whitesmoke,
            alignment=TA_CENTER,
            leading=14
        )
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=11,
            alignment=TA_CENTER,
            leading=13
        )
        
        # Создаем таблицу с форматированным текстом
        headers_row = [Paragraph(header, header_style) for header in self.headers]
        table_data = [headers_row]
        
        for row in self.data:
            formatted_row = [Paragraph(str(cell), cell_style) for cell in row]
            table_data.append(formatted_row)
        
        # Вычисляем ширину колонок (в процентах от ширины страницы)
        col_widths = [
            doc.width * 0.2,  # Фамилия
            doc.width * 0.2,  # Имя
            doc.width * 0.15, # Группа
            doc.width * 0.25, # Лабораторная работа
            doc.width * 0.15  # Результат
        ]
        
        # Создаем таблицу
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Добавляем стиль таблицы
        table.setStyle(TableStyle([
            # Стиль заголовков
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Стиль ячеек
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            
            # Отступы
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            
            # Сетка
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),  # Жирная линия под заголовками
            
            # Чередование цветов строк для лучшей читаемости
            *[('BACKGROUND', (0, i), (-1, i), colors.lightgrey) 
              for i in range(2, len(table_data), 2)]
        ]))
        
        elements.append(table)
        
        # Создаем PDF
        doc.build(elements)
        
        return filename
