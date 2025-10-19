from fastapi import HTTPException
from fastcrud import FastCRUD
from sqlalchemy.exc import NoResultFound


class CustomFastCRUD(FastCRUD):
    async def get(self, *args, **kwargs):
        # Raise 404 if not found
        item = await super().get(*args, **kwargs)
        if not item:
            raise HTTPException(404, "Item not found")
        return item

    async def get_multi(self, *args, **kwargs):
        # Return the list of items directly
        result = await super().get_multi(*args, **kwargs)
        return result.get("data")

    async def update(self, **kwargs):
        # Raise 404 if not found and return updated item
        try:
            kwargs.setdefault("return_as_model", True)
            return await super().update(**kwargs)
        except NoResultFound:
            raise HTTPException(404, "Item not found")

    async def delete(self, *args, **kwargs):
        # Raise 404 if not found
        try:
            return await super().delete(*args, **kwargs)
        except NoResultFound:
            raise HTTPException(404, "Item not found")
