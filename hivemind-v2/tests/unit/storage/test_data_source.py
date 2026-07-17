"""Unit tests for EcosystemDataSource storage repository methods (v1.6.0 P0.1)."""

from __future__ import annotations

import pytest
import pytest_asyncio

from aiteam.storage.connection import close_db
from aiteam.storage.repository import StorageRepository
from aiteam.types import DataSourceKind


@pytest_asyncio.fixture()
async def repo() -> StorageRepository:
    r = StorageRepository(db_url="sqlite+aiosqlite://")
    await r.init_db()
    yield r  # type: ignore[misc]
    await close_db()


PROJECT_ID = "proj-test-001"


async def test_create_data_source_returns_model(repo: StorageRepository) -> None:
    ds = await repo.create_data_source(
        project_id=PROJECT_ID,
        kind=DataSourceKind.GITHUB,
        name="GitHub default",
        config={"queries": ["topic:claude-code"]},
    )
    assert ds.id
    assert ds.project_id == PROJECT_ID
    assert ds.kind == DataSourceKind.GITHUB
    assert ds.name == "GitHub default"
    assert ds.config["queries"] == ["topic:claude-code"]
    assert ds.enabled is True
    assert ds.version == 1


async def test_list_data_sources_empty(repo: StorageRepository) -> None:
    result = await repo.list_data_sources(PROJECT_ID)
    assert result == []


async def test_list_data_sources_returns_created(repo: StorageRepository) -> None:
    await repo.create_data_source(PROJECT_ID, DataSourceKind.GITHUB, "gh")
    await repo.create_data_source(PROJECT_ID, DataSourceKind.NPM, "npm")

    result = await repo.list_data_sources(PROJECT_ID)
    assert len(result) == 2
    kinds = {ds.kind for ds in result}
    assert DataSourceKind.GITHUB in kinds
    assert DataSourceKind.NPM in kinds


async def test_list_data_sources_project_isolation(repo: StorageRepository) -> None:
    await repo.create_data_source(PROJECT_ID, DataSourceKind.GITHUB, "gh")
    await repo.create_data_source("other-project", DataSourceKind.NPM, "npm")

    result = await repo.list_data_sources(PROJECT_ID)
    assert len(result) == 1
    assert result[0].kind == DataSourceKind.GITHUB


async def test_update_data_source_name(repo: StorageRepository) -> None:
    ds = await repo.create_data_source(PROJECT_ID, DataSourceKind.GITHUB, "old name")

    updated = await repo.update_data_source(ds.id, name="new name")
    assert updated.name == "new name"
    assert updated.version == 2  # version increments on update


async def test_update_data_source_config(repo: StorageRepository) -> None:
    ds = await repo.create_data_source(
        PROJECT_ID, DataSourceKind.GITHUB, "gh", config={"queries": ["old"]}
    )
    updated = await repo.update_data_source(ds.id, config={"queries": ["new1", "new2"]})
    assert updated.config["queries"] == ["new1", "new2"]


async def test_update_data_source_enabled(repo: StorageRepository) -> None:
    ds = await repo.create_data_source(PROJECT_ID, DataSourceKind.GITHUB, "gh")
    assert ds.enabled is True

    updated = await repo.update_data_source(ds.id, enabled=False)
    assert updated.enabled is False


async def test_disable_data_source(repo: StorageRepository) -> None:
    ds = await repo.create_data_source(PROJECT_ID, DataSourceKind.GITHUB, "gh")
    await repo.disable_data_source(ds.id)

    sources = await repo.list_data_sources(PROJECT_ID)
    disabled = next(s for s in sources if s.id == ds.id)
    assert disabled.enabled is False


async def test_update_data_source_not_found(repo: StorageRepository) -> None:
    from aiteam.api.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await repo.update_data_source("nonexistent-id", name="x")


async def test_all_data_source_kinds_accepted(repo: StorageRepository) -> None:
    for kind in DataSourceKind:
        ds = await repo.create_data_source(PROJECT_ID, kind, f"{kind.value}-source")
        assert ds.kind == kind
