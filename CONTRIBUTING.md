# Contributing

This is a Hermes **profile distribution**, not a fork of Hermes itself.

1. Keep `distribution.yaml` at the repo root. Without it `hermes profile install` refuses the tree.
2. User plugins live in `plugins/<name>/` with `plugin.yaml` + `register(ctx)`.
3. Only declare hooks that exist in Hermes `VALID_HOOKS`. Never `pre_agent_turn` / `transform_system_prompt`. Do not put observers on fail-closed `pre_tool_call` unless you actually gate tools.
4. Do not put API keys, `base_url`, or a default model in distro `config.yaml`. `hermes profile install --force` overwrites that file; `hermes profile update` preserves it.
5. Skills in `AGENTS.md` must exist under `skills/`. Ghost names (`seagull-unlimited`, …) are a regression.
6. Personality in `SOUL.md`. Routing in `AGENTS.md`. Plugin overlay stays under 4000 chars.
7. Tests: `python -m unittest discover -s tests -v` from repo root.

Bump `distribution.yaml` `version` on every release users should pull with `hermes profile update seagull`.

When Hermes bumps `DEFAULT_CONFIG._config_version`, update distro `config.yaml` `_config_version` to match (currently 49 on 0.21.5). Fresh installs otherwise show `v0 → vN` in `hermes doctor`.

Weekly Actions job `hermes-compat.yml` fetches `VALID_HOOKS` from `NousResearch/hermes-agent` main. A red run means the overlay declared a hook Hermes dropped — fix `plugin.yaml` + `__init__.py` before users update.
