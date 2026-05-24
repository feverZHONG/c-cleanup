# 磁盘清理工具集

> 安全、可复现的 Windows C 盘空间回收方案。Python 脚本，无 PowerShell 编码问题。

[English](README.en.md) · [![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#) [![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-brightgreen)](#)

这是 **QClaw / OpenClaw 智能体平台** 的 C 盘清理技能（skill）。安装后可通过自然语言直接触发清理操作，也可作为独立工具手动运行。

## 概述

这套工具覆盖了日常 C 盘清理的绝大部分场景，把常见的手动操作集中成一批可重复执行的 Python 脚本。每个脚本只干一类事，用完即走。

核心设计原则：
- **安全第一** — 所有操作均有梯度分级，深度操作默认只读扫描
- **容错** — 遇到被程序锁定的文件自动跳过，不会卡死系统
- **可复现** — 同一套脚本可以在多台机器上跑出同样的结果

## 功能特性

| 类别 | 覆盖内容 |
|------|----------|
| 🧹 安全清理 | Updater 缓存、Temp、npm/pip 缓存、旧 NVIDIA 着色器缓存、ima.copilot、NEO 编译器缓存、GameViewer/OfficePLUS 网页缓存 |
| 🔧 保守清理 | Edge 浏览器缓存、PowerToys 更新包、Steam 缓存、D3DSCache、bililive 直播缓存、豆包代码缓存 |
| ⚠️ 深度清理 | 当前 NVIDIA 驱动着色器缓存（`--force` 确认） |
| 🪟 Windows Update | 停服清理下载缓存（需管理员权限） |
| 🔍 空间诊断 | 扫描 AppData\Local 下所有 >100MB 的目录 |
| 📊 状态查看 | 一键查看 C 盘使用情况 |

## 脚本一览

| 脚本 | 用途 | 执行方式 |
|------|------|----------|
| `status.py` | 查看 C 盘剩余空间 | `python scripts/status.py` |
| `scan_appdata.py` | 扫描 AppData\Local 大于 100MB 目录 | `python scripts/scan_appdata.py` |
| `clean_safe.py` | 安全清理 | `python scripts/clean_safe.py` |
| `clean_conservative.py` | 保守清理 | `python scripts/clean_conservative.py` |
| `clean_deep.py` | 深度清理（当前 DXCache） | `python scripts/clean_deep.py`（只读）<br>`python scripts/clean_deep.py --force` |
| `clean_winupdate.py` | Windows Update 缓存 | `python scripts/clean_winupdate.py`（只读）<br>`python scripts/clean_winupdate.py --force` |

## 安装

### 作为 QClaw 技能安装

```bash
skillhub_install install_skill c-cleanup
```

安装后，当你说"C盘满了"、"清理C盘"、"释放C盘空间"等指令时，智能体会自动触发对应脚本。

### 手动使用

克隆仓库后直接调用脚本：

```bash
git clone https://github.com/feverZHONG/c-cleanup.git
cd c-cleanup
python scripts/status.py
```

## 快速开始

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

## 安全原则

| 等级 | 说明 |
|------|------|
| ✅ **可自动清理** | Temp、updater 缓存、旧驱动缓存、可重新生成的浏览器缓存 |
| ⚠️ **需用户确认** | 当前 NVIDIA 着色器缓存（重建耗时）、系统级缓存 |
| ❌ **绝对不碰** | 系统文件、注册表、正在运行的程序数据、用户文档 |

所有删除操作逐项 try/except，遇到被占用的文件自动跳过，不会导致系统卡顿。

## 清理目标参考

详见 [`targets.md`](targets.md) — 按 Safe / Confirm 分级列出各路径和典型大小。

## 环境要求

- Windows 10 / 11
- Python 3.8+
- （可选）NVIDIA 显卡 — 用于 DXCache 深度清理

## 免责声明

`clean_deep.py --force` 和 `clean_winupdate.py --force` 属于风险操作：
- 深度清理后游戏着色器需重新编译，首次加载变慢
- Windows Update 缓存清理后系统会重新下载更新
- 两脚本默认只读扫描，需显式传递 `--force` 才会执行

## 许可

MIT
