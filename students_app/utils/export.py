"""Модуль для экспорта данных в различные форматы"""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from loguru import logger

# Регистрируем шрифт DejaVu (поддерживает кириллицу)
FONT_PATH = Path(__file__).parent.parent / "resources" / "fonts" / "DejaVuSans.ttf"
if FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont('DejaVuSans', str(FONT_PATH)))
else:
    logger.warning(f"Font file not found: {FONT_PATH}")

@dataclass
class ExportConfig:
    """Конфигурация экспорта"""
    include_charts: bool = True
    include_statistics: bool = True
    chart_type: str = "bar"  # bar, pie, line
    excel_template: Optional[str] = None
    pdf_orientation: str = "portrait"  # portrait, landscape
    output_dir: Optional[str] = None

class DataExporter:
    """Класс для экспорта данных"""

    def __init__(self, data: List[List[Any]], config: Optional[ExportConfig] = None):
        """
        Инициализация экспортера

        Args:
            data: список списков с данными [[фамилия, имя, группа, работа, результат], ...]
            config: конфигурация экспорта
        """
        self.data = data
        self.headers = ["Фамилия", "Имя", "Группа", "Лабораторная работа", "Результат"]
        self.current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.config = config or ExportConfig()

        # Создаем директорию для экспорта
        self.export_dir = Path(self.config.output_dir or os.path.expanduser("~")) / "Загрузки" / "Результаты тестирования"
        self.export_dir.mkdir(parents=True, exist_ok=True)

        # Создаем DataFrame для удобства работы с данными
        self.df = pd.DataFrame(self.data, columns=self.headers)

    def create_charts(self) -> Dict[str, str]:
        """Создает графики на основе данных"""
        charts = {}

        # Создаем временную директорию для графиков
        charts_dir = self.export_dir / "temp_charts"
        charts_dir.mkdir(exist_ok=True)

        # Настраиваем стиль графиков
        plt.style.use('seaborn')
        sns.set_palette("husl")

        # График распределения результатов по группам
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.df, x='Группа', y='Результат')
        plt.title('Распределение результатов по группам')
        chart_path = charts_dir / f'group_results_{self.current_time}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts['group_results'] = str(chart_path)

        # График среднего балла по лабораторным работам
        plt.figure(figsize=(12, 6))
        avg_results = self.df.groupby('Лабораторная работа')['Результат'].mean()
        avg_results.plot(kind=self.config.chart_type)
        plt.title('Средний балл по лабораторным работам')
        plt.xticks(rotation=45)
        chart_path = charts_dir / f'lab_results_{self.current_time}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts['lab_results'] = str(chart_path)

        return charts

    def get_statistics(self) -> Dict[str, Any]:
        """Получает статистику по данным"""
        stats = {
            'Общая статистика': {
                'Всего студентов': len(self.df['Фамилия'].unique()),
                'Всего групп': len(self.df['Группа'].unique()),
                'Средний балл': round(self.df['Результат'].mean(), 2),
                'Медианный балл': round(self.df['Результат'].median(), 2),
                'Максимальный балл': self.df['Результат'].max(),
                'Минимальный балл': self.df['Результат'].min()
            },
            'По группам': self.df.groupby('Группа')['Результат'].agg([
                ('Средний балл', 'mean'),
                ('Медиана', 'median'),
                ('Максимум', 'max'),
                ('Минимум', 'min')
            ]).round(2).to_dict('index')
        }
        return stats

    def export_to_excel(self) -> str:
        """Экспорт в Excel"""
        filename = self.export_dir / f"результаты_{self.current_time}.xlsx"

        # Создаем writer для Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Основные данные
            self.df.to_excel(writer, sheet_name='Результаты', index=False)

            # Статистика
            if self.config.include_statistics:
                stats = self.get_statistics()
                stats_df = pd.DataFrame.from_dict(stats['Общая статистика'], orient='index')
                stats_df.to_excel(writer, sheet_name='Статистика')

                # Статистика по группам
                groups_stats = pd.DataFrame.from_dict(stats['По группам'])
                groups_stats.to_excel(writer, sheet_name='Статистика по группам')

            # Форматирование
            for sheet in writer.sheets.values():
                for column in sheet.columns:
                    max_length = max(len(str(cell.value)) for cell in column)
                    sheet.column_dimensions[column[0].column_letter].width = max_length + 2

        return str(filename)

    def export_to_csv(self) -> str:
        """Экспорт в CSV"""
        filename = self.export_dir / f"результаты_{self.current_time}.csv"
        self.df.to_csv(filename, index=False, encoding='utf-8-sig')
        return str(filename)

    def export_to_pdf(self) -> str:
        """Экспорт в PDF"""
        filename = self.export_dir / f"результаты_{self.current_time}.pdf"

        # Создаем PDF документ
        pagesize = landscape(A4) if self.config.pdf_orientation == 'landscape' else A4
        doc = SimpleDocTemplate(
            filename,
            pagesize=pagesize,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Создаем стили
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

        # Добавляем заголовок и дату
        elements.extend([
            Paragraph("Результаты тестирования", title_style),
            Paragraph(
                f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontName='DejaVuSans',
                    fontSize=12,
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
            )
        ])

        # Добавляем статистику
        if self.config.include_statistics:
            stats = self.get_statistics()
            stats_style = ParagraphStyle(
                'StatsStyle',
                parent=styles['Normal'],
                fontName='DejaVuSans',
                fontSize=11,
                alignment=TA_LEFT,
                leading=14
            )

            elements.extend([
                Paragraph("Общая статистика:", title_style),
                Spacer(1, 10)
            ])

            for key, value in stats['Общая статистика'].items():
                elements.append(Paragraph(f"{key}: {value}", stats_style))

            elements.append(Spacer(1, 20))

        # Добавляем графики
        if self.config.include_charts:
            charts = self.create_charts()
            for chart_path in charts.values():
                elements.extend([
                    Image(chart_path, width=400, height=300),
                    Spacer(1, 20)
                ])

        # Добавляем таблицу с результатами
        table_data = [[Paragraph(header, styles['Normal']) for header in self.headers]]
        table_data.extend(
            [[Paragraph(str(cell), styles['Normal']) for cell in row]
             for row in self.data]
        )

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        elements.append(table)

        # Собираем документ
        doc.build(elements)

        # Очищаем временные файлы
        if self.config.include_charts:
            for chart_path in charts.values():
                try:
                    os.remove(chart_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary chart file {chart_path}: {e}")
            try:
                os.rmdir(os.path.dirname(chart_path))
            except Exception as e:
                logger.warning(f"Failed to remove temporary charts directory: {e}")

        return str(filename)

    def export_all(self) -> Dict[str, str]:
        """Экспортирует данные во все поддерживаемые форматы"""
        return {
            'excel': self.export_to_excel(),
            'csv': self.export_to_csv(),
            'pdf': self.export_to_pdf()
        }
