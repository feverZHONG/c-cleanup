# 磁盘清理工具集 / Disk Cleanup Toolkit

> 安全、可复现的 Windows C 盘空间回收方案。Python 脚本，无 PowerShell 编码问题。
>
> Safe, reproducible Windows C: drive space reclamation. Pure Python — no PowerShell encoding pitfalls.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](#)

---

## 中文文档

### 概述

这套工具覆盖了日常 C 盘清理的绝大部分场景，把常见的手动操作集中成一批可重复执行的 Python 脚本。每个脚本只干一类事，用完即走。

核心设计原则：
- **安全第一** — 所有操作均有梯度分级，深度操作默认只读扫描
- **容错** — 遇到被程序锁定的文件自动跳过，不会卡死系统
- **可复现** — 同一套脚本可以在多台机器上跑出同样的结果

### 功能特性

| 类别 | 覆盖内容 |
|------|----------|
| 🧹 安全清理 | Updater 缓存、Temp、npm/pip 缓存、旧 NVIDIA 着色器缓存、ima.copilot、NEO 编译器缓存、GameViewer/OfficePLUS 网页缓存 |
| 🔧 保守清理 | Edge 浏览器缓存、PowerToys 更新包、Steam 缓存、D3DSCache、bililive 直播缓存、豆包代码缓存 |
| ⚠️ 深度清理 | 当前 NVIDIA 驱动着色器缓存（`--force` 确认） |
| 🪟 Windows Update | 停服清理下载缓存（需管理员权限） |
| 🔍 空间诊断 | 扫描 AppData\Local 下所有 >100MB 的目录 |
| 📊 状态查看 | 一键查看 C 盘使用情况 |

### 脚本一览

| 脚本 | 用途 | 执行方式 |
|------|------|----------|
| `status.py` | 查看 C 盘剩余空间 | `python scripts/status.py` |
| `scan_appdata.py` | 扫描 AppData\Local 大于 100MB 目录 | `python scripts/scan_appdata.py` |
| `clean_safe.py` | 安全清理 | `python scripts/clean_safe.py` |
| `clean_conservative.py` | 保守清理 | `python scripts/clean_conservative.py` |
| `clean_deep.py` | 深度清理（当前 DXCache） | `python scripts/clean_deep.py`（只读）<br>`python scripts/clean_deep.py --force` |
| `clean_winupdate.py` | Windows Update 缓存 | `python scripts/clean_winupdate.py`（只读）<br>`python scripts/clean_winupdate.py --force` |

### 快速开始

```bash
# 1. 查看 C 盘状态
python scripts/status.py

# 2. 扫描分析大目录
python scripts/scan_appdata.py

# 3. 安全清理（可随时运行，锁文件自动跳过）
python scripts/clean_safe.py

# 4. 保守清理（定期维护）
python scripts/clean_conservative.py
```

### 安全原则

| 等级 | 说明 |
|------|------|
| ✅ **可自动清理** | Temp、updater 缓存、旧驱动缓存、可重新生成的浏览器缓存 |
| ⚠️ **需用户确认** | 当前 NVIDIA 着色器缓存（重建耗时）、系统级缓存 |
| ❌ **绝对不碰** | 系统文件、注册表、正在运行的程序数据、用户文档 |

所有删除操作逐项 try/except，遇到被占用的文件自动跳过，不会导致系统卡顿或卡死。

### 清理目标参考

详见 [`targets.md`](targets.md) — 按 Safe / Confirm 分级列出各路径和典型大小。

### 环境要求

- Windows 10 / 11
- Python 3.8+
- （可选）NVIDIA 显卡 — 用于 DXCache 深度清理

### 免责声明

`clean_deep.py --force` 和 `clean_winupdate.py --force` 属于风险操作：
- 深度清理后游戏着色器需重新编译，首次加载变慢
- Windows Update 缓存清理后系统会重新下载更新
- 两脚本默认只读扫描，需显式传递 `--force` 才会执行

---

## English Documentation

### Overview

A collection of Python scripts for Windows C: drive space reclamation. Each script handles one category of cleanup, designed to be safe, repeatable, and resilient.

Core principles:
- **Safety-first** — Tiered approach with read-only scanning by default for risky operations
- **Fault-tolerant** — Automatically skips locked files, won't hang your system
- **Reproducible** — Same scripts, same results, across machines

### Features

| Category | Scope |
|----------|-------|
| 🧹 Safe Cleanup | Updater cache, Temp, npm/pip cache, old NVIDIA DXCache, ima.copilot, NEO compiler cache, GameViewer/OfficePLUS web caches |
| 🔧 Conservative Cleanup | Edge browser cache, PowerToys updates, Steam cache, D3DSCache, bililive cache, Doubao code cache |
| ⚠️ Deep Cleanup | Current NVIDIA driver shader cache (`--force` required) |
| 🪟 Windows Update | Service-stop cleanup of download cache (admin required) |
| 🔍 Space Diagnostics | Scan AppData\Local for directories >100MB |
| 📊 Status | One-command C: drive overview |

### Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `status.py` | C: drive space overview | `python scripts/status.py` |
| `scan_appdata.py` | Scan large AppData directories | `python scripts/scan_appdata.py` |
| `clean_safe.py` | Safe cleanup | `python scripts/clean_safe.py` |
| `clean_conservative.py` | Conservative cleanup | `python scripts/clean_conservative.py` |
| `clean_deep.py` | Deep cleanup (current DXCache) | `python scripts/clean_deep.py` (read-only)<br>`python scripts/clean_deep.py --force` |
| `clean_winupdate.py` | Windows Update cache | `python scripts/clean_winupdate.py` (read-only)<br>`python scripts/clean_winupdate.py --force` |

### Quick Start

```bash
# 1. Check C: drive status
python scripts/status.py

# 2. Scan for large directories
python scripts/scan_appdata.py

# 3. Safe cleanup (run anytime, locked files skipped)
python scripts/clean_safe.py

# 4. Conservative cleanup (periodic maintenance)
python scripts/clean_conservative.py
```

### Safety Tiers

| Level | Description |
|-------|-------------|
| ✅ **Auto-safe** | Temp, updater cache, old driver cache, regenerable browser cache |
| ⚠️ **Confirm required** | Current NVIDIA shader cache (rebuild cost), system-level cache |
| ❌ **Never touch** | System files, registry, running process data, user documents |

All delete operations use per-file try/except. Locked files are skipped gracefully.

### Cleanup Targets Reference

See [`targets.md`](targets.md) — categorized by Safe / Confirm with paths and typical sizes.

### Requirements

- Windows 10 / 11
- Python 3.8+
- (Optional) NVIDIA GPU — for DXCache deep cleanup

### Disclaimer

`clean_deep.py --force` and `clean_winupdate.py --force` carry risks:
- Deep cleanup triggers game shader recompilation (first-load slowdown only)
- Windows Update cache cleanup causes re-download of updates
- Both default to read-only mode; explicit `--force` flag required for execution

---

## License

MIT
