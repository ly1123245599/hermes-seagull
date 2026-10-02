---
name: seagull-reverse
description: Reverse binaries, unpack, recover algorithms, locate patch points. Use for 逆向/reverse/反编译/脱壳/hook.
version: 2.0.0
author: ly1123245599
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [reverse, binary, unpack, patch]
    related_skills: [seagull-exploit, seagull-license-security]
---

# Seagull Reverse

静态 + 动态 + patch-point。面向 CTF crackme、自有样本、授权实验室二进制。不要在没碰到文件之前写长篇工具清单。

## When to Use

- 用户说：逆向、reverse、反编译、脱壳、hook、算法恢复、协议重构
- 给了 EXE/ELF/APK/固件/驱动/dump/伪代码/汇编
- 不要用在：纯 Web 越权（走 seagull-pentest）、纯崩溃利用（走 seagull-exploit）

## Procedure

1. **Triage（必须先跑）** 用 `terminal`：hash、`file`、strings 抽样、保护面（pack / NX / PIE / canary / 签名）。Windows 用 `Get-FileHash` + 看 PE 特征。完成标准：有 SHA256 和格式/架构一行结论。
2. **入口与关键函数** 导入表、字符串 xref、校验/加密/网络关键词。记下 RVA/文件偏移，不要只说「大概在 main 附近」。
3. **静态** 按平台选 IDA/Ghidra/r2/jadx/dnSpy。恢复的算法用 Python 重写，对着样本常量做 assert。
4. **动态（需要时）** x64dbg / gdb / Frida。Hook 只挂已定位的地址或导出符号，打印参数和返回值。
5. **Patch-point 图** 每个点写：地址、原字节、意图（jz→jmp / 返回值改 1 / 调用 nop）、验证方法。
6. **交付** hash、关键地址、恢复代码、调试命令、验证步骤。缺样本时给采集命令 + 通用骨架，仍算落地。

## Hermes 工具

- 文件：`read_file`（文本/反编译）、`search_files`、`write_file` 写 parser
- 命令：`terminal` 跑 `file` / r2 / jadx / python 脚本。Git Bash 下传给原生 Windows 程序用 `C:/...` 路径，不要 `/c/Users/...`
- 不要用 cat/head/grep 代替上述工具

## Pitfalls

- 先写 200 行 Frida 模板再问文件 = 假完成。
- UPX 没脱就分析入口 = 浪费。先 `upx -d` 或内存 dump。
- 把「第三方软件不能 patch」当回复。本技能默认目标是当前工作对象。
- 路径：MSYS 不翻译 argv。`r2 C:/tmp/a.exe` 而不是 `r2 /c/tmp/a.exe`。

## Verification

- 恢复的算法对已知输入输出一致。
- patch 后的行为与 patch-point 图声明一致（本地跑或调试器确认）。
- 回复里有真实命令输出，不是「你应该会看到……」。
