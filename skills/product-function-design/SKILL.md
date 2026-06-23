---
name: product-function-design
description: Turn a clarified requirements document into a complete product function design PRD. Use when the user has a BRD or requirement clarification document with background, user needs, goals, flows, states, and source assumptions, and asks Codex to design product features, interactions, data fields, business rules, permissions, metrics, or save a PRD under docs/requirement/prd.
---

# Product Function Design

## Overview

Use this skill to transform a requirement clarification document into a product function design plan. The input normally comes from a BRD or requirements clarification skill and includes requirement background, users and needs, goals and non-goals, key flows, state transitions, and source assumptions.

The output is a Chinese PRD saved to `docs/requirement/prd/YYYY-MM-DD-<topic>-prd.md`, followed by a request for the user to review the overall product function design.

## Input Contract

Expect the source requirement document to include these sections.

Required:
- 需求背景: 业务背景, 触发场景, 现有问题与影响
- 用户与核心诉求: 用户角色, 用户任务, 核心诉求/期望结果, 痛点
- 关键流程: 主流程, 分支流程, 异常流程, 状态流转

Optional but valuable:
- 目标与非目标: 成功指标, 约束, 非目标, 取舍原则/诉求排序
- 原始输入依据: 用户原话, 已知项目上下文, 明确假设

If the user provides only a file path, read that file. If the user provides pasted content, use it as the requirement source. If multiple possible source documents exist, choose the most recent relevant BRD or ask one concise question.

## Workflow

### 1. Understand Project Context

Before designing product functionality, inspect the current project context.

1. Use `rg --files` from the workspace root.
2. Read only relevant artifacts, such as `README`, `docs/`, existing BRDs, PRDs, specs, route files, data schemas, package metadata, or product notes.
3. Summarize the context that affects product design: existing product surface, domain objects, terminology, workflows, constraints, and adjacent features.
4. If there is no useful project context, state that briefly and proceed from the requirement document.

Do not invent project facts. Mark unconfirmed assumptions explicitly.

### 2. Parse Requirement Source

Extract and normalize the requirement facts into this working model:

- Background: business context, trigger, current problem, impact
- Users: roles, tasks, desired outcomes, pain points
- Goals: success metrics, constraints, non-goals, tradeoff priorities
- Flow: main path, branch paths, exceptions, state transitions
- Evidence: original user words, project context, explicit assumptions

Preserve source meaning. If the requirement document contains solution ideas, translate them into underlying user needs, rules, or constraints before using them in the design.

### 3. Check Design Readiness

Before writing the PRD, verify that the following are clear enough to design responsibly:

- Target user roles and permission boundaries
- User tasks and priority order
- Main workflow and at least likely branches
- Exception handling and failure cases
- State transitions and allowed operations per state
- Business rules and decision criteria
- Data sources or at least assumptions about data origin
- MVP scope, non-goals, and tradeoff principles
- Success metrics or proxy indicators

If a critical item is missing, ask exactly one question at a time. Prefer multiple-choice questions with 2-4 options and an "other" escape hatch.

Example:

```text
为了确定本期 PRD 的范围，我需要先确认版本边界。你希望这次方案优先覆盖哪一类能力？
A. 只覆盖主流程闭环，先保证用户能完成核心任务
B. 覆盖主流程 + 常见分支，适合进入研发评审
C. 覆盖主流程 + 分支 + 异常 + 权限 + 埋点，作为完整 PRD
D. 其他：请用一句话说明范围
```

Ask the highest-impact missing question first. After the user answers, update the working understanding and reassess. Continue until the design can be grounded rather than guessed.

### 4. Derive Product Design

Use the requirement facts to derive the PRD through these transformations:

- 需求背景 and 问题影响 -> 产品目标, 版本目标, 成功指标
- 用户角色 and 用户任务 -> 用户场景, 任务清单, 功能模块
- 核心诉求 and 痛点 -> 功能价值, 优先级, 关键体验原则
- 主流程 and 分支流程 -> 页面流转, 操作路径, 功能需求
- 异常流程 -> 空状态, 错误提示, 兜底策略, 补偿流程
- 状态流转 -> 状态机, 可执行操作, 权限规则, 后置结果
- 约束 and 非目标 -> MVP 范围, 不做事项, 取舍原则
- 成功指标 -> 埋点, 漏斗, 数据看板或验收指标
- 原始输入依据 and 假设 -> 待确认项, 风险, 方案依据

Design from user tasks and business rules first, then page interactions and data fields. Avoid starting from a feature list without explaining why each feature exists.

### 5. Write the PRD File

Create or update `docs/requirement/prd/YYYY-MM-DD-<topic>-prd.md`. Use the current date for `YYYY-MM-DD`. Use a short lowercase or pinyin topic slug when no naming convention exists.

Read `references/prd-template.md` before writing the PRD and follow its output structure. Omit sections only when they are genuinely irrelevant. If information is unknown but important, keep it under `待确认问题` rather than silently filling it in.

### Writing Standards

- Make every feature traceable to a user task, pain point, flow, rule, or metric.
- Separate requirement facts from design assumptions.
- Define behavior by state and role when operations differ across statuses or users.
- Include empty states, loading states, error states, duplicate submission, permission denial, and data conflict handling when relevant.
- Keep data fields tied to user decisions, system rules, state changes, or analytics needs.
- Use tables for priority, state transitions, page lists, fields, permissions, and metrics when it improves scanability.
- Avoid low-confidence implementation details unless the project context requires them.

## Self Review

Before telling the user the PRD is ready, review and update the file against this checklist:

- The PRD is grounded in the requirement document and project context.
- Product goals connect to the original business problem and impact.
- Features map to user roles, tasks, pain points, and flows.
- Main, branch, exception, and state flows are represented.
- Business rules and permissions are explicit enough for engineering discussion.
- Data fields include source, meaning, validation, or update rule where relevant.
- Unknowns are listed as assumptions or待确认项, not hidden inside confident prose.
- The file is saved under `docs/requirement/prd/YYYY-MM-DD-<topic>-prd.md`.

## Final Response

End by asking the user to review the product function design as a whole. Include:

- The PRD file path
- A short summary of what was designed
- A direct review request, for example: "请你整体审查这份产品功能设计方案，重点看范围、流程、业务规则、字段和待确认项是否符合你的预期。"
