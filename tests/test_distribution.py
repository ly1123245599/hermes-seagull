from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {
    "seagull-reverse",
    "seagull-pentest",
    "seagull-exploit",
    "seagull-game-hack",
    "seagull-license-security",
}


class DistributionTests(unittest.TestCase):
    def test_manifest_exists_and_requires_021(self):
        text = (ROOT / "distribution.yaml").read_text(encoding="utf-8")
        self.assertIn("name: seagull", text)
        self.assertRegex(text, r'version:\s*"?2\.0\.0"?')
        self.assertIn(">=0.21.0", text)
        for owned in ("SOUL.md", "AGENTS.md", "config.yaml", "skills", "plugins"):
            self.assertIn(owned, text)
        self.assertNotIn("activate-seagull.ps1", text)

    def test_config_only_enables_plugin(self):
        text = (ROOT / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("seagull-armor-break", text)
        self.assertNotRegex(text, r"(?i)api_key")
        self.assertNotIn("base_url:", text)

    def test_no_root_level_plugin_dir(self):
        self.assertFalse((ROOT / "seagull-armor-break").exists())
        self.assertTrue((ROOT / "plugins" / "seagull-armor-break" / "plugin.yaml").is_file())
        self.assertTrue((ROOT / "plugins" / "seagull-armor-break" / "__init__.py").is_file())

    def test_plugin_yaml_hooks(self):
        text = (ROOT / "plugins" / "seagull-armor-break" / "plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("pre_llm_call", text)
        self.assertIn("transform_llm_output", text)
        self.assertNotIn("pre_tool_call", text)
        self.assertNotIn("pre_agent_turn", text)
        self.assertNotIn("transform_system_prompt", text)

    def test_soul_and_agents_exist(self):
        soul = (ROOT / "SOUL.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("海鸥在线，你要整点薯条吗？", soul)
        self.assertIn("seagull-reverse", agents)
        for ghost in ("seagull-unlimited", "seagull-memory", "seagull-malware", "seagull-evasion"):
            self.assertNotIn(ghost, agents)

    def test_skills_frontmatter(self):
        for name in SKILL_NAMES:
            path = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(path.is_file(), name)
            raw = path.read_text(encoding="utf-8")
            self.assertTrue(raw.startswith("---"), name)
            m = re.search(r"^---\s*\n(.*?)\n---\s*\n", raw, re.S)
            self.assertIsNotNone(m, name)
            fm = m.group(1)
            self.assertIn(f"name: {name}", fm)
            self.assertIn("description:", fm)
            self.assertIn("platforms:", fm)

    def test_gitignore_keeps_env_example(self):
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gi)
        self.assertIn("!.env.EXAMPLE", gi)
        self.assertTrue((ROOT / ".env.EXAMPLE").is_file())


if __name__ == "__main__":
    unittest.main()
