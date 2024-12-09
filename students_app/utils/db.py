"""Утилиты для работы с базой данных"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional, TypeVar

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class DatabaseManager:
    """Менеджер базы данных"""

    def __init__(self, database_url: str):
        """
        Инициализация менеджера базы данных

        Args:
            database_url: URL базы данных (например, 'sqlite+aiosqlite:///questions.db')
        """
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self.async_session: Optional[async_sessionmaker[AsyncSession]] = None

    async def init(self):
        """Инициализация подключения к базе данных"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # Отключаем вывод SQL запросов
                pool_pre_ping=True,  # Проверка соединения перед использованием
                pool_size=5,  # Размер пула соединений
                max_overflow=10,  # Максимальное количество дополнительных соединений
            )

            self.async_session = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            logger.info(f"Database connection initialized: {self.database_url}")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    async def close(self):
        """Закрытие подключения к базе данных"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Контекстный менеджер для сессии базы данных"""
        if not self.async_session:
            await self.init()

        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise

    async def check_connection(self) -> bool:
        """Проверка подключения к базе данных"""
        try:
            async with self.session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    async def create_backup(self, backup_dir: Optional[str] = None) -> str:
        """
        Создание резервной копии базы данных

        Args:
            backup_dir: Директория для сохранения резервной копии

        Returns:
            Путь к файлу резервной копии
        """
        if not backup_dir:
            backup_dir = os.path.join(os.path.expanduser("~"), "Загрузки", "Backups")

        os.makedirs(backup_dir, exist_ok=True)

        # Извлекаем имя файла из URL базы данных
        db_file = self.database_url.split("/")[-1]
        backup_file = os.path.join(
            backup_dir,
            f"{os.path.splitext(db_file)[0]}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
        )

        try:
            # Для SQLite можно просто скопировать файл
            if self.database_url.startswith("sqlite"):
                import shutil

                db_path = self.database_url.replace("sqlite+aiosqlite:///", "")
                shutil.copy2(db_path, backup_file)
                logger.info(f"Database backup created: {backup_file}")
                return backup_file
            else:
                raise NotImplementedError(
                    "Backup is only supported for SQLite databases"
                )

        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise

    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Получение информации о таблице

        Args:
            table_name: Имя таблицы

        Returns:
            Словарь с информацией о таблице
        """
        valid_table_names = [
            "students",
            "courses",
            "enrollments",
        ]  # Replace with actual table names
        if table_name not in valid_table_names:
            raise ValueError(f"Invalid table name: {table_name}")
        try:
            async with self.session() as session:
                valid_table_names = [
                    "students",
                    "courses",
                    "enrollments",
                ]  # Replace with actual table names
                if table_name not in valid_table_names:
                    raise ValueError(f"Invalid table name: {table_name}")

                result = await session.execute(
                    text("SELECT COUNT(*) FROM :table_name"), {"table_name": table_name}
                )
                row_count = result.scalar()

                result = await session.execute(
                    text("PRAGMA table_info(:table_name)"), {"table_name": table_name}
                )
                columns = result.fetchall()

                # Получаем размер таблицы (только для SQLite)
                result = await session.execute(
                    text(
                        "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
                    )
                )
                size_bytes = result.scalar()

                return {
                    "table_name": table_name,
                    "row_count": row_count,
                    "size_bytes": size_bytes,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "nullable": not col[3],
                            "primary_key": bool(col[5]),
                        }
                        for col in columns
                    ],
                }

        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            raise

    async def vacuum(self):
        """Оптимизация базы данных"""
        try:
            async with self.session() as session:
                await session.execute(text("VACUUM"))
                logger.info("Database optimized")
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
            raise

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики базы данных

        Returns:
            Словарь со статистикой
        """
        try:
            async with self.session() as session:
                # Получаем список таблиц
                result = await session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result.fetchall()]

                stats = {"tables": {}, "total_size": 0, "total_rows": 0}

                # Собираем статистику по каждой таблице
                for table in tables:
                    table_info = await self.get_table_info(table)
                    stats["tables"][table] = table_info
                    stats["total_size"] += table_info["size_bytes"]
                    stats["total_rows"] += table_info["row_count"]

                return stats

        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            raise
