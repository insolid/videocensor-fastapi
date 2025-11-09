from unittest.mock import patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscriptions import Subscription
from app.models.users import User
from app.models.videojobs import Language, Status, VideoJob, VisualConfig
from app.schemas.videojobs import VideoJobRead, VideoJobReadShort

pytestmark = pytest.mark.asyncio


async def test_auth_required_to_access_videojobs(client: AsyncClient, app: FastAPI):
    res = await client.get(app.url_path_for("videojobs:list"))
    assert res.status_code == 401


async def test_subscription_required_to_create_videojob(
    auth_client: AsyncClient, app: FastAPI
):
    res = await auth_client.post(app.url_path_for("videojobs:create"), json={})
    assert res.status_code == 403


async def test_get_videojob(
    app: FastAPI, auth_client: AsyncClient, test_user: User, db: AsyncSession
):
    vj = VideoJob(user=test_user, language=Language.EN)
    db.add(vj)
    await db.commit()
    await db.refresh(vj)

    res = await auth_client.get(app.url_path_for("videojobs:get_one", id=vj.id))
    assert res.status_code == 200
    vj_data = VideoJobRead.model_validate(res.json())
    assert vj_data.id == vj.id
    assert vj_data.language == vj.language


async def test_list_videojobs(
    app: FastAPI, auth_client: AsyncClient, test_user: User, db: AsyncSession
):
    vj1 = VideoJob(user=test_user, language=Language.EN)
    vj2 = VideoJob(user=test_user, language=Language.RU)
    db.add_all([vj1, vj2])
    await db.commit()

    res = await auth_client.get(app.url_path_for("videojobs:list"))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


async def test_create_videojob(
    app: FastAPI, auth_client: AsyncClient, test_user: User, db: AsyncSession
):
    db.add(Subscription(user=test_user, is_active=True))
    await db.commit()

    payload = {
        "language": "en",
        "visual_config": {"smoking": True},
        "audio_config": {"profanity": True},
    }
    res = await auth_client.post(app.url_path_for("videojobs:create"), json=payload)
    assert res.status_code == 201
    vj = VideoJobRead.model_validate(res.json())
    assert vj.language == payload["language"]
    assert vj.visual_config.smoking is payload["visual_config"]["smoking"]  # type: ignore
    assert vj.audio_config.profanity is payload["audio_config"]["profanity"]  # type: ignore


async def test_update_videojob(
    app: FastAPI, auth_client: AsyncClient, test_user: User, db: AsyncSession
):
    vj = VideoJob(
        user=test_user,
        language=Language.EN,
        visual_config=VisualConfig(smoking=True),
    )
    db.add_all([vj, Subscription(user=test_user, is_active=True)])
    await db.commit()

    payload = {"language": "ru", "visual_config": {"smoking": False}}
    res = await auth_client.patch(
        app.url_path_for("videojobs:update", id=vj.id), json=payload
    )
    assert res.status_code == 200
    updated_vj = VideoJobRead.model_validate(res.json())
    assert updated_vj.language == payload["language"]
    assert updated_vj.visual_config.smoking is payload["visual_config"]["smoking"]  # type: ignore


async def test_can_update_only_pending_videojob(
    app: FastAPI, auth_client: AsyncClient, test_user: User, db: AsyncSession
):
    vj = VideoJob(
        user=test_user,
        language=Language.EN,
        status=Status.PROCESSING,
    )
    db.add_all([vj, Subscription(user=test_user, is_active=True)])
    await db.commit()

    res = await auth_client.patch(
        app.url_path_for("videojobs:update", id=vj.id), json={}
    )
    assert res.status_code == 400


async def test_upload_video_file_for_videojob(
    app: FastAPI,
    auth_client: AsyncClient,
    test_user: User,
    db: AsyncSession,
):
    vj = VideoJob(
        user=test_user,
        language=Language.EN,
        status=Status.PENDING,
    )
    db.add_all([vj, Subscription(user=test_user, is_active=True)])
    await db.commit()

    file = {"file": ("test.mp4", "content", "video/mp4")}

    with patch("app.api.v1.videojobs.aiofiles.open"), patch(
        "app.api.v1.videojobs.os.makedirs"
    ):
        res = await auth_client.post(
            app.url_path_for("videojobs:upload_file", id=vj.id), files=file
        )
    assert res.status_code == 200
    vj = VideoJobReadShort.model_validate(res.json())
    assert vj.status == Status.PROCESSING
