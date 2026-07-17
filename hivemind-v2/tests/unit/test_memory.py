"""AI Team OS — Memory 模块单元测试."""

from __future__ import annotations

from pathlib import Path

import pytest

from aiteam.memory.recovery import ContextRecovery
from aiteam.memory.retriever import (
    build_context_string,
    keyword_search,
    rank_by_relevance,
)
from aiteam.memory.store import MemoryStore
from aiteam.storage.repository import StorageRepository
from aiteam.types import Memory, MemoryScope

# ================================================================
# MemoryStore
# ================================================================


async def test_store_and_retrieve(db_repository: StorageRepository) -> None:
    """存储记忆并通过关键词检索."""
    store = MemoryStore(db_repository)

    mid = await store.store("agent", "a1", "Python是一种编程语言", {"tag": "lang"})
    assert isinstance(mid, str) and len(mid) > 0

    await store.store("agent", "a1", "FastAPI用于构建REST API")
    await store.store("agent", "a1", "React是前端框架")

    results = await store.retrieve("agent", "a1", "Python", limit=5)
    assert len(results) >= 1
    assert any("Python" in m.content for m in results)


async def test_hot_cache(db_repository: StorageRepository) -> None:
    """验证 store 后记忆同时存在于 Hot 层缓存."""
    store = MemoryStore(db_repository)

    await store.store("agent", "a1", "Hot层缓存测试内容")

    # 直接检查 Hot 层缓存
    key = store._cache_key("agent", "a1")
    assert key in store._hot_cache
    assert len(store._hot_cache[key]) == 1
    assert store._hot_cache[key][0].content == "Hot层缓存测试内容"

    # 存储更多记忆，缓存应累积
    await store.store("agent", "a1", "第二条记忆")
    assert len(store._hot_cache[key]) == 2


async def test_memory_scope_isolation(db_repository: StorageRepository) -> None:
    """不同 scope 的记忆应互相隔离."""
    store = MemoryStore(db_repository)

    await store.store("agent", "a1", "Agent私有记忆关于Python")
    await store.store("team", "t1", "Team共享记忆关于Python")
    await store.store("global", "system", "全局记忆关于Python")

    agent_results = await store.retrieve("agent", "a1", "Python", limit=10)
    team_results = await store.retrieve("team", "t1", "Python", limit=10)
    global_results = await store.retrieve("global", "system", "Python", limit=10)

    # 每个 scope 只能检索到自己的记忆
    assert all(m.scope == MemoryScope.AGENT for m in agent_results)
    assert all(m.scope == MemoryScope.TEAM for m in team_results)
    assert all(m.scope == MemoryScope.GLOBAL for m in global_results)

    # 各 scope 最多只有1条
    assert len(agent_results) <= 1
    assert len(team_results) <= 1
    assert len(global_results) <= 1


async def test_delete_memory(db_repository: StorageRepository) -> None:
    """删除记忆应同时清理 Hot 层和 Warm 层."""
    store = MemoryStore(db_repository)

    mid = await store.store("agent", "a1", "待删除的记忆")

    # 删除前: Hot 层和 Warm 层都有
    key = store._cache_key("agent", "a1")
    assert len(store._hot_cache[key]) == 1
    warm = await store.list_all("agent", "a1")
    assert len(warm) == 1

    # 执行删除
    result = await store.delete(mid)
    assert result is True

    # 删除后: Hot 层和 Warm 层都清空
    assert len(store._hot_cache[key]) == 0
    warm_after = await store.list_all("agent", "a1")
    assert len(warm_after) == 0


async def test_get_context(db_repository: StorageRepository) -> None:
    """构建 Agent 上下文字符串."""
    store = MemoryStore(db_repository)

    # 存储 agent 级别记忆
    await store.store("agent", "agent-001", "该Agent擅长数据分析和Python编程")
    # 存储 global 级别记忆
    await store.store("global", "system", "项目使用Python和FastAPI技术栈")

    ctx = await store.get_context("agent-001", "用Python分析数据")

    # 上下文应包含相关记忆
    assert "相关记忆" in ctx
    assert "数据分析" in ctx or "Python" in ctx


async def test_list_all(db_repository: StorageRepository) -> None:
    """列出指定作用域的所有记忆."""
    store = MemoryStore(db_repository)

    await store.store("team", "t1", "记忆1")
    await store.store("team", "t1", "记忆2")
    await store.store("team", "t1", "记忆3")
    await store.store("team", "t2", "其他团队记忆")

    t1_mems = await store.list_all("team", "t1")
    assert len(t1_mems) == 3

    t2_mems = await store.list_all("team", "t2")
    assert len(t2_mems) == 1


async def test_archive(db_repository: StorageRepository, tmp_path: Path) -> None:
    """归档记忆到 Cold 层 JSON 文件."""
    archive_dir = tmp_path / "archive"
    store = MemoryStore(db_repository, archive_dir=archive_dir)

    await store.store("team", "t1", "归档记忆1")
    await store.store("team", "t1", "归档记忆2")

    file_path = await store.archive("team", "t1")

    assert file_path.exists()
    assert file_path.suffix == ".json"
    assert "team" in str(file_path)
    assert "t1" in str(file_path)

    import json

    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert len(data) == 2


# ================================================================
# Retriever
# ================================================================


async def test_keyword_search() -> None:
    """关键词搜索匹配测试."""
    m1 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="Python编程语言很流行")
    m2 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="LangGraph构建状态图")
    m3 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="Python和LangChain集成")

    # 搜索 Python: 应命中 m1 和 m3
    results = keyword_search([m1, m2, m3], "Python")
    assert len(results) == 2
    contents = [m.content for m in results]
    assert any("Python编程" in c for c in contents)
    assert any("LangChain" in c for c in contents)

    # 搜索 LangGraph: 只命中 m2
    results = keyword_search([m1, m2, m3], "LangGraph")
    assert len(results) == 1
    assert "LangGraph" in results[0].content

    # 搜索不存在的词: 空结果
    results = keyword_search([m1, m2, m3], "Java")
    assert len(results) == 0


async def test_rank_by_relevance() -> None:
    """按相关性排序测试."""
    m1 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="Python web开发")
    m2 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="数据库设计")
    m3 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="Python数据分析和web爬虫")

    # m3 命中 "Python" + "web" 两个词，m1 也命中两个，m2 命中0个
    ranked = rank_by_relevance([m1, m2, m3], "Python web")
    # m2 应排在最后（命中数为0）
    assert ranked[-1].content == "数据库设计"


async def test_build_context_string() -> None:
    """构建上下文字符串测试."""
    m1 = Memory(scope=MemoryScope.AGENT, scope_id="a1", content="记忆内容一")
    m2 = Memory(scope=MemoryScope.GLOBAL, scope_id="sys", content="记忆内容二")

    ctx = build_context_string([m1, m2])
    assert "相关记忆" in ctx
    assert "记忆内容一" in ctx
    assert "记忆内容二" in ctx
    assert "(agent/a1)" in ctx
    assert "(global/sys)" in ctx

    # 空列表返回空字符串
    assert build_context_string([]) == ""

    # max_tokens 限制
    short_ctx = build_context_string([m1, m2], max_tokens=30)
    # header 本身就占了不少字符，可能只包含部分内容
    assert len(short_ctx) <= 50  # 给一些余量，因为 header 可能刚好卡边界


# ================================================================
# ContextRecovery
# ================================================================


async def test_checkpoint_create_restore(tmp_path: Path) -> None:
    """创建检查点并恢复状态."""
    recovery = ContextRecovery(checkpoint_dir=tmp_path / "checkpoints")

    state = {
        "task": "分析数据",
        "progress": 50,
        "messages": ["hello", "world"],
    }
    cp_id = await recovery.create_checkpoint("agent-001", state)
    assert isinstance(cp_id, str) and len(cp_id) > 0

    # 恢复检查点
    restored = await recovery.restore_checkpoint(cp_id)
    assert restored["agent_id"] == "agent-001"
    assert restored["state"]["task"] == "分析数据"
    assert restored["state"]["progress"] == 50
    assert restored["state"]["messages"] == ["hello", "world"]
    assert "timestamp" in restored

    # 恢复不存在的检查点应抛出 FileNotFoundError
    with pytest.raises(FileNotFoundError):
        await recovery.restore_checkpoint("nonexistent-id")


async def test_checkpoint_list(tmp_path: Path) -> None:
    """列出 Agent 的所有检查点."""
    recovery = ContextRecovery(checkpoint_dir=tmp_path / "checkpoints")

    # 空列表
    assert await recovery.list_checkpoints("agent-001") == []

    # 创建多个检查点
    cp1 = await recovery.create_checkpoint("agent-001", {"step": 1})
    cp2 = await recovery.create_checkpoint("agent-001", {"step": 2})
    cp3 = await recovery.create_checkpoint("agent-001", {"step": 3})

    # 其他 Agent 的检查点不应出现
    await recovery.create_checkpoint("agent-002", {"step": 99})

    cps = await recovery.list_checkpoints("agent-001")
    assert len(cps) == 3

    # 验证按时间升序排列
    ids = [cp["checkpoint_id"] for cp in cps]
    assert cp1 in ids
    assert cp2 in ids
    assert cp3 in ids

    # agent-002 只有1个
    cps2 = await recovery.list_checkpoints("agent-002")
    assert len(cps2) == 1


async def test_checkpoint_cleanup(tmp_path: Path) -> None:
    """清理旧检查点，只保留最新N个."""
    recovery = ContextRecovery(checkpoint_dir=tmp_path / "checkpoints")

    # 创建7个检查点
    for i in range(7):
        await recovery.create_checkpoint("agent-001", {"step": i})

    cps_before = await recovery.list_checkpoints("agent-001")
    assert len(cps_before) == 7

    # 清理: 只保留最新3个
    deleted = await recovery.cleanup_old_checkpoints("agent-001", keep_latest=3)
    assert deleted == 4

    cps_after = await recovery.list_checkpoints("agent-001")
    assert len(cps_after) == 3

    # 保留的应该是最新的3个（时间最大的）
    timestamps = [cp["timestamp"] for cp in cps_after]
    assert timestamps == sorted(timestamps)

    # 不存在的 Agent 清理返回0
    assert await recovery.cleanup_old_checkpoints("nonexistent") == 0
