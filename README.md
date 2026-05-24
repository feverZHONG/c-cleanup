# C盘安全清理技能

> C 盘空间管理工具集 — 安全清理、定期维护、深度清理全覆盖。

通过 Python 脚本执行，避免 PowerShell 编码问题。

## 功能

- **安全清理** — 一键清理 updater 缓存、Temp、npm/pip 缓存、旧 NVIDIA 着色器缓存等
- **保守清理** — Edge 浏览器缓存、PowerToys 更新包、Steam 缓存、Doubao 缓存等
- **深度清理** — 当前 NVIDIA 驱动着色器缓存（需 `--force` 确认）
- **Windows Update 缓存** — 停服清理下载缓存（需管理员权限）
- **空间诊断** — 扫描 AppData 大户目录

## 脚本一览

| 脚本 | 用途 | 风险 |
|------|------|------|
| `status.py` | 查看 C 盘剩余空间 | 无 |
| `scan_appdata.py` | 扫描 AppData\Local >100MB 的目录 | 无 |
| `clean_safe.py` | 安全清理（updater / Temp / 旧DXCache / ima / NEO / GameViewer / OfficePLUS） | 低，锁文件自动跳过 |
| `clean_conservative.py` | 保守清理（Edge / PowerToys / Steam / Doubao / bililive） | 低，锁文件自动跳过 |
| `clean_deep.py` | 删除当前 NVIDIA 驱动着色器缓存 | 中，默认只读，`--force` 执行 |
| `clean_winupdate.py` | 清理 Windows Update 下载缓存 | 中，`--force` 执行，需管理员 |

## 快速开始

```bash
# 查看 C 盘状态
python scripts/status.py

# 扫描分析
python scripts/scan_appdata.py

# 安全清理
python scripts/clean_safe.py

# 保守清理
python scripts/clean_conservative.py
```

## 安全原则

| 类别 | 处理方式 |
|------|----------|
| **可直接清理** | Temp、updater 缓存、旧驱动缓存、可重新生成的缓存 |
| **需用户确认** | 当前 NVIDIA 着色器缓存（重建耗时）、软件缓存 |
| **绝对不碰** | 系统文件、注册表、正在运行的程序数据、用户重要文件 |

脚本中所有删除操作均使用 try/except 捕获权限错误，遇到正在被程序占用的文件会自动跳过，不会导致系统卡顿。

## 清理目标参考

详见 [`targets.md`](targets.md)。

## 环境要求

- Python 3.8+
- Windows 10 / 11
- NVIDIA 驱动缓存清理需要 NVIDIA 显卡

## 免责声明

执行 `clean_deep.py --force` 和 `clean_winupdate.py --force` 前请确认理解风险。深度清理会导致游戏着色器重新编译（仅影响首次加载速度），Windows Update 缓存清理后系统会重新下载更新。
