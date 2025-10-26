import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.schemas.videojobs import VideoJobCreate

pytestmark = pytest.mark.asyncio


async def test_auth_required_to_access_videojobs(client: AsyncClient, app: FastAPI):
    response = await client.get(app.url_path_for("videojobs:list"))
    assert response.status_code == 401


async def test_create_videojob(app: FastAPI, auth_client: AsyncClient):
    payload = {"language": "en"}
    res = await auth_client.post(app.url_path_for("videojobs:create"), json=payload)
    videojob = VideoJobCreate.model_validate(res.json())
    assert res.status_code == 201
    assert videojob.language == payload["language"]
