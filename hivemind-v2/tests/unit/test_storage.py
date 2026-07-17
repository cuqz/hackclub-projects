"""AI Team OS — StorageRepository 单元测试."""

from __future__ import annotations

import pytest

from aiteam.storage.repository import StorageRepository
from aiteam.types import TaskStatus

# ================================================================
# Teams
# ================================================================


async def test_create_and_get_team(db_repository: StorageRepository) -> None:
    """创建团队并通过 ID 和名称获取."""
    team = await db_repository.create_team("alpha", "coordinate", {"env": "test"})
    assert team.name == "alpha"
    assert team.mode.value == "coordinate"
    assert team.config == {"env": "test"}

    # 通过 ID 获取
    by_id = await db_repository.get_team(team.id)
    assert by_id is not None
    assert by_id.id == team.id
    assert by_id.name == "alpha"

    # 通过名称获取
    by_name = await db_repository.get_team_by_name("alpha")
    assert by_name is not None
    assert by_name.id == team.id

    # 不存在的团队返回 None
    assert await db_repository.get_team("nonexistent") is None
    assert await db_repository.get_team_by_name("nonexistent") is None


async def test_list_teams(db_repository: StorageRepository) -> None:
    """列出所有团队."""
    await db_repository.create_team("team-a", "coordinate")
    await db_repository.create_team("team-b", "broadcast")

    teams = await db_repository.list_teams()
    assert len(teams) == 2
    names = {t.name for t in teams}
    assert names == {"team-a", "team-b"}


async def test_update_team(db_repository: StorageRepository) -> None:
    """更新团队信息."""
    team = await db_repository.create_team("updatable", "coordinate")

    updated = await db_repository.update_team(team.id, mode="broadcast")
    assert updated.mode.value == "broadcast"

    # 验证持久化
    fetched = await db_repository.get_team(team.id)
    assert fetched is not None
    assert fetched.mode.value == "broadcast"

    # 更新不存在的团队应抛出异常
    with pytest.raises(ValueError, match="不存在"):
        await db_repository.update_team("nonexistent", mode="route")


async def test_delete_team(db_repository: StorageRepository) -> None:
    """删除团队."""
    team = await db_repository.create_team("deletable", "coordinate")
    assert await db_repository.delete_team(team.id) is True

    # 确认已删除
    assert await db_repository.get_team(team.id) is None

    # 删除不存在的团队返回 False
    assert await db_repository.delete_team("nonexistent") is False


# ================================================================
# Agents
# ================================================================


async def test_create_and_get_agent(db_repository: StorageRepository) -> None:
    """创建 Agent 并获取."""
    team = await db_repository.create_team("dev-team", "coordinate")
    agent = await db_repository.create_agent(
        team.id, "dev-1", "后端开发", system_prompt="你是后端开发工程师"
    )
    assert agent.name == "dev-1"
    assert agent.role == "后端开发"
    assert agent.system_prompt == "你是后端开发工程师"
    assert agent.team_id == team.id

    fetched = await db_repository.get_agent(agent.id)
    assert fetched is not None
    assert fetched.name == "dev-1"

    # 不存在的 Agent 返回 None
    assert await db_repository.get_agent("nonexistent") is None


async def test_list_agents_by_team(db_repository: StorageRepository) -> None:
    """按团队列出 Agent，确保团队隔离."""
    team_a = await db_repository.create_team("team-a", "coordinate")
    team_b = await db_repository.create_team("team-b", "coordinate")

    await db_repository.create_agent(team_a.id, "a1", "开发")
    await db_repository.create_agent(team_a.id, "a2", "测试")
    await db_repository.create_agent(team_b.id, "b1", "设计")

    agents_a = await db_repository.list_agents(team_a.id)
    assert len(agents_a) == 2
    assert {a.name for a in agents_a} == {"a1", "a2"}

    agents_b = await db_repository.list_agents(team_b.id)
    assert len(agents_b) == 1
    assert agents_b[0].name == "b1"


# ================================================================
# Tasks
# ================================================================


async def test_create_and_get_task(db_repository: StorageRepository) -> None:
    """创建任务并获取."""
    team = await db_repository.create_team("task-team", "coordinate")
    task = await db_repository.create_task(team.id, "实现登录", "实现用户登录功能")
    assert task.title == "实现登录"
    assert task.description == "实现用户登录功能"
    assert task.status == TaskStatus.PENDING

    fetched = await db_repository.get_task(task.id)
    assert fetched is not None
    assert fetched.title == "实现登录"

    # 不存在的任务返回 None
    assert await db_repository.get_task("nonexistent") is None


async def test_list_tasks_filter_status(db_repository: StorageRepository) -> None:
    """列出任务并按状态过滤."""
    team = await db_repository.create_team("filter-team", "coordinate")

    task1 = await db_repository.create_task(team.id, "任务1")
    task2 = await db_repository.create_task(team.id, "任务2")
    task3 = await db_repository.create_task(team.id, "任务3")

    # 将 task2 标记为 running
    await db_repository.update_task(task2.id, status="running")
    # 将 task3 标记为 completed
    await db_repository.update_task(task3.id, status="completed")

    # 不过滤 — 全部返回
    all_tasks = await db_repository.list_tasks(team.id)
    assert len(all_tasks) == 3

    # 按状态过滤
    pending = await db_repository.list_tasks(team.id, status=TaskStatus.PENDING)
    assert len(pending) == 1
    assert pending[0].id == task1.id

    running = await db_repository.list_tasks(team.id, status=TaskStatus.RUNNING)
    assert len(running) == 1
    assert running[0].id == task2.id

    completed = await db_repository.list_tasks(team.id, status=TaskStatus.COMPLETED)
    assert len(completed) == 1
    assert completed[0].id == task3.id


# ================================================================
# Events
# ================================================================


async def test_create_and_list_events(db_repository: StorageRepository) -> None:
    """创建事件并按条件列出."""
    await db_repository.create_event("team.created", "system", {"team": "alpha"})
    await db_repository.create_event("agent.created", "system", {"agent": "dev-1"})
    await db_repository.create_event("team.created", "cli", {"team": "beta"})

    # 全部列出
    all_events = await db_repository.list_events()
    assert len(all_events) == 3

    # 按类型过滤
    team_events = await db_repository.list_events(event_type="team.created")
    assert len(team_events) == 2

    # 按来源过滤
    cli_events = await db_repository.list_events(source="cli")
    assert len(cli_events) == 1
    assert cli_events[0].data["team"] == "beta"

    # 同时按类型和来源过滤
    filtered = await db_repository.list_events(event_type="team.created", source="system")
    assert len(filtered) == 1

    # 限制数量
    limited = await db_repository.list_events(limit=1)
    assert len(limited) == 1


# ================================================================
# Memories
# ================================================================


async def test_create_and_search_memories(db_repository: StorageRepository) -> None:
    """创建记忆并搜索."""
    team = await db_repository.create_team("mem-team", "coordinate")

    m1 = await db_repository.create_memory(
        "team", team.id, "项目使用Python和FastAPI开发", {"tag": "tech"}
    )
    await db_repository.create_memory(
        "team", team.id, "团队成员包括3名后端和2名前端", {"tag": "org"}
    )
    await db_repository.create_memory("agent", "agent-001", "该Agent擅长数据分析")

    # 获取单条记忆
    fetched = await db_repository.get_memory(m1.id)
    assert fetched is not None
    assert fetched.content == "项目使用Python和FastAPI开发"
    assert fetched.metadata == {"tag": "tech"}

    # 列出指定作用域的记忆
    team_mems = await db_repository.list_memories("team", team.id)
    assert len(team_mems) == 2

    agent_mems = await db_repository.list_memories("agent", "agent-001")
    assert len(agent_mems) == 1

    # 关键词搜索
    python_results = await db_repository.search_memories("team", team.id, "Python")
    assert len(python_results) == 1
    assert "Python" in python_results[0].content

    # 搜索不到的关键词
    empty = await db_repository.search_memories("team", team.id, "Java")
    assert len(empty) == 0

    # 跨作用域不会搜到
    cross_scope = await db_repository.search_memories("agent", "agent-001", "Python")
    assert len(cross_scope) == 0

    # 删除记忆
    assert await db_repository.delete_memory(m1.id) is True
    assert await db_repository.get_memory(m1.id) is None
    assert await db_repository.delete_memory("nonexistent") is False
