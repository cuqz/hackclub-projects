"""生态标签字典存储层单元测试 — upsert / get / list 覆盖。"""

from __future__ import annotations

import pytest_asyncio

from aiteam.storage.connection import close_db
from aiteam.storage.repository import StorageRepository
from aiteam.types import EcosystemTag, EcosystemTagCategory


@pytest_asyncio.fixture()
async def repo() -> StorageRepository:
    """内存 SQLite 仓库用于测试。"""
    r = StorageRepository(db_url="sqlite+aiosqlite://")
    await r.init_db()
    yield r  # type: ignore[misc]
    await close_db()


def _make_tag(
    name: str = "memory_system",
    category: EcosystemTagCategory = EcosystemTagCategory.CAPABILITY,
    aliases: list[str] | None = None,
    description: str = "记忆系统",
) -> EcosystemTag:
    return EcosystemTag(
        name=name,
        category=category,
        aliases=aliases or [],
        description=description,
    )


async def test_upsert_new_tag_persists(repo: StorageRepository) -> None:
    """新标签 upsert 后能按 name 检索。"""
    tag = _make_tag()
    await repo.upsert_tag(tag)

    fetched = await repo.get_tag_by_name("memory_system")
    assert fetched is not None
    assert fetched.category == EcosystemTagCategory.CAPABILITY
    assert fetched.description == "记忆系统"


async def test_upsert_tag_updates_existing(repo: StorageRepository) -> None:
    """同名标签再次 upsert 会更新 aliases / category / description。"""
    await repo.upsert_tag(_make_tag())

    updated = _make_tag(aliases=["mem", "long-term"], description="新描述")
    await repo.upsert_tag(updated)

    fetched = await repo.get_tag_by_name("memory_system")
    assert fetched is not None
    assert set(fetched.aliases) == {"mem", "long-term"}
    assert fetched.description == "新描述"


async def test_get_tag_by_name_missing_returns_none(repo: StorageRepository) -> None:
    """未注册的 name 返回 None。"""
    assert await repo.get_tag_by_name("non-existent") is None


async def test_list_tags_filter_by_category(repo: StorageRepository) -> None:
    """按 category 过滤只返回对应分类的标签。"""
    await repo.upsert_tag(_make_tag("python", EcosystemTagCategory.TECH_STACK))
    await repo.upsert_tag(_make_tag("rust", EcosystemTagCategory.TECH_STACK))
    await repo.upsert_tag(_make_tag("framework", EcosystemTagCategory.POSITIONING))

    tech = await repo.list_tags(category="tech_stack")
    pos = await repo.list_tags(category="positioning")
    assert {t.name for t in tech} == {"python", "rust"}
    assert {t.name for t in pos} == {"framework"}


async def test_list_tags_no_filter_returns_all(repo: StorageRepository) -> None:
    """不传 category 则返回所有标签。"""
    await repo.upsert_tag(_make_tag("a", EcosystemTagCategory.CAPABILITY))
    await repo.upsert_tag(_make_tag("b", EcosystemTagCategory.MATURITY))

    rows = await repo.list_tags()
    names = {t.name for t in rows}
    assert {"a", "b"} <= names
