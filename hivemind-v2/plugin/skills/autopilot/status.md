# /autopilot status — 查询 Autopilot 状态

## 输入参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `task_id` | 是 | 要查询的任务 ID |

示例：`/autopilot status task-abc123`

## 执行步骤

### Step 1: 读取 pipeline 状态

调用 `GET /api/tasks/{task_id}/pipeline/v2`，获取：
- `autopilot_active`：是否正在运行
- `current_stage` / `current_stage_class`
- `stage_started_at`：当前阶段开始时间
- `recent_history`：最近 5 次 stage 转换
- `template`：pipeline 模板类型

同时从 `task.config.pipeline` 中读取：
- `autopilot_started_at`：autopilot 启动时间
- `autopilot_max_duration_minutes`：最大时长（可能为空）

### Step 2: 计算时间信息

- **已运行时长** = `now - autopilot_started_at`（如果 `autopilot_active=True`）
- **剩余时长** = `autopilot_max_duration_minutes - 已运行分钟数`（如果有上限）
- **当前阶段已运行** = `now - stage_started_at`

### Step 3: 输出状态

```
Autopilot 状态 — {task_id}
- 状态：{"运行中" if autopilot_active else "已停止"}
- 当前阶段：{current_stage}（{current_stage_class} 类）
- 当前阶段已运行：{stage_duration}
- 总运行时长：{total_duration} {/ 上限 {max_duration} if max_duration}
- 剩余时长：{remaining 或 "无限制"}

最近 5 次阶段转换：
{history 列表，格式："{from_stage} → {to_stage}（{triggered_by}，{transitioned_at}）"}

待自动 advance 的出口条件：
{根据 current_stage 描述当前评估器判断条件}
```

### 出口条件说明（按阶段）

| 阶段 | 自动 advance 触发条件 |
|------|----------------------|
| `implement` | 任意 `Edit`/`Write` 修改了 `src/` 下的 `.py` 文件（mtime > stage_started_at） |
| `test` / `retest` | Bash 输出包含通过信号（"passed"、"OK"、"✓"）→ advance；包含失败信号 → 回退到 fix |
| 其他阶段 | 暂无自动规则，需手动 `pipeline_advance` |
