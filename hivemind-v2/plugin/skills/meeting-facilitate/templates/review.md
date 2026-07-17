---
template_name: review
description: 评审会议——评估交付物质量，发现问题并提出改进建议
total_rounds: 3
rounds:
  - number: 1
    name: "方案陈述"
    rule: "汇报人展示交付物，评审者只听不评（可提澄清问题）。发言格式：[概述] + [核心设计] + [已知局限] + [期望反馈]"
  - number: 2
    name: "独立评审"
    rule: "评审者独立发言，不互相参考。问题分级：Critical/Major/Minor/Suggestion，每个问题附带改进建议。发言格式：[总体评价] + 各级问题列表"
  - number: 3
    name: "回应裁定"
    rule: "汇报人对每个问题回应（接受/部分接受/不接受+理由）。裁定结果：APPROVED / CONDITIONALLY_APPROVED / REVISION_REQUIRED"
keywords: [review, 评审, code review, PR, 验收, 审查, quality]
---

# Review 评审模板

## 何时使用

- 代码 PR 评审，需要多人从不同维度检查质量
- 设计文档、架构方案的正式审查
- 交付物验收前的质量把关
- 需要结构化反馈（而非随意讨论）的场景

**不适合**：探索性讨论或方案选择场景，那更适合 brainstorm 或 decision 模板。

## 参与者建议

- 1 位汇报人（交付物作者，负责陈述和回应）
- 2～4 位评审者（与交付物相关领域的专家）
- 评审者在 Round 2 需独立发言，避免互相影响
- 主持人确保评审粒度合理（不过于挑剔细节，也不流于表面）

## 反模式

- Round 1 评审者抢先评论（应先让汇报人完整陈述）
- Round 2 评审者之间互相参考，导致意见同质化
- 问题没有分级，Critical 和 Suggestion 混在一起
- 汇报人在 Round 3 逐条争辩而非结构化回应
- 评审结果模糊，没有明确的 APPROVED/REVISION_REQUIRED 裁定
