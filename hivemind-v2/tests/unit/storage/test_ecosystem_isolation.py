"""Stage J — Ecosystem 项目隔离 storage-layer 单元测试。

验证 5 张数据表（profile / scan_run / deep_review / repo_tag / relation）
在不同 project_id 之间完全隔离，且 EcosystemTag 字典保持全局可见。

设计要点：
- 同一个 in-memory SQLite DB 模拟真实环境（共享数据库 + 多项目作用域）。
- 测试两个 StorageRepository 实例分别 project_scope=p1 / p2。
- 通过显式 project_id 参数 + 隐式 _project_scope 两种路径都验证。
- 包含 backfill_ecosystem_to_project 的端到端验证场景。
"""

from __future__ import annotations

import pytest_asyncio

from aiteam.storage.connection import close_db
from aiteam.storage.repository import StorageRepository
from aiteam.types import (
    EcosystemDeepReview,
    EcosystemDeepReviewStatus,
    EcosystemRelation,
    EcosystemRelationType,
    EcosystemRepoProfile,
    EcosystemRepoTag,
    EcosystemScanRun,
    EcosystemScanStrategy,
    EcosystemTag,
    EcosystemTagCategory,
    EcosystemTagSource,
)

# 共享 in-memory DB —— 用 file::memory:?cache=shared 让多个连接看到相同表
# 但测试简化：复用同一个 db_url，在同一进程内 EnginePool 就能共享。
SHARED_DB_URL = "sqlite+aiosqlite://"


@pytest_asyncio.fixture()
async def shared_db():
    """初始化共享 in-memory DB 并返回三个 repo：
    - global_repo: 不带作用域，用于设置基础数据 + 全局查询
    - project_a / project_b: 两个独立项目 id
    """
    # 先用 global_repo 创建 schema + 项目
    global_repo = StorageRepository(db_url=SHARED_DB_URL)
    await global_repo.init_db()

    # 创建两个项目
    project_a_obj = await global_repo.create_project(
        name="Project-A",
        root_path="/tmp/project-a",
        description="测试项目 A",
    )
    project_b_obj = await global_repo.create_project(
        name="Project-B",
        root_path="/tmp/project-b",
        description="测试项目 B",
    )

    # 为每个项目创建 scoped repo（共享同一 db_url，因为 EnginePool 缓存了 engine）
    repo_a = StorageRepository(
        db_url=SHARED_DB_URL, project_scope=project_a_obj.id
    )
    repo_b = StorageRepository(
        db_url=SHARED_DB_URL, project_scope=project_b_obj.id
    )

    yield {
        "global": global_repo,
        "project_a_id": project_a_obj.id,
        "project_b_id": project_b_obj.id,
        "repo_a": repo_a,
        "repo_b": repo_b,
    }

    await close_db()


def _make_profile(repo_full_name: str = "test/repo") -> EcosystemRepoProfile:
    return EcosystemRepoProfile(
        repo_full_name=repo_full_name,
        name=repo_full_name.split("/")[-1],
        owner=repo_full_name.split("/")[0],
        description="iso-test",
        stars=100,
        topics=["claude"],
    )


# ------------------------------------------------------------------
# Profile isolation
# ------------------------------------------------------------------


async def test_profile_isolated_by_project_scope(shared_db) -> None:
    """两个项目 upsert 同一仓 → 各自得到独立行，互不可见。"""
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    p_a = _make_profile("anthropic/sdk")
    p_b = _make_profile("anthropic/sdk")
    await repo_a.upsert_ecosystem_profile(p_a)
    await repo_b.upsert_ecosystem_profile(p_b)

    a_list = await repo_a.search_ecosystem_profiles(limit=100)
    b_list = await repo_b.search_ecosystem_profiles(limit=100)

    assert len(a_list) == 1
    assert len(b_list) == 1
    assert a_list[0].project_id == shared_db["project_a_id"]
    assert b_list[0].project_id == shared_db["project_b_id"]
    # 同一 repo_full_name 两条独立 id
    assert a_list[0].id != b_list[0].id


async def test_get_profile_respects_project_scope(shared_db) -> None:
    """get_ecosystem_profile 在不同作用域下只看到自己项目的行。"""
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    await repo_a.upsert_ecosystem_profile(_make_profile("dummy/repo"))

    found_in_a = await repo_a.get_ecosystem_profile("dummy/repo")
    found_in_b = await repo_b.get_ecosystem_profile("dummy/repo")

    assert found_in_a is not None
    assert found_in_a.project_id == shared_db["project_a_id"]
    assert found_in_b is None  # 项目 B 看不到项目 A 的仓


async def test_explicit_project_id_overrides_scope(shared_db) -> None:
    """显式 project_id 参数优先于 _project_scope。"""
    repo_a = shared_db["repo_a"]
    pid_b = shared_db["project_b_id"]

    # repo_a 用显式 project_id=pid_b 写入项目 B
    await repo_a.upsert_ecosystem_profile(
        _make_profile("forced/projectb"), project_id=pid_b
    )

    # repo_a 自身（作用域=A）查不到
    assert await repo_a.get_ecosystem_profile("forced/projectb") is None
    # 通过显式 project_id=pid_b 查询 OK
    found = await repo_a.get_ecosystem_profile(
        "forced/projectb", project_id=pid_b
    )
    assert found is not None
    assert found.project_id == pid_b


# ------------------------------------------------------------------
# ScanRun isolation
# ------------------------------------------------------------------


async def test_scan_run_isolated(shared_db) -> None:
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    await repo_a.create_scan_run(
        EcosystemScanRun(strategy=EcosystemScanStrategy.INCREMENTAL)
    )
    await repo_a.create_scan_run(
        EcosystemScanRun(strategy=EcosystemScanStrategy.FULL)
    )
    await repo_b.create_scan_run(
        EcosystemScanRun(strategy=EcosystemScanStrategy.INCREMENTAL)
    )

    a_list = await repo_a.list_scan_runs(limit=100)
    b_list = await repo_b.list_scan_runs(limit=100)
    assert len(a_list) == 2
    assert len(b_list) == 1
    assert all(r.project_id == shared_db["project_a_id"] for r in a_list)
    assert b_list[0].project_id == shared_db["project_b_id"]


# ------------------------------------------------------------------
# DeepReview isolation
# ------------------------------------------------------------------


async def test_deep_review_isolated(shared_db) -> None:
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    # A 写一个 profile + 一个 deep review
    p_a = _make_profile("dr/test")
    await repo_a.upsert_ecosystem_profile(p_a)
    profile_a = (await repo_a.search_ecosystem_profiles(limit=10))[0]

    await repo_a.create_deep_review(
        EcosystemDeepReview(
            repo_id=profile_a.id,
            status=EcosystemDeepReviewStatus.QUEUED,
        )
    )

    # B 看不到
    a_reviews = await repo_a.list_deep_reviews(limit=100)
    b_reviews = await repo_b.list_deep_reviews(limit=100)
    assert len(a_reviews) == 1
    assert a_reviews[0].project_id == shared_db["project_a_id"]
    assert len(b_reviews) == 0


# ------------------------------------------------------------------
# RepoTag + Relation isolation
# ------------------------------------------------------------------


async def test_repo_tag_isolated(shared_db) -> None:
    global_repo = shared_db["global"]
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    # 全局标签字典（project_id NULL）
    tag = EcosystemTag(
        name="memory_system",
        category=EcosystemTagCategory.CAPABILITY,
        description="long-term memory",
    )
    await global_repo.upsert_tag(tag)

    # 两项目各自有一个仓
    await repo_a.upsert_ecosystem_profile(_make_profile("a-team/repo"))
    await repo_b.upsert_ecosystem_profile(_make_profile("b-team/repo"))
    profile_a = (await repo_a.search_ecosystem_profiles(limit=10))[0]
    profile_b = (await repo_b.search_ecosystem_profiles(limit=10))[0]
    saved_tag = await global_repo.get_tag_by_name("memory_system")
    assert saved_tag is not None

    # 各自打标
    await repo_a.add_repo_tag(
        EcosystemRepoTag(
            repo_id=profile_a.id,
            tag_id=saved_tag.id,
            source=EcosystemTagSource.MANUAL,
        )
    )
    await repo_b.add_repo_tag(
        EcosystemRepoTag(
            repo_id=profile_b.id,
            tag_id=saved_tag.id,
            source=EcosystemTagSource.MANUAL,
        )
    )

    a_rt = await repo_a.list_repo_tags(limit=100)
    b_rt = await repo_b.list_repo_tags(limit=100)
    assert len(a_rt) == 1
    assert len(b_rt) == 1
    assert a_rt[0].project_id == shared_db["project_a_id"]
    assert b_rt[0].project_id == shared_db["project_b_id"]

    # 标签字典保持全局：两个项目都能查到同一标签字典行
    assert (await global_repo.list_tags(limit=10))[0].name == "memory_system"


async def test_relation_isolated(shared_db) -> None:
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    # A 项目两个仓 + 一条关系
    await repo_a.upsert_ecosystem_profile(_make_profile("rel/x"))
    await repo_a.upsert_ecosystem_profile(_make_profile("rel/y"))
    a_profiles = await repo_a.search_ecosystem_profiles(limit=10)
    assert len(a_profiles) == 2
    pa_x = next(p for p in a_profiles if p.repo_full_name == "rel/x")
    pa_y = next(p for p in a_profiles if p.repo_full_name == "rel/y")

    await repo_a.add_relation(
        EcosystemRelation(
            from_repo_id=pa_x.id,
            to_repo_id=pa_y.id,
            relation_type=EcosystemRelationType.INSPIRED_BY,
        )
    )

    a_rels = await repo_a.list_relations(limit=100)
    b_rels = await repo_b.list_relations(limit=100)
    assert len(a_rels) == 1
    assert a_rels[0].project_id == shared_db["project_a_id"]
    assert len(b_rels) == 0


# ------------------------------------------------------------------
# Backfill scenario
# ------------------------------------------------------------------


async def test_backfill_to_project(shared_db) -> None:
    """legacy 行（project_id=NULL）通过 backfill 迁移到指定项目，
    迁移后 repo_a 的 search 能看到，repo_b 看不到。"""
    global_repo = shared_db["global"]
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    # 模拟 legacy 数据：用 global_repo（没有 project_scope）写入 NULL project_id
    legacy_profile = _make_profile("legacy/repo-1")
    legacy_profile.project_id = None  # 显式确保 NULL
    await global_repo.upsert_ecosystem_profile(legacy_profile)

    legacy_run = EcosystemScanRun(strategy=EcosystemScanStrategy.INCREMENTAL)
    await global_repo.create_scan_run(legacy_run)

    # 迁移前 repo_a / repo_b 都看不到
    assert len(await repo_a.search_ecosystem_profiles(limit=100)) == 0
    assert len(await repo_b.search_ecosystem_profiles(limit=100)) == 0

    # backfill 到 project A
    counts = await global_repo.backfill_ecosystem_to_project(
        shared_db["project_a_id"]
    )
    assert counts["ecosystem_repo_profiles"] == 1
    assert counts["ecosystem_scan_runs"] == 1

    # 迁移后 repo_a 看到，repo_b 看不到
    a_after = await repo_a.search_ecosystem_profiles(limit=100)
    b_after = await repo_b.search_ecosystem_profiles(limit=100)
    assert len(a_after) == 1
    assert a_after[0].repo_full_name == "legacy/repo-1"
    assert a_after[0].project_id == shared_db["project_a_id"]
    assert len(b_after) == 0

    # 二次 backfill 幂等：NULL 行已经不存在，无新增
    counts_again = await global_repo.backfill_ecosystem_to_project(
        shared_db["project_a_id"]
    )
    assert all(v == 0 for v in counts_again.values())


async def test_backfill_rejects_unknown_project(shared_db) -> None:
    """不存在的 project_id 应抛异常。"""
    import pytest

    global_repo = shared_db["global"]
    with pytest.raises(ValueError):
        await global_repo.backfill_ecosystem_to_project("not-a-real-id")


# ------------------------------------------------------------------
# Cross-project scope override
# ------------------------------------------------------------------


async def test_search_extended_scoped(shared_db) -> None:
    """search_ecosystem_profiles_extended 也尊重作用域。"""
    repo_a = shared_db["repo_a"]
    repo_b = shared_db["repo_b"]

    await repo_a.upsert_ecosystem_profile(_make_profile("ext/in-a-1"))
    await repo_a.upsert_ecosystem_profile(_make_profile("ext/in-a-2"))
    await repo_b.upsert_ecosystem_profile(_make_profile("ext/in-b"))

    rows_a, total_a = await repo_a.search_ecosystem_profiles_extended(limit=100)
    rows_b, total_b = await repo_b.search_ecosystem_profiles_extended(limit=100)

    assert total_a == 2
    assert total_b == 1
    assert all(r.project_id == shared_db["project_a_id"] for r in rows_a)
    assert rows_b[0].project_id == shared_db["project_b_id"]
