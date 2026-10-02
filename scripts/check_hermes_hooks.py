#!/usr/bin/env python3
"""Fail CI if seagull-armor-break declares a hook Hermes no longer fires.

Fetches VALID_HOOKS from NousResearch/hermes-agent (main). Offline, unless
--strict, prints a warning and exits 0.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_YAML = ROOT / "plugins" / "seagull-armor-break" / "plugin.yaml"
HERMES_PLUGINS_PY = (
    "https://raw.githubusercontent.com/NousResearch/hermes-agent/main/hermes_cli/plugins.py"
)


def declared_hooks(text: str) -> list[str]:
    lines = text.splitlines()
    hooks: list[str] = []
    in_list = False
    for line in lines:
        if re.match(r"^provides_hooks:\s*$", line):
            in_list = True
            continue
        if in_list:
            m = re.match(r"^\s+-\s+([A-Za-z0-9_]+)\s*$", line)
            if m:
                hooks.append(m.group(1))
                continue
            if line.strip() and not line.startswith((" ", "\t")):
                break
    return hooks


def parse_valid_hooks(source: str) -> set[str]:
    m = re.search(r"VALID_HOOKS:\s*Set\[str\]\s*=\s*\{(.*?)\n\}", source, re.S)
    if not m:
        raise SystemExit("could not find VALID_HOOKS in hermes_cli/plugins.py")
    return set(re.findall(r'"([a-z0-9_]+)"', m.group(1)))


def fetch(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "hermes-seagull-compat-check"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--strict", action="store_true")
    p.add_argument("--local-plugins-py", type=Path, default=None)
    args = p.parse_args()

    declared = declared_hooks(PLUGIN_YAML.read_text(encoding="utf-8"))
    if not declared:
        print("plugin.yaml has no provides_hooks", file=sys.stderr)
        return 1

    try:
        if args.local_plugins_py:
            source = args.local_plugins_py.read_text(encoding="utf-8")
        else:
            source = fetch(HERMES_PLUGINS_PY)
        valid = parse_valid_hooks(source)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"skip: could not load VALID_HOOKS ({exc})", file=sys.stderr)
        return 1 if args.strict else 0

    unknown = [h for h in declared if h not in valid]
    print(f"declared={declared}")
    print(f"valid_hooks={len(valid)}")
    if unknown:
        print(f"UNKNOWN HOOKS (will silently no-op in Hermes): {unknown}", file=sys.stderr)
        return 1
    print("ok: all declared hooks are in VALID_HOOKS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
