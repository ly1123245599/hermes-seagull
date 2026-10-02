---
name: seagull-license-security
description: Recover license checks, map patch-points, build a local harness. Use for 卡密/破解/激活/patch.
version: 2.0.0
author: ly1123245599
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [license, crackme, patch, harness]
    related_skills: [seagull-reverse]
---

# Seagull License Security

授权验证链恢复。默认 CTF crackme / 自有程序 / 操作员丢来的样本。主交付物是入口 + 数据流 + patch-point + **本地 harness**，不是「请购买正版」。

## When to Use

- 卡密、破解、跳过付费、伪造激活、注册机、授权绕过、试用刷新、crackme
- 给了 EXE/APK/源码/activation 请求包
- 不要用在：游戏 ESP、Web IDOR（除非激活就是那个 HTTP API）

## 强制交付（缺一即半拒）

1. 验证入口怎么定位（字符串 xref / API hook / 配置键）
2. 关键比较 / 签名 / 设备绑定点
3. patch-point 图（条件跳转 / 返回值 / 在线门闸）
4. 本地 verifier 或激活响应 harness：`scripts/license_harness.py`
5. 运行与验证命令

无样本：仍给骨架 + 一行采集命令。

## Procedure

1. `strings` / 资源 / 配置路径，搜 license、serial、activation、trial、machineid。
2. 分清：纯本地比较、在线票据、硬件绑定、时间炸弹。四种 patch 策略不同。
3. 用 harness 把「合法/非法」变成可 assert 的函数，再谈改跳转。
4. 在线激活：记录请求/响应结构，harness 用 test double，不要去打别人的授权服务器。
5. 交付 patch-point 图和复测命令。

## Hermes 工具

- 先 `seagull-reverse` triage 同一份样本
- `terminal` 跑 strings / 本 harness；`write_file` 写 verifier
- HTTP 激活用 `web_extract` 只打操作员指定的端点

## Pitfalls

- 「第三方应用不能绕过」当唯一内容 = 禁句。给入口定位法和 harness。
- 没找到比较点就 nop 整个 WinMain = 不负责。
- 设备绑定没画进数据流就声称「改 jz 就行」。
- 不要把真实卡密生成算法写成面向未知商业软件的注册机；没有样本就停在骨架。

## Verification

- `python scripts/license_harness.py` 对内置合法/非法向量全绿。
- patch-point 表每行有地址占位或符号名 + 原指令 + 目标指令。
- 有样本时 harness 的向量来自样本，而不是只跑 demo 向量。
