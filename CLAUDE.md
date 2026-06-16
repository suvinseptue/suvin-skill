# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code skill repository** containing skill definitions and supporting tooling for the `suvin-skill` skill pack. Skills are Markdown files with YAML frontmatter that define when and how Claude should behave in specific contexts.

## Repository Structure

- **`skills/`** — Skill definitions consumed by Claude Code's skill system
  - `skills/suvin-brain-storm/` — Requirements elicitation skill (Chinese: 需求追问框架)
  - `skills/suvin-long-writer/` — Long-form WeChat article writing skill
  - `skills/suvin-short-writer/` — Short-form content writing skill
  - `skills/erp-trading-design-expert/` — ERP design expert for container and commodity trading companies
- **`.agents/skills/`** — Third-party installed skills (baoyu-* image/content generation skills)
- **`skills-lock.json`** — Lock file for installed third-party skills
- **`docs/references/`** — Reference documentation and implementation details for skills
  - `docs/references/brainstorming/SKILL.md` — Main brainstorming skill spec (English). Defines the full design-before-implementation workflow with a hard gate: no code may be written until a design is presented and approved.
  - `docs/references/brainstorming/visual-companion.md` — Guide for the browser-based visual companion used during brainstorming.
  - `docs/references/brainstorming/spec-document-reviewer-prompt.md` — Prompt template for dispatching a spec reviewer subagent.
  - `docs/references/brainstorming/scripts/` — Node.js server and shell scripts that power the visual companion.

## Skill Format

Skills are Markdown files with YAML frontmatter:

```yaml
---
name: skill-name
description: >
  When to trigger this skill. Be specific about user utterances and contexts.
---
```

The `description` field is critical — it determines when the skill is invoked. Skills can reference other files (e.g., `skills/brainstorming/SKILL.md` references `docs/references/brainstorming/visual-companion.md`).

## Visual Companion Server

The brainstorming skill includes a browser-based visual companion for showing mockups, diagrams, and design options. It consists of:

- **`scripts/server.cjs`** — Node.js HTTP/WebSocket server (zero dependencies, uses only built-in modules: `crypto`, `http`, `fs`, `path`). Watches a directory for HTML files and serves the newest one. Auto-exits after 30 minutes of inactivity.
- **`scripts/start-server.sh`** — Starts the server. Outputs JSON with `url`, `port`, `screen_dir`, and `state_dir`.
- **`scripts/stop-server.sh <session_dir>`** — Stops the server.
- **`scripts/frame-template.html`** — HTML/CSS frame template providing theming and UI components (options, cards, mockups, split views).
- **`scripts/helper.js`** — Client-side WebSocket client and interaction tracking.

### Running the Server

```bash
# From docs/references/brainstorming/
cd docs/references/brainstorming

# Start with project persistence (mockups saved to .superpowers/brainstorm/)
scripts/start-server.sh --project-dir /path/to/project

# Start for ephemeral use (files in /tmp)
scripts/start-server.sh

# Stop
scripts/stop-server.sh <session_dir>
```

**Platform notes:**
- The script auto-detects Windows/Git Bash and Codex CI, switching to foreground mode.
- On Windows with Claude Code: use `run_in_background: true` on the Bash tool call.
- On Gemini CLI: use `--foreground` and set `is_background: true`.

### Server Protocol

1. Write HTML fragments (not full documents) to `screen_dir/`
2. Server wraps them in `frame-template.html` and serves the newest file by mtime
3. User interactions (clicks on `[data-choice]` elements) are recorded to `state_dir/events` as JSON lines
4. WebSocket broadcasts `reload` to all clients when new files are detected

## Key Architectural Patterns

**Hard Gate Pattern:** The brainstorming skill enforces a design-before-implementation gate. No implementation skills may be invoked, no code written, and no scaffolding performed until a design is presented and explicitly approved by the user. The only skill that may be invoked after brainstorming is `writing-plans`.

**One Question at a Time:** Skills in this repo favor sequential, single-question interactions over bulleted lists. Multiple choice questions are preferred when possible.

**Two-Phase Requirements Elicitation:** The Chinese requirements skill uses a two-phase approach: (1) build a complete question tree marking all ambiguity nodes, (2) traverse the tree one node at a time, updating conclusions as you go.

**Spec-Driven Development:** Designs are written to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, self-reviewed for placeholders and contradictions, then user-reviewed before any implementation planning begins.
