---
name: autopilot
description: 让 OS 在用户离开期间自主推进任务。支持三个子命令：start（启动）、stop（停止）、status（状态查询）。
---

# /autopilot — 自动驾驶技能

本技能让 OS 在你离开期间以 **autopilot 模式**自主推进指定任务的 pipeline 阶段。

## 何时使用

- 你需要离开一段时间，但希望 OS 继续处理耗时任务（如 implement → test → review 阶段）
- 你信任当前任务范围，允许 OS 自主调用工具修改文件、运行测试
- 任务已有活跃 pipeline（已执行 `pipeline_create`）

## 子命令速览

| 命令 | 说明 |
|------|------|
| `/autopilot start <task_id> [--duration=4h]` | 启动 autopilot | 
| `/autopilot stop` | 手动停止（所有活跃任务） |
| `/autopilot status <task_id>` | 查询当前状态 |

详细步骤见：
- [start.md](start.md) — 启动流程和参数
- [stop.md](stop.md) — 停止流程和总结生成
- [status.md](status.md) — 状态读取格式

## 风险提示

**重要**：autopilot 期间 OS 会自主调用工具修改文件、运行命令。仅在你信任当前任务范围时启用。

OS 会根据当前 pipeline 阶段（Plan / Execute / Verify）限制可用工具集，高风险操作（如 `git_auto_commit`、`team_delete`）会自动生成 briefing 等待你回来批准。

## 退出方式

1. **自动退出**：你发送任意消息时，`autopilot_auto_stop` hook 自动检测并停止所有 autopilot 任务
2. **手动退出**：显式执行 `/autopilot stop`

## 快速示例

```
/autopilot start task-abc123 --duration=2h
# 离开去做别的事...
# 回来后 OS 自动停止 autopilot 并生成总结
/autopilot status task-abc123  # 查看这期间的进展
```
