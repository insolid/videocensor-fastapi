from fastapi import FastAPI

from app.api.v1 import auth, subscriptions, users, videojobs

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(videojobs.router)
app.include_router(subscriptions.router)


@app.get("/clear-db")
async def clear_db():
    from app.core.db import engine
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"deatail": "Database cleared"}
