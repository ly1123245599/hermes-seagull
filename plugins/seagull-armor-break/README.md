# seagull-armor-break

Hermes **user plugin** that ships inside the Seagull profile distribution.

It does **not** monkey-patch Hermes. It uses only documented `PluginContext` APIs that exist in Hermes 0.21+:

| API | Why |
|---|---|
| `register_system_prompt_section` | Frozen into the session prompt once. Cache-friendly. Caps at 4000 chars. |
| `pre_llm_call` | Tiny per-turn context **only** for a bare greeting / skill trigger. |
| `transform_llm_output` | Force the exact greeting / trigger confirmation line. |

It deliberately does **not** register `pre_tool_call`. That hook is fail-closed: a hung observer blocks every tool.

## What this is not

- Not a jailbreak of Hermes safety tooling.
- Not an install of extra CLIs. Skills tell the agent which tools to use.
- Not a replacement for `SOUL.md`. Personality lives in SOUL; this plugin is the small, stable overlay + greeting interceptor.

## Enable

User plugins are opt-in. The distribution's `config.yaml` already contains:

```yaml
plugins:
  enabled:
    - seagull-armor-break
```

On a profile that did not come from this distro:

```bash
hermes -p seagull plugins enable seagull-armor-break
```
