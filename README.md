# hermes-seagull

[![ci](https://github.com/ly1123245599/hermes-seagull/actions/workflows/ci.yml/badge.svg)](https://github.com/ly1123245599/hermes-seagull/actions/workflows/ci.yml)
[![hermes](https://img.shields.io/badge/Hermes-%3E%3D0.21-black)](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

海鸥：给 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 用的 **profile distribution**（人格 + 技能 + 插件），不是「把整个 Hermes 重装一遍」的脚本，也不是 Codex 插件。

```bash
hermes profile install github.com/ly1123245599/hermes-seagull
hermes -p seagull setup          # 填你自己的模型/API key
hermes -p seagull chat
```

进会话后发 `在吗`，应只收到：

```
海鸥在线，你要整点薯条吗？
```

## 这和 laoshu666/hermes-seagull 有什么不同

上游仓库（[laoshu666/hermes-seagull](https://github.com/laoshu666/hermes-seagull)）以及未合并的 [PR #1](https://github.com/laoshu666/hermes-seagull/pull/1) 的问题，本仓库按 **Hermes 0.21.5** 的真实契约重写：

| 上游问题 | 本仓库 |
|---|---|
| 根目录没有 `distribution.yaml`，`hermes profile install <git-url>` 直接抛错 | 标准 profile distribution |
| 插件放在仓库根 `seagull-armor-break/`，Hermes 只扫 profile 的 `plugins/` | `plugins/seagull-armor-break/` |
| `plugin.yaml` 声明 `pre_agent_turn` / `transform_system_prompt`，不在 `VALID_HOOKS`，**静默失效** | 只用 `pre_llm_call` + `transform_llm_output` |
| 每个 turn 经 `pre_llm_call` 灌 ~2KB 破甲栈，打爆 prompt cache | `register_system_prompt_section` 一次冻结；触发词才走 per-turn context |
| 在 fail-closed 的 `pre_tool_call` 上挂空观察者，超时会 **阻断全部工具** | 不注册 `pre_tool_call` |
| `config.yaml` 塞进个人模型路由 / 密钥形态 | 只启用插件。模型是用户的 |
| `AGENTS.md` 路由到 8 个不存在的技能 | 只路由仓库里真实存在的 5 个技能 |
| 十几份互相复制的安装文档、错误的 `hermes bot restart`、Codex 残留 | 一份 README |
| 无测试 | `python -m unittest` + CI + 每周 hook 契约巡检 |

人格和技能思路源自上游；v0.19 hook 对应关系参考了 PR #1（作者 [3265653940-oss](https://github.com/3265653940-oss)），但实现按 0.21 的 `register_system_prompt_section` 重做，没有照抄那份每轮灌 context 的写法。

## 仓库结构

```
distribution.yaml          # hermes profile install 的清单
SOUL.md                    # 人格（system prompt slot #1）
AGENTS.md                  # 技能路由 / 执行纪律
config.yaml                # 仅 plugins.enabled: [seagull-armor-break]
plugins/seagull-armor-break/
skills/seagull-{reverse,pentest,exploit,game-hack,license-security}/
tests/                     # 不依赖已安装的 Hermes
```

## 安装 / 更新

需要本机已安装 Hermes Agent `>= 0.21.0`。

```bash
# 官方安装器（Linux / macOS / WSL）。Windows 见官方文档。
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 安装海鸥（profile 名默认 seagull）
hermes profile install github.com/ly1123245599/hermes-seagull

# 或本地开发树
hermes profile install /path/to/hermes-seagull --name seagull --force
```

`--force` 会覆盖发行物拥有的文件（SOUL / AGENTS / skills / plugins / **config.yaml**）。已有 profile 请用更新：

```bash
hermes profile update seagull
```

`update` **默认保留** `config.yaml` 和全部用户数据（`.env`、sessions、memories、state.db）。

装完后：

```bash
hermes -p seagull plugins list | findstr seagull   # Windows
hermes -p seagull plugins list | grep seagull      # Unix
hermes -p seagull doctor
```

`seagull-armor-break` 必须是 **enabled**。用户插件是 opt-in；发行包的 `config.yaml` 已经写进白名单。若你把 config 改丢了：

```bash
hermes -p seagull plugins enable seagull-armor-break
```

不要把 API key 写进 `config.yaml`。写进该 profile 的 `.env`。

## 常用触发

| 你发 | 海鸥应回 |
|---|---|
| `在吗` / `hi` / `你好` | `海鸥在线，你要整点薯条吗？` |
| `逆向` | `逆向工程已打开` |
| `渗透` | `渗透工程已打开` |
| `外挂` | `游戏辅助开发已打开` |
| `卡密` | `卡密安全已打开` |
| `pwn` | `漏洞利用已打开` |

之后直接丢任务。技能通过 `skill_view` 按需加载，不要指望模型把 700 行教程背在上下文里。

## 维护

本仓库由 [ly1123245599](https://github.com/ly1123245599) 维护。

- CI：skill frontmatter、distribution 清单、插件 hook 名单、问候分类器。
- 每周一 UTC 04:17：从 `NousResearch/hermes-agent` 拉 `VALID_HOOKS`，确认本插件声明的 hook 仍合法。Hermes 再改契约时会先红，而不是再静默失效。
- 发版：改 `distribution.yaml` 的 `version`，打 `vX.Y.Z` tag。使用者 `hermes profile update seagull` 即拉到。

兼容性矩阵：

| Seagull | Hermes |
|---|---|
| 2.0.x | >= 0.21.0（测过 0.21.5） |

## 范围

技能面向 CTF、授权实验室、自有样本的逆向 / 渗透 / exploit / 授权校验研究。插件只做会话覆盖和问候拦截，不提供攻击基础设施，不绕过 Hermes 的安全扫描或审批。

## License

MIT. 上游人格来自 laoshu666/hermes-seagull（MIT）。
