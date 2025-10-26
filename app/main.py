from fastapi import FastAPI

from app.api.v1 import auth, users, videojobs

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(videojobs.router)


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
