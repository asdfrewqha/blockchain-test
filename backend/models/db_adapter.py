# from uuid import uuid4
import logging
import uuid
from typing import Any, List

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import and_
from thefuzz import fuzz, process

from backend.core.config import DATABASE_URL
from backend.models.db_tables import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncDatabaseAdapter:
    def __init__(self, database_url: str = DATABASE_URL) -> None:
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
        )
        self.SessionLocal = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize_tables(self) -> None:
        logger.info("Tables are created or exists")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_all(self, model) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model))
            return result.scalars().all()

    async def get_by_id(self, model, id) -> Any:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model).where(model.id == id))
            return result.scalar_one_or_none()

    async def get_by_value(self, model, parameter: str, parameter_value: Any) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(model).where(getattr(model, parameter) == parameter_value)
            )
            return result.scalars().all()

    async def get_by_values(self, model, conditions: dict) -> List[Any]:
        async with self.SessionLocal() as session:
            query = select(model)
            for key, value in conditions.items():
                query = query.where(getattr(model, key) == value)
            result = await session.execute(query)
            return result.scalars().all()

    async def insert(self, model, insert_dict: dict) -> Any:
        async with self.SessionLocal() as session:
            record = model(**insert_dict)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def update_by_id(self, model, record_id: int, updates: dict):
        async with self.SessionLocal() as session:
            stmt = update(model).where(model.id == record_id).values(**updates)
            await session.execute(stmt)
            await session.commit()

    async def update_by_value(self, model, filters: dict, updates: dict):
        async with self.SessionLocal() as session:
            conditions = [getattr(model, key) == value for key, value in filters.items()]
            stmt = update(model).where(and_(*conditions)).values(**updates)
            await session.execute(stmt)
            await session.commit()

    async def delete(self, model, id: int) -> Any:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model).where(model.id == id))
            record = result.scalar_one_or_none()
            if record:
                await session.delete(record)
                await session.commit()
            return record

    async def delete_by_value(self, model, parameter: str, parameter_value: Any) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(model).where(getattr(model, parameter) == parameter_value)
            )
            records = result.scalars().all()
            for record in records:
                await session.delete(record)
            await session.commit()
            return records

    async def find_similar_value(
        self,
        model,
        column_name: str,
        search_value: str,
        limit: int = 5,
        similarity_threshold: int = 35,
    ) -> list:
        all_records = await self.get_all(model)
        values = []
        records_map = {}
        for record in all_records:
            value = getattr(record, column_name)
            if value not in records_map:
                records_map[value] = []
            records_map[value].append(record)
            values.append(value)
        results = process.extractBests(
            search_value,
            list(set(values)),
            limit=limit * 5,
            score_cutoff=similarity_threshold,
            scorer=fuzz.token_sort_ratio,
        )
        output = []
        for value, score in results:
            for record in records_map[value]:
                record_dict = {}
                for column in record.__table__.columns:
                    record_dict[column.name] = getattr(record, column.name)
                record_dict["similarity"] = score
                output.append(record_dict)
        output.sort(key=lambda x: x["similarity"], reverse=True)
        return output[:limit]

    async def execute_with_request(self, request) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(request)
            await session.commit()
            return result.fetchall()

    async def get_polls_voted_by_user(self, user_id: uuid.UUID):
        from sqlalchemy import select

        from backend.models.db_tables import Poll, Vote

        async with self.SessionLocal() as session:
            stmt = (
                select(Poll)
                .join(Vote, Vote.poll_id == Poll.id)
                .where(Vote.user_id == user_id)
                .options(selectinload(Poll.votes))
                .distinct(Poll.id)
            )
            result = await session.execute(stmt)
            return result.scalars().all()


adapter = AsyncDatabaseAdapter()
