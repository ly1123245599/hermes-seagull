# Changelog

## 2.0.0 — 2026-10-02

Rewrite against Hermes Agent 0.21.5. New GitHub home: `ly1123245599/hermes-seagull`.

### Breaking

- Install path is now a real profile distribution (`distribution.yaml` at repo root). `hermes profile install <git-url>` works.
- Plugin lives at `plugins/seagull-armor-break/` (Hermes only scans `plugins/`).
- `hermes_requires: ">=0.21.0"`.
- Distro `config.yaml` no longer ships a model/provider. Users run `hermes -p seagull setup`.
- AGENTS.md no longer names skills that are not in the repo.

### Plugin

- Drop illegal hooks `pre_agent_turn` / `transform_system_prompt` (never in `VALID_HOOKS`; silent no-op).
- Drop `pre_tool_call` observer (fail-closed in 0.21 — timeout blocks every tool).
- Add `ctx.register_system_prompt_section("seagull-armor", ...)` so the overlay is frozen into the session prompt (prompt-cache friendly).
- `pre_llm_call` injects context only on a *bare* greeting or skill-trigger turn.
- `transform_llm_output` pins the exact confirmation line.

### Skills

- YAML frontmatter on all five skills (`name`, `description`, `version`, `platforms`).
- Hermes-tool framing; demo scripts for ESP / IDOR / license harness.

### Docs / CI

- Single README. No more overlapping install novels.
- `python -m unittest` + GitHub Actions + weekly VALID_HOOKS drift check.

### Credit

- Persona origin: [laoshu666/hermes-seagull](https://github.com/laoshu666/hermes-seagull).
- v0.19 hook mapping documented in [PR #1](https://github.com/laoshu666/hermes-seagull/pull/1) by 3265653940-oss; this tree does not vendor that plugin verbatim.
