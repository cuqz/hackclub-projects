"""Unit tests for EcosystemScanProfile storage repository methods (v1.6.0 P0.1)."""

from __future__ import annotations

import pytest_asyncio

from aiteam.storage.connection import close_db
from aiteam.storage.repository import StorageRepository


@pytest_asyncio.fixture()
async def repo() -> StorageRepository:
    r = StorageRepository(db_url="sqlite+aiosqlite://")
    await r.init_db()
    yield r  # type: ignore[misc]
    await close_db()


PROJECT_ID = "proj-scan-001"

_SAMPLE_PROFILE = {
    "active_definition": {
        "primary_metric_kind": "popularity_rank",
        "active_top_n_per_source": 200,
        "min_popularity_floor": {"github": 1000},
    },
    "inactive_signals": {"no_activity_days": 180},
    "archive_signals": {"no_activity_days": 730},
    "alert_thresholds": {"max_new_per_scan": 50},
}


async def test_get_active_scan_profile_returns_none_when_empty(repo: StorageRepository) -> None:
    result = await repo.get_active_scan_profile(PROJECT_ID)
    assert result is None


async def test_create_scan_profile_is_active(repo: StorageRepository) -> None:
    sp = await repo.create_or_update_scan_profile(PROJECT_ID, _SAMPLE_PROFILE)
    assert sp.id
    assert sp.project_id == PROJECT_ID
    assert sp.is_active is True
    assert sp.version == 1
    assert sp.profile["active_definition"]["active_top_n_per_source"] == 200


async def test_get_active_scan_profile_returns_created(repo: StorageRepository) -> None:
    await repo.create_or_update_scan_profile(PROJECT_ID, _SAMPLE_PROFILE)
    sp = await repo.get_active_scan_profile(PROJECT_ID)
    assert sp is not None
    assert sp.is_active is True
    assert sp.version == 1


async def test_update_scan_profile_increments_version(repo: StorageRepository) -> None:
    await repo.create_or_update_scan_profile(PROJECT_ID, _SAMPLE_PROFILE)
    updated_profile = dict(_SAMPLE_PROFILE)
    updated_profile["inactive_signals"] = {"no_activity_days": 90}

    sp2 = await repo.create_or_update_scan_profile(PROJECT_ID, updated_profile)
    assert sp2.version == 2
    assert sp2.profile["inactive_signals"]["no_activity_days"] == 90


async def test_update_scan_profile_deactivates_old_version(repo: StorageRepository) -> None:
    await repo.create_or_update_scan_profile(PROJECT_ID, _SAMPLE_PROFILE)
    await repo.create_or_update_scan_profile(PROJECT_ID, _SAMPLE_PROFILE)

    # Only the latest version should be active
    active = await repo.get_active_scan_profile(PROJECT_ID)
    assert active is not None
    assert active.version == 2


async def test_scan_profile_project_isolation(repo: StorageRepository) -> None:
    await repo.create_or_update_scan_profile(PROJECT_ID, _SAMPLE_PROFILE)

    other_profile = await repo.get_active_scan_profile("other-project")
    assert other_profile is None


async def test_multiple_updates_keep_latest_active(repo: StorageRepository) -> None:
    for i in range(1, 5):
        profile = dict(_SAMPLE_PROFILE)
        profile["_version_marker"] = i
        await repo.create_or_update_scan_profile(PROJECT_ID, profile)

    active = await repo.get_active_scan_profile(PROJECT_ID)
    assert active is not None
    assert active.version == 4
    assert active.profile["_version_marker"] == 4
