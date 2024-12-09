"""Утилиты для логирования"""
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from loguru import logger


def setup_logger(
    debug_mode: bool = False,
    log_dir: Optional[str] = None,
    app_name: str = "students_app"
) -> None:
    """
    Настройка логгера

    Args:
        debug_mode: Режим отладки
        log_dir: Директория для логов
        app_name: Имя приложения
    """
    # Удаляем стандартный обработчик
    logger.remove()

    # Настраиваем формат логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Создаем директорию для логов
    if not log_dir:
        log_dir = Path.home() / "AppData" / "Local" / app_name / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)

    # Файл для всех логов
    log_file = log_dir / f"{app_name}.log"
    logger.add(
        str(log_file),
        format=log_format,
        level="DEBUG" if debug_mode else "INFO",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )

    # Отдельный файл для ошибок
    error_file = log_dir / f"{app_name}_error.log"
    logger.add(
        str(error_file),
        format=log_format,
        level="ERROR",
        rotation="1 week",
        retention="3 months",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )

    # Вывод в консоль
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if debug_mode else "INFO",
        colorize=True
    )

    logger.info(f"Logger initialized. Debug mode: {debug_mode}")


class LoggerStats:
    """Класс для сбора статистики логов"""

    def __init__(self, log_dir: Optional[str] = None, app_name: str = "students_app"):
        self.log_dir = Path(log_dir) if log_dir else Path.home() / "AppData" / "Local" / app_name / "logs"
        self.app_name = app_name

    def get_log_files(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о файлах логов"""
        log_files = {}

        for file in self.log_dir.glob(f"{self.app_name}*.log*"):
            stats = file.stat()
            log_files[file.name] = {
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime),
                "modified": datetime.fromtimestamp(stats.st_mtime),
                "compressed": file.suffix == ".zip"
            }

        return log_files

    def get_error_stats(self) -> Dict[str, int]:
        """Получение статистики ошибок"""
        error_stats = {
            "critical": 0,
            "error": 0,
            "warning": 0
        }

        error_file = self.log_dir / f"{self.app_name}_error.log"
        if error_file.exists():
            with open(error_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "CRITICAL" in line:
                        error_stats["critical"] += 1
                    elif "ERROR" in line:
                        error_stats["error"] += 1
                    elif "WARNING" in line:
                        error_stats["warning"] += 1

        return error_stats

    def clear_old_logs(self, days: int = 30) -> int:
        """
        Удаление старых логов

        Args:
            days: Количество дней, после которых лог считается старым

        Returns:
            Количество удаленных файлов
        """
        deleted = 0
        current_time = datetime.now().timestamp()

        for file in self.log_dir.glob(f"{self.app_name}*.log*"):
            if (current_time - file.stat().st_mtime) > (days * 24 * 60 * 60):
                file.unlink()
                deleted += 1

        return deleted


def log_exception(e: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Логирование исключения с дополнительным контекстом

    Args:
        e: Исключение
        context: Дополнительный контекст
    """
    error_info = {
        "type": type(e).__name__,
        "message": str(e),
        "context": context or {}
    }

    logger.exception(f"Exception occurred: {error_info}")


def log_function_call(func):
    """Декоратор для логирования вызовов функций"""
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            log_exception(e, {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            })
            raise
    return wrapper


def log_method_call(method):
    """Декоратор для логирования вызовов методов класса"""
    def wrapper(self, *args, **kwargs):
        logger.debug(f"Calling {self.__class__.__name__}.{method.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = method(self, *args, **kwargs)
            logger.debug(f"{self.__class__.__name__}.{method.__name__} completed successfully")
            return result
        except Exception as e:
            log_exception(e, {
                "class": self.__class__.__name__,
                "method": method.__name__,
                "args": args,
                "kwargs": kwargs
            })
            raise
    return wrapper
