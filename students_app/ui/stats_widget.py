"""Виджет статистики для окна преподавателя"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QGridLayout, QPushButton
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class StatsWidget(QWidget):
    """Виджет для отображения статистики"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
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
            title_label.setAlignment(Qt.AlignCenter)
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignCenter)
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
    
    def update_stats(self, data):
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
        for i, (_, value) in enumerate(stats.items()):
            container = self.layout().itemAt(0).layout().itemAtPosition(i // 2, i % 2).widget()
            value_label = container.layout().itemAt(1).widget()
            value_label.setText(value)
            
        self.update_plot(data)
    
    def update_plot(self, data):
        """Обновление графика результатов"""
        self.ax.clear()
        
        if not data:
            self.ax.text(0.5, 0.5, 'Нет данных', 
                        horizontalalignment='center',
                        verticalalignment='center')
        else:
            results = [float(row[5].strip('%')) for row in data]
            groups = [row[2] for row in data]
            
            # Создаем график средних результатов по группам
            unique_groups = list(set(groups))
            group_means = [np.mean([r for r, g in zip(results, groups) if g == group]) 
                         for group in unique_groups]
            
            bars = self.ax.bar(unique_groups, group_means)
            self.ax.set_ylabel('Средний результат (%)')
            self.ax.set_title('Результаты по группам')
            
            # Добавляем значения над столбцами
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%',
                           ha='center', va='bottom')
        
        self.canvas.draw()
