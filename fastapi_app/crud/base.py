from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    """Базовый класс для всех моделей для работы с базой данных."""

    def __init__(self, model: type) -> None:
        """Конструктор базового класса для работы с базой данных.

        :param model: модель.
        """
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ) -> None:
        """Получить объект по id.

        :param obj_id: id объекта
        :param session: сессия базы данных
        :return: объект.
        """
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id,
            ),
        )
        return db_obj.scalars().first()

    async def get_all(self, session: AsyncSession) -> List[dict]:
        """Получить все объекты."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    @staticmethod
    async def update(
            obj: type,
            session: AsyncSession,
    ) -> None:
        """Обновить объект."""
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @staticmethod
    async def remove(
            obj: type,
            session: AsyncSession,
    ) -> None:
        """Удалить объект."""
        await session.delete(obj)
        await session.commit()
        return obj

    async def create(
            self,
            obj_in: dict,
            session: AsyncSession,
    ) -> type:
        """Создать новый объект.

        :param obj_in: словарь с данными для создания объекта
        :param session: сессия базы данных
        :return: созданный объект
        """
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
