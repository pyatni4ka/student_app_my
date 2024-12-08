"""Менеджер окон приложения"""
import logging
from PyQt5.QtWidgets import QMainWindow, QWidget

logger = logging.getLogger(__name__)

class WindowManager:
    """Класс для управления окнами приложения"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls)
            cls._instance.current_window = None
            logger.info("Создан новый экземпляр WindowManager")
        return cls._instance
    
    def show_window(self, window_class_or_instance, instance=None):
        """
        Показать новое окно
        
        Args:
            window_class_or_instance: класс окна или экземпляр окна для отображения
            instance: опциональный экземпляр окна (для обратной совместимости)
        """
        try:
            logger.info(f"Попытка показать окно класса {window_class_or_instance.__name__ if isinstance(window_class_or_instance, type) else window_class_or_instance.__class__.__name__}")
            
            # Определяем, что нам передали - класс или экземпляр
            if instance is not None:
                new_window = instance
            elif isinstance(window_class_or_instance, (QMainWindow, QWidget)):
                new_window = window_class_or_instance
            else:
                if not issubclass(window_class_or_instance, (QMainWindow, QWidget)):
                    error_msg = "window_class должен быть подклассом QMainWindow или QWidget"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                new_window = window_class_or_instance()
            
            logger.debug(f"Создано новое окно класса {new_window.__class__.__name__}")
            
            # Закрываем текущее окно, если оно существует
            if self.current_window is not None:
                logger.debug(f"Закрываем текущее окно класса {self.current_window.__class__.__name__}")
                self.current_window.close()
                self.current_window.deleteLater()
                
            # Устанавливаем и показываем новое окно
            self.current_window = new_window
            self.current_window.show()
            logger.info(f"Успешно показано новое окно класса {new_window.__class__.__name__}")
            
        except Exception as e:
            error_msg = f"Ошибка при создании окна: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
