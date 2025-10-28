from fastapi import HTTPException
from fastcrud import FastCRUD
from sqlalchemy.exc import NoResultFound


class CustomFastCRUD(FastCRUD):
    async def get(self, *args, **kwargs):
        item = await super().get(*args, **kwargs)
        if not item:
            raise HTTPException(404, f"{self.model.__name__} not found")
        return item

    async def get_joined(self, *args, **kwargs):
        item = await super().get_joined(*args, **kwargs)
        if not item:
            raise HTTPException(404, f"{self.model.__name__} not found")
        return item

    async def get_multi(self, *args, **kwargs):
        result = await super().get_multi(*args, **kwargs)
        return result.get("data")

    async def get_multi_joined(self, *args, **kwargs):
        result = await super().get_multi_joined(*args, **kwargs)
        return result.get("data")

    async def update(self, **kwargs):
        try:
            kwargs.setdefault("return_as_model", True)
            return await super().update(**kwargs)
        except NoResultFound:
            raise HTTPException(404, f"{self.model.__name__} not found")

    async def delete(self, *args, **kwargs):
        try:
            return await super().delete(*args, **kwargs)
        except NoResultFound:
            raise HTTPException(404, f"{self.model.__name__} not found")
