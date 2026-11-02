# Disk Cleanup Toolkit

> Safe, reproducible Windows C: drive space reclamation. Pure Python — no PowerShell encoding pitfalls.

[中文](README.md) · [![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#) [![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-brightgreen)](#)

This is a **skill for the QClaw / OpenClaw agent platform**. Installed as a skill, it can be triggered via natural language (e.g., "C drive is full", "clean up disk space"). It also works as a standalone tool when invoked directly. This README is a **dual-purpose manual for humans and AI**: `SKILL.md` is the entry signpost, `README.md` is the step-by-step operation manual.

## Overview

A collection of Python scripts for Windows C: drive space reclamation. Each script handles one category of cleanup, designed to be safe, repeatable, and resilient.

Core principles:
- **Safety-first** — Tiered approach with read-only scanning by default for risky operations
- **Fault-tolerant** — Automatically skips locked files, won't hang your system
- **Reproducible** — Same scripts, same results, across machines

## Features

| Category | Scope |
|----------|-------|
| 🧹 Safe Cleanup | Updater cache, Temp, npm/pip cache, old NVIDIA DXCache, ima.copilot, NEO compiler cache, GameViewer/OfficePLUS web caches<br>📌 Supports `--dry-run` (preview) and `--log` (record) |
| 🔧 Conservative Cleanup | Edge browser cache, PowerToys updates, Steam cache, D3DSCache, bililive cache, Doubao code cache |
| ⚠️ Deep Cleanup | Current NVIDIA driver shader cache (`--force` required) |
| 🪟 Windows Update | Service-stop cleanup of download cache (admin required) |
| 🧹 Driver Store Cleanup | Old NVIDIA drivers in DriverStore (file-level delete, keeps current version, admin required) |
| 🔍 Space Diagnostics | Scan AppData\Local for directories >100MB |
| 📊 Status | One-command C: drive overview |

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `clean.py` | 🏆 Unified entry (recommended) | `python scripts/clean.py`<br>`python scripts/clean.py --level all --dry-run` |
| `status.py` | C: drive space overview | `python scripts/status.py` |
| `scan_appdata.py` | Scan large AppData directories | `python scripts/scan_appdata.py` |
| `clean_safe.py` | Safe cleanup | `python scripts/clean_safe.py` |
| `clean_conservative.py` | Conservative cleanup | `python scripts/clean_conservative.py` |
| `clean_deep.py` | Deep cleanup (current DXCache) | `python scripts/clean_deep.py` (read-only)<br>`python scripts/clean_deep.py --force` |
| `clean_winupdate.py` | Windows Update cache | `python scripts/clean_winupdate.py` (read-only)<br>`python scripts/clean_winupdate.py --force` |
| `clean_driverstore.py` | Old NVIDIA drivers in DriverStore | `python scripts/clean_driverstore.py` (read-only)<br>`python scripts/clean_driverstore.py --force` |
| `clean_admin.ps1` | ⭐ Admin-elevated batch: Nsight×2 + Installer2 + WinUpdate cache + DriverStore | Admin PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/clean_admin.ps1 -DryRun` (preview first) |

## Installation

### Install as a QClaw Skill

```bash
skillhub_install install_skill c-cleanup
```

Once installed, the agent automatically triggers the appropriate script when you say "C drive is full", "clean up disk space", or similar natural language commands.

### Standalone Use

Clone the repo and run scripts directly:

```bash
git clone https://github.com/feverZHONG/c-cleanup.git
cd c-cleanup
python scripts/status.py
```

## Quick Start

```bash
# Recommended: unified entry point
python scripts/clean.py                         # Safe cleanup
python scripts/clean.py --level all             # Safe + Conservative
python scripts/clean.py --level all --dry-run   # Preview all reclaimable space

# Or use individual scripts
python scripts/status.py                        # Check C: drive status
python scripts/scan_appdata.py                  # Scan large directories
python scripts/clean_safe.py                    # Safe cleanup
python scripts/clean_safe.py --dry-run          # Safe cleanup preview
python scripts/clean_conservative.py            # Conservative cleanup
python scripts/clean_deep.py                    # Deep cleanup (read-only scan)
python scripts/clean_winupdate.py --force       # Windows Update cache (admin required)
python scripts/clean_driverstore.py --force     # DriverStore old drivers (admin required)

# Admin targets (Nsight/Installer2/WinUpdate/DriverStore) go through the elevated batch:
# In an admin PowerShell, preview first, then run for real.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/clean_admin.ps1 -DryRun
```

## Safety Tiers

| Level | Description |
|-------|-------------|
| ✅ **Auto-safe** | Temp, updater cache, old driver cache, regenerable browser cache |
| ⚠️ **Confirm required** | Current NVIDIA shader cache (rebuild cost), system-level cache |
| ❌ **Never touch** | System files, registry, running process data, user documents |

All delete operations use per-file try/except. Locked files are skipped gracefully.

## Cleanup Targets Reference

See [`targets.md`](targets.md) — categorized by Safe / Confirm with paths and typical sizes.

## For AI Agents

Work in this order when handed a cleanup task:

1. **Read `SKILL.md`** (index + flow + pitfalls) and **`targets.md`** (authoritative tiers: Safe / Confirm / NoTouch)
2. **Pick the script by scenario**: general cleanup → `clean.py --level safe|conservative|all`; drivers → `clean_deep.py` / `clean_driverstore.py`; admin targets → `clean_admin.ps1`
3. **Preview before executing**: any `--force` operation must first run `--dry-run` (or `clean_admin.ps1 -DryRun`) to list reclaimable space and cost; execute only after user confirmation
4. **Never auto-elevate**: `C:\Program Files\*` and `C:\Windows\*` targets cannot be deleted from a normal session, and Hermes auto-elevation gets cancelled by UAC — hand the `clean_admin.ps1` command to the user to run in an admin PowerShell
5. **Record**: use `--log` to append to `scripts/cleanup_history.md` (single source of truth for history; reference.md keeps only a summary example)

**Tier mapping (targets.md)**:
- **Safe** → clean directly; **Confirm** → list the cost and wait for consent (current DXCache rebuild time, DriverStore losing rollback ability, kill NVIDIA processes before OTA cleanup, JianyingPro only `Cache/` and `CEF/Cache/`); **NoTouch** → report only (system files, registry, running-process data, user documents, JianyingPro AI models, Doubao IndexedDB, QClaw memory)

**Red lines (never, even if the user insists)**: no `System32` / current DriverStore driver / `Program Files` bodies / `WinSxS`; no `pnputil /delete-driver /force`; kill NVIDIA processes before OTA cache deletion; unconfirmed Confirm items are never cleaned.

**Pitfall quick notes**:
- `pnputil /delete-driver` always reports "presently installed" for multi-version `nvami.inf`; rebooting does not help (2026-09-25 correction) → use `clean_admin.ps1 -DriverStoreFiles` (file-level delete)
- NVIDIA App re-installs Nsight / Installer2 after every update flow (verified 2026-09-12) — re-check after cleaning
- `.ps1` files must be UTF-8 with BOM, or PS 5.1 garbles Chinese comments; Markdown / frontmatter must NOT have a BOM

## Maintenance Discipline

1. **Sync docs before committing feature changes**: after adding/modifying scripts, sync `targets.md` (tiers), `reference.md` (details), `README.md`/`README.en.md` (overview tables), `SKILL.md` (index)
2. **New cleanup targets**: evaluate Safe / Confirm / NoTouch first, then add to `targets.md` and the script's hardcoded list (updater list needs manual addition)
3. **Parameter / level changes**: `clean.py --level` tiers and per-script flags must be reflected in the reference.md quick table
4. History records only live in `scripts/cleanup_history.md`

## Requirements

- Windows 10 / 11
- Python 3.8+
- (Optional) NVIDIA GPU — for DXCache deep cleanup

## Disclaimer

`clean_deep.py --force`, `clean_winupdate.py --force` and `clean_driverstore.py --force` carry risks:
- Deep cleanup triggers game shader recompilation (first-load slowdown only)
- Windows Update cache cleanup causes re-download of updates
- DriverStore old-driver deletion loses the ability to "roll back the driver" to that old version (see reference.md 2026-09-25 correction)
- All three default to read-only mode; explicit `--force` flag required for execution

## License

MIT
