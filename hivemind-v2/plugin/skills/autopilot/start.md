# /autopilot start — 启动 Autopilot

## 输入参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `task_id` | 是 | 要启动 autopilot 的任务 ID |
| `--duration` | 否 | 最大运行时长，如 `4h`、`30m`。不设则无上限 |

示例：`/autopilot start task-abc123 --duration=4h`

## 执行步骤

### Step 1: 验证任务

调用 `task_status(task_id=...)` 确认任务存在且状态为 `running` 或 `pending`。

如果任务不存在或已 `completed` / `cancelled`，中止并告知用户。

### Step 2: 确保 pipeline 已初始化

调用 `GET /api/tasks/{task_id}/pipeline/v2` 检查：

- 如果 `success=True`，pipeline 已存在，记录 `current_stage` 和 `current_stage_class`
- 如果 `success=False`（没有 pipeline），询问用户需要哪种 `task_type`（feature / hotfix / research / quick-fix 等），然后调用 `POST /api/tasks/{task_id}/pipeline/v2` 创建

### Step 3: 启动 autopilot

调用 `POST /api/tasks/{task_id}/pipeline/v2/autopilot`：

```json
{
  "active": true,
  "max_duration_minutes": 240
}
```

（如无 `--duration` 参数，不传 `max_duration_minutes`）

### Step 4: 时长提示

- **已设置时长**：输出"Autopilot 已启动，将在 `{duration}` 后自动停止（或你返回时）"
- **未设置时长**：输出警告：

  > 未设置时长上限，autopilot 将持续运行直到你返回。建议下次启用时加 `--duration=4h` 设硬上限。

### Step 5: 输出启动摘要

```
Autopilot 已启动
- 任务：{task_id} — {task_title}
- 当前阶段：{current_stage}（{current_stage_class} 类）
- 时长上限：{duration 或 "无限制"}
- 退出触发条件：{当前阶段的出口条件描述}
- 返回后发任意消息即可自动停止
```

## 注意事项

- autopilot 期间 pipeline_gate hook 自动限制工具集（Plan 阶段只能读/研究，Execute 阶段才能修改文件）
- 高风险操作会生成 briefing 等你回来批准，不会自动执行
- sub-agent 无法调用 `pipeline_advance(force=True)` 或 `briefing_resolve`，必须由你（Leader）处理
