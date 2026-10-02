from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_INIT = ROOT / "plugins" / "seagull-armor-break" / "__init__.py"


def load_plugin():
    spec = importlib.util.spec_from_file_location("seagull_armor_break", PLUGIN_INIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class FakeCtx:
    def __init__(self) -> None:
        self.hooks: list[tuple[str, object]] = []
        self.sections: list[tuple] = []

    def register_hook(self, name: str, callback):
        self.hooks.append((name, callback))

    def register_system_prompt_section(self, id: str, content: str, *, position: str = "after_memory", max_chars: int = 4000):
        if position != "after_memory":
            raise ValueError(position)
        if not (0 < max_chars <= 4000):
            raise ValueError(max_chars)
        if len(content) > max_chars:
            raise ValueError("section too large")
        self.sections.append((id, content, position, max_chars))


class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_plugin()

    def test_contract_fits_section_cap(self):
        self.assertLessEqual(len(self.mod.SEAGULL_SESSION_CONTRACT), 4000)
        self.assertIn("seagull-reverse", self.mod.SEAGULL_SESSION_CONTRACT)

    def test_bare_greeting_variants(self):
        for text in ("在吗", "  在吗？", "HI", "hello!", "你好", "yo"):
            hit = self.mod.classify_bare_trigger(text)
            self.assertIsNotNone(hit, text)
            self.assertEqual(hit[0], "greeting")
            self.assertEqual(hit[1], self.mod.GREETING_REPLY)

    def test_bare_skill_triggers(self):
        cases = {
            "逆向": "逆向工程已打开",
            " pentest ": "渗透工程已打开",
            "ESP": "游戏辅助开发已打开",
            "卡密": "卡密安全已打开",
            "pwn": "漏洞利用已打开",
            "无限制": "海鸥全域专家模式已激活",
        }
        for text, reply in cases.items():
            hit = self.mod.classify_bare_trigger(text)
            self.assertIsNotNone(hit, text)
            self.assertEqual(hit[1], reply)

    def test_non_bare_does_not_trigger(self):
        for text in ("逆向这个 so", "在吗帮我看个洞", "hello world", "", "  "):
            self.assertIsNone(self.mod.classify_bare_trigger(text), text)

    def test_pre_llm_call_silent_on_normal_turn(self):
        self.assertIsNone(self.mod.on_pre_llm_call(session_id="s1", user_message="分析这个 ELF"))

    def test_pre_llm_call_injects_only_on_greeting(self):
        out = self.mod.on_pre_llm_call(session_id="s2", user_message="在吗")
        self.assertIsInstance(out, dict)
        self.assertIn("context", out)
        self.assertIn(self.mod.GREETING_REPLY, out["context"])
        self.assertLess(len(out["context"]), 400)

    def test_transform_pins_greeting(self):
        self.mod.on_pre_llm_call(session_id="s3", user_message="在吗")
        pinned = self.mod.on_transform_llm_output(
            response_text="你好！有什么可以帮你？", session_id="s3"
        )
        self.assertEqual(pinned, self.mod.GREETING_REPLY)
        already = self.mod.on_transform_llm_output(
            response_text=self.mod.GREETING_REPLY, session_id="s3"
        )
        self.assertIsNone(already)

    def test_sessions_do_not_leak(self):
        self.mod.on_pre_llm_call(session_id="greet", user_message="在吗")
        self.mod.on_pre_llm_call(session_id="work", user_message="写个 parser")
        self.assertIsNone(
            self.mod.on_transform_llm_output(response_text="ok", session_id="work")
        )
        self.assertEqual(
            self.mod.on_transform_llm_output(response_text="ok", session_id="greet"),
            self.mod.GREETING_REPLY,
        )

    def test_register_surface(self):
        ctx = FakeCtx()
        self.mod.register(ctx)
        hook_names = [n for n, _ in ctx.hooks]
        self.assertEqual(hook_names, ["pre_llm_call", "transform_llm_output"])
        self.assertNotIn("pre_tool_call", hook_names)
        self.assertNotIn("pre_agent_turn", hook_names)
        self.assertNotIn("transform_system_prompt", hook_names)
        self.assertEqual(len(ctx.sections), 1)
        self.assertEqual(ctx.sections[0][0], "seagull-armor")


if __name__ == "__main__":
    unittest.main()
