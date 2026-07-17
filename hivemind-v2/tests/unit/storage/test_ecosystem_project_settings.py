"""v1.5.0-A: EcosystemProjectSettings 单元测试 (项目自定义阈值)。"""

from __future__ import annotations

import pytest
import pytest_asyncio

from aiteam.storage.connection import close_db
from aiteam.storage.repository import StorageRepository
from aiteam.types import EcosystemProjectSettings


@pytest_asyncio.fixture()
async def repo() -> StorageRepository:
    r = StorageRepository(db_url="sqlite+aiosqlite://")
    await r.init_db()
    yield r  # type: ignore[misc]
    await close_db()


@pytest_asyncio.fixture()
async def project_id(repo: StorageRepository) -> str:
    p = await repo.create_project(
        name="AI Team OS",
        root_path="C:/test/ai-team-os",
        description="test",
    )
    return p.id


@pytest.mark.asyncio
async def test_get_settings_missing_returns_none(
    repo: StorageRepository, project_id: str
) -> None:
    """无设置时 get 返回 None。"""
    settings = await repo.get_ecosystem_project_settings(project_id)
    assert settings is None


@pytest.mark.asyncio
async def test_ensure_settings_creates_default_for_normal_project(
    repo: StorageRepository,
) -> None:
    """普通项目使用通用默认值。"""
    p = await repo.create_project(name="my-app", root_path="/tmp/a")
    settings = await repo.ensure_ecosystem_project_settings(p.id, is_ai_team_os=False)
    assert settings.project_id == p.id
    assert settings.min_stars == 1000
    assert settings.top_n == 100
    assert settings.focus_topics == []
    assert settings.shallow_concurrency == 5


@pytest.mark.asyncio
async def test_ensure_settings_creates_strict_default_for_ai_team_os(
    repo: StorageRepository, project_id: str
) -> None:
    """AI Team OS 项目使用严格默认值 (min_stars=5000)。"""
    settings = await repo.ensure_ecosystem_project_settings(
        project_id, is_ai_team_os=True
    )
    assert settings.min_stars == 5000
    assert settings.top_n == 200
    assert "claude-code" in settings.focus_topics
    assert "mcp" in settings.focus_topics


@pytest.mark.asyncio
async def test_ensure_settings_idempotent(
    repo: StorageRepository, project_id: str
) -> None:
    """已存在时 ensure 不覆盖，幂等。"""
    first = await repo.ensure_ecosystem_project_settings(
        project_id, is_ai_team_os=True
    )
    # 用户手动调整
    first.min_stars = 9999
    await repo.upsert_ecosystem_project_settings(first)

    # ensure 不应覆盖
    second = await repo.ensure_ecosystem_project_settings(
        project_id, is_ai_team_os=True
    )
    assert second.min_stars == 9999


@pytest.mark.asyncio
async def test_upsert_settings_updates_existing(
    repo: StorageRepository, project_id: str
) -> None:
    """upsert 现有设置应更新所有字段。"""
    initial = EcosystemProjectSettings(
        project_id=project_id,
        min_stars=1000,
        top_n=100,
    )
    await repo.upsert_ecosystem_project_settings(initial)

    initial.min_stars = 2000
    initial.top_n = 50
    initial.focus_topics = ["test"]
    await repo.upsert_ecosystem_project_settings(initial)

    fetched = await repo.get_ecosystem_project_settings(project_id)
    assert fetched.min_stars == 2000
    assert fetched.top_n == 50
    assert fetched.focus_topics == ["test"]


@pytest.mark.asyncio
async def test_upsert_settings_requires_project_id(
    repo: StorageRepository,
) -> None:
    """空 project_id 应抛 ValueError。"""
    with pytest.raises(ValueError):
        await repo.upsert_ecosystem_project_settings(
            EcosystemProjectSettings(project_id="")
        )
