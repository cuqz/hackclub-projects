---
template_name: council
description: Council review — multi-perspective expert evaluation of proposals or architectures
total_rounds: 3
rounds:
  - number: 1
    name: "Expert perspectives"
    rule: "Each participant evaluates from their professional angle (security, performance, maintainability, UX, cost, etc.). Format: [Perspective] + [Strengths] + [Risks] + [Score 1-5]"
  - number: 2
    name: "Cross-examination"
    rule: "Challenge the highest-risk items from Round 1. Propose mitigations or alternatives. Format: [Risk addressed] + [Mitigation proposal] + [Revised score]"
  - number: 3
    name: "Verdict"
    rule: "Each expert gives final verdict: APPROVE / CONDITIONAL / REJECT. Decision requires majority APPROVE. Output: [Verdict] + [Conditions if any] + [Action items]"
keywords: [council, 评审委员会, 多角度, multi-perspective, 专家评审, 架构评审, 方案评估]
---

# Council 专家委员会评审模板

## 何时使用

- 重大架构决策需要多个专业视角的系统性评审
- 方案涉及安全、性能、成本等多个维度，单一评审者视角不足
- 需要形成正式评审结论（APPROVE/CONDITIONAL/REJECT）
- 项目里程碑评审，确保关键决策经过多方专家背书

**不适合**：日常代码 PR（用 review 模板即可）；需要创意发散的场景（用 brainstorm）；已明确结论只需执行的场景。

## 参与者建议

- 每位参与者代表一个专业视角（安全、性能、可维护性、UX、成本等）
- 建议 3～6 位专家，确保视角多元但不过于冗长
- 方案提出者可作为观察者，在评审结束后回应问题
- 主持人负责汇总各轮评分，确保 Round 3 产出明确结论

## 反模式

- 参与者视角重叠，多人从同一角度评审（降低多角度价值）
- Round 1 评分没有理由支撑，只有数字
- 跳过 Round 2，直接从 Round 1 进入裁决（遗漏重要风险的交叉验证）
- 裁决需要"全票通过"导致无法收敛（应采用多数通过原则）
- 方案提出者在 Round 1/2 介入为自己辩护（影响独立评审）
