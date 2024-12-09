"""
Базовый класс репозитория для работы с данными
"""
from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from models.base import Base

T = TypeVar('T', bound=Base)

class Repository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить объект по ID"""
        try:
            result = await self.session.execute(
                select(self.model).filter(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            raise

    async def get_all(self) -> List[T]:
        """Получить все объекты"""
        try:
            result = await self.session.execute(select(self.model))
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}s: {e}")
            raise

    async def add(self, item: T) -> T:
        """Добавить новый объект"""
        try:
            self.session.add(item)
            await self.session.commit()
            await self.session.refresh(item)
            return item
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error adding {self.model.__name__}: {e}")
            raise

    async def update(self, id: int, values: dict) -> Optional[T]:
        """Обновить объект"""
        try:
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**values)
                .returning(self.model)
            )
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise

    async def delete(self, id: int) -> bool:
        """Удалить объект"""
        try:
            result = await self.session.execute(
                delete(self.model).where(self.model.id == id)
            )
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise

    async def exists(self, id: int) -> bool:
        """Проверить существование объекта"""
        try:
            result = await self.session.execute(
                select(self.model.id).filter(self.model.id == id)
            )
            return result.scalar() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {e}")
            raise
