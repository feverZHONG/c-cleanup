# 清理目标分级表

## Safe Targets（可直接清理，无需确认）

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|----------|------|
| **Updater 缓存** | `AppData\Local\` 下以 `*-updater` 或 `@*` 的文件夹 | 0.1~3 GB | 各类软件的更新缓存，删除自动重建。⚠ 脚本内为硬编码列表（见 clean_safe.py），新出现的 updater 需手动加入，如 `com.ugreen.desktop-updater`（UGREEN NAS 客户端，~425 MB）、`@deepseek-aidsh-desktop-updater`（~158 MB）、`chatglm-updater`（~63 MB）、`qclaw-updater`（~518 MB） |
| **C 盘根目录临时文件** | `C:\temp_ts_merge` | 0.1~1 GB | TS 下载临时碎片，视频下完即可删除 |
| **旧 NVIDIA 驱动缓存** | `NVIDIA\DXCache\` 中非当前驱动前缀的文件 | 几十 MB~数 GB | 不同前缀=不同驱动版本。非当前前缀可直接删除。当前前缀通过 `clean_deep.py` 扫描确定 |
| **用户 Temp** | `%TEMP%` | 几十~几百 MB | 临时文件，无实际用途 |
| **npm/pip 缓存** | `%LOCALAPPDATA%\pip\cache`、`%LOCALAPPDATA%\npm-cache`、`%LOCALAPPDATA%\pnpm-cache` | 几十~几百 MB | 删除下次安装重新下载 |
| **Steam htmlcache** | `%LOCALAPPDATA%\Steam\htmlcache` | 200~300 MB | Steam 内置浏览器缓存，无害 |
| **bililive** | `%LOCALAPPDATA%\bililive` | 100~200 MB | B站直播缓存 |
| **ima.copilot 缓存** | `%LOCALAPPDATA%\ima.copilot` | 600~700 MB | IMA 知识库客户端缓存，删除自动重建 |
| **NEO 着色器缓存** | `%LOCALAPPDATA%\NEO\neo_compiler_cache` | ~200 MB | OpenCL 着色器编译缓存（.cl_cache），删除下次运行自动重建 |
| **GameViewer webviewcache** | `%LOCALAPPDATA%\GameViewer\webviewcache` | ~125 MB | 网页视图缓存，可安全删除 |
| **OfficePLUS WebView2** | `%LOCALAPPDATA%\OfficePLUS\webview2` | ~130 MB | OfficePLUS 的 WebView2 缓存，可安全删除 |
| **CrashDumps 崩溃转储** | `%LOCALAPPDATA%\CrashDumps` | 几十~几百 MB | 程序崩溃转储文件，无实际用途。清内容不删目录（2026-09-12 清出 204 MB） |
| **SquirrelTemp 更新残留** | `%LOCALAPPDATA%\SquirrelTemp` | 0~600 MB | .NET Squirrel 安装器（KOOK 等）的更新包残留，含 `*.nupkg` + `app-*.7z`。清内容不删目录 |
| **Nsight**（⚠需管理员） | `C:\Program Files\NVIDIA Corporation\Nsight Systems *` / `Nsight Compute *` | ~1.6 GB | CUDA 开发者调试工具，纯剪辑/游戏用户用不到，可直接删。**Program Files 需管理员** → 用 `scripts/clean_admin.ps1` |
| **NVIDIA Installer2**（⚠需管理员） | `C:\Program Files\NVIDIA Corporation\Installer2` | ~300 MB | NVIDIA 安装器残留缓存，可直接删除。**需管理员** → 用 `scripts/clean_admin.ps1` |

> **⚠ 需要管理员权限的目标**：`C:\Program Files\*` 和 `C:\Windows\*` 下的所有目标，普通会话删不掉（访问被拒绝）。
> Hermes 会话里也**无法自动提权**：`Start-Process -Verb RunAs` 会被 UAC 取消，且 `-Verb RunAs` 与 `-RedirectStandardOutput` 参数集冲突。
> 统一走 `scripts/clean_admin.ps1`，由阁下在管理员 PowerShell 里手动运行（一次搞定 Nsight ×2 + Installer2 + WinUpdate 缓存，`-DriverStore` 可带上旧驱动）。

## Confirm Targets（需用户确认）—— Trae AI IDE 数据

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|------|------|
| **Trae CN 数据** | `%APPDATA%\Trae CN` + `~\.trae-cn` | 4.4 + 0.7 GB | 字节 AI IDE。`ModularData\ai-agent\database.db` 是 AI 会话历史（1.6 GB，删了对话全丢），`logs`/`CachedData`/`Crashpad` 是纯垃圾可随手清（~0.9 GB）。**用户态度（2026-08-25 澄清）：本体留在 D 盘不删，只清 C 盘数据目录**。整个数据目录可删 ~5 GB |
| **TRAE SOLO CN 数据** | `%APPDATA%\TRAE SOLO CN` | 3.5 GB | 同上。`ModularData\ai-agent\vm\tools` 是 AI agent 运行时（3.4 GB），删了重下。整体可删 |
| **Trae 安装本体** | `D:\Trae CN`（D 盘） | 1.2 GB | 官方卸载器 `unins000.exe`。**用户明确保留，不删** |

## Confirm Targets（需用户确认）

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|------|------|
| **当前 NVIDIA DXCache** | `NVIDIA\DXCache\` 中当前驱动前缀的文件 | 几百 MB~数 GB | 着色器编译缓存，删除后游戏需要重新编译 shader，用 `clean_deep.py` 扫描确定 |
| **剪映缓存** | `%LOCALAPPDATA%\JianyingPro` | 1~5 GB | 视频编辑缓存。**仅可清 `Cache/` 和 `CEF/Cache/`**。`ComponentStore/`（ONNX Runtime, ~1.7GB）、`SupplysStore/`（ASR 模型, ~1.1GB）是运行时依赖，不是缓存 |
| **Steam 下载缓存** | `%LOCALAPPDATA%\Steam` | 0.5~10+ GB | 游戏下载缓存，删除 Steam 需重新验证 |
| **Edge 数据** | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default` | 0.5~2 GB | 浏览器数据。通过 Edge 内置清理更安全（保留 Login Data/Profile） |
| **EBWebView 残留** | `%LOCALAPPDATA%\EBWebView` | ~100~150 MB | Electron 嵌入式浏览器残留文件，是缓存不是数据 |
| **CalabiYau 缓存** | `%LOCALAPPDATA%\CalabiYau\cache` + `QtWebEngine` | ~44 MB | 应用缓存 + 内嵌浏览器缓存。`Saved/` 是用户数据不碰 |
| **GenerativeGame 崩溃日志** | `%LOCALAPPDATA%\GenerativeGame\.sentry-native` | ~0.5 MB | 崩溃日志，可删。`Saved/` 是用户数据不碰 |
| **Doubao 缓存系列** | `%LOCALAPPDATA%\Doubao\User Data\Default\` 下 `Cache`/`Code Cache`/`GPUCache`/`Service Worker`/`DawnGraphiteCache` | ~100 MB | Chromium 缓存可重建。⚠ `IndexedDB` 是聊天记录（~1.1 GB）NoTouch |
| **DriverStore 旧 NVIDIA 驱动** | `C:\Windows\System32\DriverStore\FileRepository\nvami.inf_amd64_*` | 2.6 GB/份 | 新旧驱动镜像各一份。旧版本用 `clean_driverstore.py` 删除（底层 pnputil，普通权限即可）。⚠ 若报 "devices are presently installed" 是引用计数未清，重启再试，勿用 `/force`。**⚠ 清之前先想清楚旧驱动的用途**（见下） |
| **NVIDIA App OTA缓存（旧版）** | `C:\ProgramData\NVIDIA Corporation\NVIDIA app\UpdateFramework\ota-artifacts\grd\post-processing\` 中**低于当前版本的 GUID 子目录** | 2~4 GB/个 | 通过 inf 内 `DriverVer` 判断版本（如 `32.0.16.1074`），低于当前驱动版本的可删。**⚠ 先杀 NVIDIA 进程再删** |
| **NVIDIA App OTA缓存（当前版）** | 同上，但版本匹配当前驱动 | 2~4 GB | 可留作修复/回滚缓存，也可删（删了 App 下次更新会重新下载）。**⚠ 先杀进程** |

## NoTouch（绝对不碰）

这些是运行时组件或用户数据，不是缓存，不能清理。

| 路径 | 说明 | 典型大小 |
|------|------|----------|
| `%LOCALAPPDATA%\JianyingPro\User Data\ComponentStore\onnxruntime_gpu` | 剪映 AI 推理引擎（ONNX Runtime GPU），清掉剪映 AI 功能不可用 | ~1.7 GB |
| `%LOCALAPPDATA%\JianyingPro\User Data\SupplysStore\local-asr-supplies` | 剪映本地语音识别模型，清掉字幕功能需重新下载 | ~1.1 GB |
| `%LOCALAPPDATA%\Doubao\User Data\Default\IndexedDB` | 豆包聊天记录存储 | ~1.1 GB |
| `%LOCALAPPDATA%\Programs\Python` | Python/ML 运行环境 | |
| `%LOCALAPPDATA%\RimSort\instances` | RimWorld 模组实例数据 | |
| `%LOCALAPPDATA%\Tencent\QQGuild` | QQ 频道客户端数据 | |
| `%LOCALAPPDATA%\Packages` | Windows Store UWP 系统目录 | |
| `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA app` | NVIDIA 控制面板数据 | |
| `C:\Program Files\Adobe\*` | Adobe 全套（AE/PR/AU/PS），视频剪辑吃饭工具 | ~11 GB |
| `C:\Program Files\Microsoft Office*` | Office，工作必需 | ~5 GB |
| `~/.qclaw/memory/lossless/` | QClaw 工作区上下文记忆，删了对话历史丢失 | ~600 MB |
| `~/.qclaw/workspace-agent-*` | 各 agent 工作区文件 | 各 ~10-50 MB |

## C 盘警戒值

- C 盘 < 5 GB → 建议用户清理，但可继续工作
- C 盘 < 2 GB → 停止写入，优先报告

## 清理历史记录格式

每次清理追加到 `reference.md` 清理历史表：

```
| YYYY-MM-DD | 清理前 | 清理后 | 释放 | 主要来源 |
```
