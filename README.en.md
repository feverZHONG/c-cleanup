# Disk Cleanup Toolkit

> Safe, reproducible Windows C: drive space reclamation. Pure Python — no PowerShell encoding pitfalls.

[中文](README.md) · [![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#) [![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-brightgreen)](#)

This is a **skill for the QClaw / OpenClaw agent platform**. Installed as a skill, it can be triggered via natural language (e.g., "C drive is full", "clean up disk space"). It also works as a standalone tool when invoked directly.

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

## Requirements

- Windows 10 / 11
- Python 3.8+
- (Optional) NVIDIA GPU — for DXCache deep cleanup

## Disclaimer

`clean_deep.py --force` and `clean_winupdate.py --force` carry risks:
- Deep cleanup triggers game shader recompilation (first-load slowdown only)
- Windows Update cache cleanup causes re-download of updates
- Both default to read-only mode; explicit `--force` flag required for execution

## License

MIT
