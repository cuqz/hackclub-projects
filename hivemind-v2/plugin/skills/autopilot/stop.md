# /autopilot stop — 停止 Autopilot

## 触发方式

1. **手动**：用户执行 `/autopilot stop`
2. **自动**：用户发送任意消息时，`autopilot_auto_stop` hook 自动触发

## 执行步骤

### Step 1: 停止所有 autopilot 任务

对每个 `autopilot_active=True` 的任务，调用 `POST /api/tasks/{task_id}/pipeline/v2/autopilot`：

```json
{
  "active": false
}
```

（不传 `max_duration_minutes`，保留已有的值用于历史记录）

### Step 2: 读取阶段历史

调用 `GET /api/tasks/{task_id}/pipeline/v2` 获取：
- `recent_history`（最近 stage 转换记录）
- `autopilot_started_at`（启动时间）
- `current_stage`（当前所处阶段）

### Step 3: 生成 autopilot 总结

计算本次 autopilot 运行期间的信息：

```
Autopilot 已停止 — {task_id}
- 运行时长：{now - autopilot_started_at}
- 经过阶段：{从 history 中提取的 from_stage → to_stage 列表}
- 当前阶段：{current_stage}
- 产出物：{如有 task_memo 可列出关键产出}
```

### Step 4: 写入 task_memo

调用 `task_memo_add`：

```
task_memo_add(
    task_id=task_id,
    content="Autopilot 总结：运行 {duration}，经过阶段 {stages}，当前停在 {current_stage}。",
    memo_type="summary",
)
```

### Step 5: 输出给用户

将 Step 3 生成的总结输出给用户，方便了解 autopilot 期间的进展。

## 多任务场景

如果同时有多个 autopilot 任务，依次对每个任务执行上述步骤，分别输出各任务的总结。
