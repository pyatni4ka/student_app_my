"""Окно статистики"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGridLayout, QWidget,
    QComboBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from datetime import datetime

class StatsWindow(QDialog):
    """Окно для отображения статистики"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Статистика")
        self.setMinimumSize(1000, 800)
        self.data = data
        self.current_year = datetime.now().year
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Создаем сетку для статистики
        stats_grid = QGridLayout()
        
        if self.data:
            results = [float(row[5].strip('%')) for row in self.data]
            labs = [row[4] for row in self.data]
            years = [int(row[3]) for row in self.data]
            current_year_results = [r for r, y in zip(results, years) if y == self.current_year]
            
            unique_labs = list(set(labs))
            lab_means = {lab: np.mean([r for r, l in zip(results, labs) if l == lab]) 
                        for lab in unique_labs}
            best_lab = max(lab_means.items(), key=lambda x: x[1])
            worst_lab = min(lab_means.items(), key=lambda x: x[1])
            
            stats = {
                "Всего работ": str(len(self.data)),
                "Работ за текущий год": str(len(current_year_results)),
                "Средний балл": f"{np.mean(results):.1f}%",
                "Средний балл за текущий год": f"{np.mean(current_year_results) if current_year_results else 0:.1f}%",
                "Лучший результат": f"{max(results):.1f}%",
                "Худший результат": f"{min(results):.1f}%",
                "Лучшая работа": f"{best_lab[0]}\n({best_lab[1]:.1f}%)",
                "Худшая работа": f"{worst_lab[0]}\n({worst_lab[1]:.1f}%)"
            }
        else:
            stats = {
                "Всего работ": "0",
                "Работ за текущий год": "0",
                "Средний балл": "0%",
                "Средний балл за текущий год": "0%",
                "Лучший результат": "0%",
                "Худший результат": "0%",
                "Лучшая работа": "Нет данных",
                "Худшая работа": "Нет данных"
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
            if col > 3:  # Теперь у нас 4 колонки
                col = 0
                row += 1
        
        layout.addLayout(stats_grid)
        
        # Добавляем выбор типа графика
        plot_control = QHBoxLayout()
        plot_type_label = QLabel("Тип графика:")
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            "Результаты по группам",
            "Результаты по группам (текущий год)",
            "Распределение оценок",
            "Результаты по работам"
        ])
        self.plot_type_combo.currentTextChanged.connect(self.update_plot)
        plot_control.addWidget(plot_type_label)
        plot_control.addWidget(self.plot_type_combo)
        plot_control.addStretch()
        layout.addLayout(plot_control)
        
        # Добавляем график
        self.figure, self.ax = plt.subplots(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.update_plot()
    
    def update_plot(self, plot_type=None):
        """Обновление графика результатов"""
        if plot_type is None:
            plot_type = self.plot_type_combo.currentText()
            
        self.ax.clear()
        
        if not self.data:
            self.ax.text(0.5, 0.5, 'Нет данных', 
                        horizontalalignment='center',
                        verticalalignment='center')
        else:
            results = [float(row[5].strip('%')) for row in self.data]
            
            if plot_type == "Результаты по группам":
                self._plot_group_results(results, False)
            elif plot_type == "Результаты по группам (текущий год)":
                self._plot_group_results(results, True)
            elif plot_type == "Распределение оценок":
                self._plot_grade_distribution(results)
            else:  # Результаты по работам
                self._plot_lab_results(results)
        
        # Регулируем размер графика, чтобы не обрезались подписи
        plt.tight_layout()
        self.canvas.draw()
    
    def _plot_group_results(self, results, current_year_only=False):
        """График результатов по группам"""
        groups = [row[2] for row in self.data]
        years = [int(row[3]) for row in self.data]
        
        if current_year_only:
            # Фильтруем данные только за текущий год
            filtered_results = [r for r, y in zip(results, years) if y == self.current_year]
            filtered_groups = [g for g, y in zip(groups, years) if y == self.current_year]
            
            if not filtered_results:
                self.ax.text(0.5, 0.5, f'Нет данных за {self.current_year} год', 
                            horizontalalignment='center',
                            verticalalignment='center')
                return
                
            results = filtered_results
            groups = filtered_groups
            title_suffix = f" ({self.current_year} год)"
        else:
            title_suffix = " (все годы)"
        
        unique_groups = sorted(list(set(groups)))
        group_means = [np.mean([r for r, g in zip(results, groups) if g == group]) 
                      for group in unique_groups]
        
        bars = self.ax.bar(unique_groups, group_means)
        self.ax.set_ylabel('Средний результат (%)')
        self.ax.set_title(f'Результаты по группам{title_suffix}')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
    
    def _plot_grade_distribution(self, results):
        """График распределения оценок"""
        bins = [0, 60, 70, 80, 90, 100]
        labels = ['0-60%', '61-70%', '71-80%', '81-90%', '91-100%']
        
        counts, _ = np.histogram(results, bins=bins)
        bars = self.ax.bar(labels, counts)
        self.ax.set_ylabel('Количество студентов')
        self.ax.set_title('Распределение результатов')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom')
    
    def _plot_lab_results(self, results):
        """График результатов по лабораторным работам"""
        labs = [row[4] for row in self.data]
        unique_labs = sorted(list(set(labs)))
        lab_means = [np.mean([r for r, l in zip(results, labs) if l == lab]) 
                    for lab in unique_labs]
        
        bars = self.ax.bar(unique_labs, lab_means)
        self.ax.set_ylabel('Средний результат (%)')
        self.ax.set_title('Результаты по лабораторным работам')
        
        # Поворачиваем подписи для лучшей читаемости
        plt.xticks(rotation=45, ha='right')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
