from fastapi import FastAPI
from sqlalchemy import delete

from app.api.v1 import auth, users, videojobs
from app.core.db import SessionDep
from app.models.users import User
from app.models.videojobs import AudioConfig, VideoJob, VisualConfig

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(videojobs.router)


@app.delete("/tables")
async def delete_tables(db: SessionDep):
    await db.execute(delete(VideoJob))
    await db.execute(delete(VisualConfig))
    await db.execute(delete(AudioConfig))
    await db.execute(delete(User))
    await db.commit()
