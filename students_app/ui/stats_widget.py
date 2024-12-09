"""Виджет статистики для окна преподавателя"""
from typing import Optional, List, Tuple, cast
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QGridLayout, QPushButton, QLayout,
    QLayoutItem
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class StatsWidget(QWidget):
    """Виджет для отображения статистики"""
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем сетку для статистики
        stats_grid = QGridLayout()

        # Добавляем метки статистики
        stats = {
            "Всего работ": "0",
            "Средний балл": "0%",
            "Лучший результат": "0%",
            "Худший результат": "0%"
        }

        row = 0
        col = 0
        for title, value in stats.items():
            container = QWidget()
            container_layout = QVBoxLayout(container)

            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setObjectName("stats-value")

            container_layout.addWidget(title_label)
            container_layout.addWidget(value_label)

            stats_grid.addWidget(container, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(stats_grid)

        # Добавляем график
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.update_plot([])

    def update_stats(self, data: List[Tuple]) -> None:
        """Обновление статистики"""
        if not data:
            return

        results = [float(row[5].strip('%')) for row in data]

        stats = {
            "Всего работ": str(len(data)),
            "Средний балл": f"{np.mean(results):.1f}%",
            "Лучший результат": f"{max(results):.1f}%",
            "Худший результат": f"{min(results):.1f}%"
        }

        # Обновляем значения
        main_layout = self.layout()
        if main_layout is None:
            return

        grid_layout = cast(QGridLayout, main_layout.itemAt(0).layout())
        if grid_layout is None:
            return

        for i, (_, value) in enumerate(stats.items()):
            item = grid_layout.itemAt(i)
            if item is None:
                continue

            container = item.widget()
            if container is None:
                continue

            container_layout = container.layout()
            if container_layout is None:
                continue

            value_item = container_layout.itemAt(1)
            if value_item is None:
                continue

            value_label = value_item.widget()
            if value_label is None:
                continue

            value_label.setText(value)

        self.update_plot(data)

    def update_plot(self, data: List[Tuple]) -> None:
        """Обновление графика результатов"""
        self.ax.clear()

        if not data:
            self.ax.text(0.5, 0.5, 'Нет данных',
                        horizontalalignment='center',
                        verticalalignment='center')
        else:
            results = [float(row[5].strip('%')) for row in data]
            bins = np.linspace(0, 100, 11)  # 10 bins from 0 to 100
            self.ax.hist(results, bins=bins, edgecolor='black')
            self.ax.set_xlabel('Результат (%)')
            self.ax.set_ylabel('Количество студентов')
            self.ax.set_title('Распределение результатов')

        self.canvas.draw()
