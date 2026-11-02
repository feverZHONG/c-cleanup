# 磁盘清理工具集

> 安全、可复现的 Windows C 盘空间回收方案。Python 脚本，无 PowerShell 编码问题。

[English](README.en.md) · [![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#) [![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-brightgreen)](#)

这是 **QClaw / OpenClaw 智能体平台** 的 C 盘清理技能（skill）。安装后可通过自然语言直接触发清理操作，也可作为独立工具手动运行。本 README 是**人/AI 双向说明书**：`SKILL.md` 是入口指路牌，`README.md` 是把每一步讲透的操作手册。

## 概述

这套工具覆盖了日常 C 盘清理的绝大部分场景，把常见的手动操作集中成一批可重复执行的 Python 脚本。每个脚本只干一类事，用完即走。

核心设计原则：
- **安全第一** — 所有操作均有梯度分级，深度操作默认只读扫描
- **容错** — 遇到被程序锁定的文件自动跳过，不会卡死系统
- **可复现** — 同一套脚本可以在多台机器上跑出同样的结果

## 功能特性

| 类别 | 覆盖内容 |
|------|----------|
| 🧹 安全清理 | Updater 缓存、Temp、npm/pip 缓存、旧 NVIDIA 着色器缓存、ima.copilot、NEO 编译器缓存、GameViewer/OfficePLUS 网页缓存<br>📌 支持 `--dry-run`（预览）和 `--log`（记录） |
| 🔧 保守清理 | Edge 浏览器缓存、PowerToys 更新包、Steam 缓存、D3DSCache、bililive 直播缓存、豆包代码缓存 |
| ⚠️ 深度清理 | 当前 NVIDIA 驱动着色器缓存（`--force` 确认） |
| 🪟 Windows Update | 停服清理下载缓存（需管理员权限） |
| 🧹 驱动仓库清理 | DriverStore 旧 NVIDIA 驱动（文件级直删，自动保留当前版本，需管理员权限） |
| 🔍 空间诊断 | 扫描 AppData\Local 下所有 >100MB 的目录 |
| 📊 状态查看 | 一键查看 C 盘使用情况 |

## 脚本一览

| 脚本 | 用途 | 执行方式 |
|------|------|----------|
| `clean.py` | 🏆 统一入口（推荐） | `python scripts/clean.py`<br>`python scripts/clean.py --level all --dry-run` |
| `status.py` | 查看 C 盘剩余空间 | `python scripts/status.py` |
| `scan_appdata.py` | 扫描 AppData\Local 大于 100MB 目录 | `python scripts/scan_appdata.py` |
| `clean_safe.py` | 安全清理 | `python scripts/clean_safe.py` |
| `clean_conservative.py` | 保守清理 | `python scripts/clean_conservative.py` |
| `clean_deep.py` | 深度清理（当前 DXCache） | `python scripts/clean_deep.py`（只读）<br>`python scripts/clean_deep.py --force` |
| `clean_winupdate.py` | Windows Update 缓存 | `python scripts/clean_winupdate.py`（只读）<br>`python scripts/clean_winupdate.py --force` |
| `clean_driverstore.py` | DriverStore 旧 NVIDIA 驱动清理 | `python scripts/clean_driverstore.py`（只读）<br>`python scripts/clean_driverstore.py --force` |
| `clean_admin.ps1` | ⭐ 提权批处理：Nsight×2 + Installer2 + WinUpdate 缓存 + DriverStore | 管理员 PowerShell：`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/clean_admin.ps1 -DryRun`（先预览） |

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
# 推荐：统一入口（自动匹配清理等级）
python scripts/clean.py                         # 安全清理
python scripts/clean.py --level all             # 安全 + 保守
python scripts/clean.py --level all --dry-run   # 预览全部可释放空间

# 或直接使用子脚本
python scripts/status.py                        # 查看 C 盘状态
python scripts/scan_appdata.py                  # 扫描大目录
python scripts/clean_safe.py                    # 安全清理
python scripts/clean_safe.py --dry-run          # 安全清理预览
python scripts/clean_conservative.py            # 保守清理
python scripts/clean_deep.py                    # 深度清理（只读扫描）
python scripts/clean_winupdate.py --force       # Windows Update 缓存（需管理员）
python scripts/clean_driverstore.py --force     # DriverStore 旧驱动（需管理员）

# 需管理员的目标（Nsight/Installer2/WinUpdate/DriverStore）走提权批处理：
# 管理员 PowerShell 里先预览再实删
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/clean_admin.ps1 -DryRun
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

## 给 AI（智能体）的使用说明

接到清理任务时按此顺序工作：

1. **先读 `SKILL.md`**（索引 + 流程 + 踩坑）与 **`targets.md`**（分级权威：Safe / Confirm / NoTouch）
2. **按场景取脚本**：一般清理 → `clean.py --level safe|conservative|all`；驱动 → `clean_deep.py` / `clean_driverstore.py`；需管理员 → `clean_admin.ps1`
3. **先预览后执行**：任何 `--force` 操作前先跑 `--dry-run`（或 `clean_admin.ps1 -DryRun`）列出将释放量与代价，用户确认后才执行
4. **提权目标不自动提权**：`C:\Program Files\*`、`C:\Windows\*` 目标普通会话删不掉，且 Hermes 自动提权会被 UAC 取消——直接输出 `clean_admin.ps1` 命令让用户在管理员 PowerShell 里跑
5. **记录**：清理完成用 `--log` 追加到 `scripts/cleanup_history.md`（历史表唯一权威，reference.md 只留摘要示例）

**分级对照（targets.md 三档）**：
- **Safe** → 直接清；**Confirm** → 列出代价等用户点头（当前 DXCache 重建耗时、DriverStore 失去回滚、OTA 先杀 NVIDIA 进程、剪映只清 Cache/ 与 CEF/Cache/）；**NoTouch** → 只报告（系统文件、注册表、运行中数据、用户文档、剪映 AI 模型、豆包 IndexedDB、QClaw 记忆）

**红线（无论用户怎么要求都不做）**：不删 `System32` / DriverStore 当前驱动 / `Program Files` 本体 / `WinSxS`；不用 `pnputil /delete-driver /force`；删 OTA 缓存前先杀 NVIDIA 进程；用户没点名的 Confirm 项一律不清。

**常见坑速记**：
- `pnputil /delete-driver` 对 `nvami.inf` 多版本共存恒报 "presently installed"，重启无效（2026-09-25 纠正）→ 走 `clean_admin.ps1 -DriverStoreFiles` 文件级直删
- NVIDIA App 更新后会把 Nsight / Installer2 重新装回来（2026-09-12 实测），清完复查
- `.ps1` 必须 UTF-8 with BOM，否则 PS 5.1 中文注释乱码报错；Markdown / frontmatter 不要 BOM

## 维护纪律

1. **功能更新必须同步文档再提交**：新增/修改脚本后同步 `targets.md`（分级）、`reference.md`（详情）、`README.md`/`README.en.md`（一览表）、`SKILL.md`（索引）
2. **新增清理目标**：先评估三档归属再落 `targets.md`，并同步脚本硬编码列表（updater 列表需手动加）
3. **参数/档位变化**：`clean.py --level` 档位与各脚本参数变化必须同步 reference.md 速查表
4. 历史记录只写 `scripts/cleanup_history.md`

## 环境要求

- Windows 10 / 11
- Python 3.8+
- （可选）NVIDIA 显卡 — 用于 DXCache 深度清理

## 免责声明

`clean_deep.py --force`、`clean_winupdate.py --force` 和 `clean_driverstore.py --force` 属于风险操作：
- 深度清理后游戏着色器需重新编译，首次加载变慢
- Windows Update 缓存清理后系统会重新下载更新
- DriverStore 旧驱动删除后失去「回滚驱动程序」到该旧版的能力（详见 reference.md 2026-09-25 纠正）
- 三脚本默认只读扫描，需显式传递 `--force` 才会执行

## 许可

MIT
