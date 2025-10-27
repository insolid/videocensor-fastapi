from typing import Any

from fastapi import HTTPException
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute


async def exists_or_error(
    db: AsyncSession, model_field: InstrumentedAttribute, value: Any
):
    """Raise error response if no record found"""
    stmt = select(exists().where(model_field == value))
    exists_ = await db.scalar(stmt)
    if not exists_:
        msg = f"No {model_field.class_.__name__} with {model_field.key} = {value}"
        raise HTTPException(400, msg)
