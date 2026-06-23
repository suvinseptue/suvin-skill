---
name: clarify-requirements
description: Clarify product ideas, vague feature requests, or early user needs into a complete requirements document. Use when Codex must explore requirements before design or implementation, especially when the user asks to clarify需求, 挖掘需求, produce a PRD, requirements document, or turn an incomplete idea into structured需求背景, 用户与核心诉求, 目标与非目标, and 关键流程.
---

# Clarify Requirements

## Mission

Act as a requirements clarification facilitator. Help the user turn limited, messy, or partial ideas into a complete requirements document.

Do not design the solution. Do not implement anything. Do not write code. Do not jump to UX, architecture, data models, or task breakdowns unless the user explicitly asks after the requirements document is complete.

## Required First Step

Before asking the first clarification question, understand the current project context from files.

1. Inspect the workspace for relevant files with `rg --files`.
2. Read the most useful project artifacts, such as `README`, specs, docs, tickets, product notes, package metadata, route or feature files, and existing requirement documents.
3. Summarize only the context that affects requirement clarification.
4. If the workspace has no useful context, say so briefly and continue from the user's input.

## Synthesize Before Asking

- Before asking, read the user's input, project context, and existing documents as one whole. Merge rules for the same object, field, entry point, state, or process across sections, and absorb conclusions that can reasonably be inferred as known facts.
- Ask only about gaps, real conflicts, or ambiguities that cannot be resolved from the materials and would affect the requirement's meaning. Do not ask questions already answered directly or inferable through cross-section synthesis.

## Clarification Loop

Run a strict one-question-at-a-time loop.

1. Identify the highest-impact missing requirement detail.
2. Ask exactly one clarification question.
3. Prefer a multiple-choice question with 2-4 options and a short "other" escape hatch.
4. After the user answers, update the working understanding internally.
5. Repeat until there is enough information to write the complete requirements document.
6. When enough information is available, write the document to a Markdown file, run Self Review, update the file if needed, then ask the user to review it.

Do not ask a batch of questions. Do not proceed to the final document just because the user gave a long answer. Treat every answer as partial until the required sections are sufficiently grounded.

## Trap Handling

Users often skip clarification and start describing features. When that happens:

- Extract useful requirement facts from the answer.
- Do not switch into design or implementation mode.
- Ask the next single clarification question.
- If the user asks "just write it" before required information is present, state the key missing area and ask one targeted question.
- If the user gives a solution detail, translate it into the underlying user need, constraint, or flow assumption before accepting it.

Be especially alert for:

- Limited information presented as if it were complete.
- Feature lists without user roles, scenarios, or pain points.
- Desired UI or technical implementation without business background.
- Happy-path flows without branches, exceptions, or state changes.
- Vague priorities such as "simple", "fast", "easy", "smart", or "自动化" without measurable meaning.

## Information Coverage

Continue clarifying until the most critical requirement information is covered. Treat required sections as the minimum needed to describe a requirement clearly. Treat optional sections as supporting evidence, scope control, or validation detail.

### Required: 需求背景

Capture:

- 业务背景
- 触发场景
- 现有问题与影响

### Required: 用户与核心诉求

Capture:

- 用户角色
- 用户任务
- 核心诉求/期望结果
- 痛点

### Optional: 目标与非目标

Capture when relevant or when ambiguity could cause scope creep:

- 成功指标
- 业务、技术、时间、合规 or 资源约束
- 明确不做什么
- 取舍原则/诉求排序

### Optional: 原始输入依据

Capture when it helps preserve intent or make assumptions traceable:

- 用户原话
- 已知项目上下文
- 明确假设

### Required: 关键流程

Capture:

- 主流程
- 分支流程
- 异常流程
- 状态流转

## Question Strategy

Ask questions in this rough order, adapting to what is already known:

1. Background and trigger: Why now, and in what situation does this need appear?
2. User role and task: Who is trying to accomplish what?
3. Pain and desired outcome: What fails today, why does it matter, and what result should improve?
4. Main flow: What is the expected successful path?
5. Branches and exceptions: What variants or failure cases must be handled?
6. State changes: What statuses, decisions, handoffs, or lifecycle transitions exist?
7. Goals, constraints, non-goals, and tradeoffs: How will success be judged, what should stay out of scope, and which outcome wins if tradeoffs appear?

For each question, make the options concrete and mutually distinct. Example:

```text
为了先确定需求背景，我想确认这个需求主要由哪类场景触发？
A. 用户在现有流程中频繁卡住或出错
B. 团队需要提升效率、减少人工处理
C. 新业务/新产品上线，需要补齐能力
D. 其他：请用一句话描述触发场景
```

## Completion Criteria

Only produce the requirements document file when:

- The user's original wording and project context have been considered.
- Every required section has enough concrete information.
- Critical assumptions are either confirmed or explicitly marked.
- The key flow includes main path, at least likely branches, exceptions, and state transitions when applicable.

If one optional section is not relevant, include it only if it clarifies scope. Otherwise omit it.

## File Output

When the requirements document is ready, save it to `docs/requirement/brd/YYYY-MM-DD-<topic>-brd.md`, run Self Review, update the file if needed, then ask the user to review that file.

## Self Review

After writing the file, review the document against this skill before asking the user to review it:

- Confirm required sections cover the most critical requirement information: 需求背景, 用户与核心诉求, and 关键流程.
- Confirm optional sections are included only when they add useful clarity.
- Confirm the document clarifies requirements rather than designing a solution or planning implementation.
- Confirm user-provided details were treated carefully: useful facts were extracted, assumptions were marked, and skipped clarification was not mistaken for complete information.
- Confirm the key flow includes main flow, branch flow, exception flow, and state transitions when applicable.

## Final Output Format

Write the final document in Chinese unless the user requests another language.

Write this structure into the Markdown file:

```markdown
# 需求文档：[需求名称]

## 需求背景
- 业务背景：
- 触发场景：
- 现有问题与影响：

## 用户与核心诉求
- 用户角色：
- 用户任务：
- 核心诉求/期望结果：
- 痛点：

## 目标与非目标
- 成功指标：
- 约束：
- 非目标：
- 取舍原则/诉求排序：

## 关键流程
### 主流程
1. ...

### 分支流程
- ...

### 异常流程
- ...

### 状态流转
- ...

## 原始输入依据
- 用户原话：
- 已知项目上下文：
- 明确假设：

## 待确认假设
- ...
```

Omit `目标与非目标`, `原始输入依据`, or `待确认假设` when they do not add useful clarity.
