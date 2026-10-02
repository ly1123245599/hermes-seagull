# Security

This repository is a Hermes **profile distribution**: persona files, skills, and a small overlay plugin.

- Do not open issues that include API keys, `.env` contents, license serials for third-party products, or live target credentials.
- Do not send exploit payloads against systems you do not own. Skills assume CTF / lab / operator-owned artifacts.
- The plugin does **not** disable Hermes safety scanning, approval gates, or secret redaction. Reports that it "jailbreaks Hermes" are out of scope.

If you find a bug that lets the plugin hang `pre_tool_call` (or any fail-closed hook) and block the agent, open a **Bug** issue with Hermes version and `hermes -p seagull plugins list` output. That class of defect is treated as a reliability incident, not a feature request.
