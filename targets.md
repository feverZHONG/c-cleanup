# 清理目标分级表

## Safe Targets（可直接清理，无需确认）

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|----------|------|
| **Updater 缓存** | `AppData\Local\` 下以 `*-updater` 或 `@*` 的文件夹 | 0.1~3 GB | 各类软件的更新缓存，删除自动重建 |
| **C 盘根目录临时文件** | `C:\temp_ts_merge` | 0.1~1 GB | TS 下载临时碎片，视频下完即可删除 |
| **旧 NVIDIA 驱动缓存** | `NVIDIA\DXCache\` 中非当前驱动前缀的文件 | 几十 MB~数 GB | 不同前缀=不同驱动版本。非当前前缀可直接删除。当前前缀通过 `clean_deep.py` 扫描确定 |
| **用户 Temp** | `%TEMP%` | 几十~几百 MB | 临时文件，无实际用途 |
| **npm/pip 缓存** | `%LOCALAPPDATA%\pip\cache`、`%LOCALAPPDATA%\npm-cache` | 几十~几百 MB | 删除下次安装重新下载 |
| **Steam htmlcache** | `%LOCALAPPDATA%\Steam\htmlcache` | 200~300 MB | Steam 内置浏览器缓存，无害 |
| **bililive** | `%LOCALAPPDATA%\bililive` | 100~200 MB | B站直播缓存 |
| **ima.copilot 缓存** | `%LOCALAPPDATA%\ima.copilot` | 600~700 MB | IMA 知识库客户端缓存，删除自动重建 |
| **NEO 着色器缓存** | `%LOCALAPPDATA%\NEO\neo_compiler_cache` | ~200 MB | OpenCL 着色器编译缓存（.cl_cache），删除下次运行自动重建 |
| **GameViewer webviewcache** | `%LOCALAPPDATA%\GameViewer\webviewcache` | ~125 MB | 网页视图缓存，可安全删除 |
| **OfficePLUS WebView2** | `%LOCALAPPDATA%\OfficePLUS\webview2` | ~130 MB | OfficePLUS 的 WebView2 缓存，可安全删除 |

## Confirm Targets（需用户确认）

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|------|------|
| **当前 NVIDIA DXCache** | `NVIDIA\DXCache\` 中当前驱动前缀的文件 | 几百 MB~数 GB | 着色器编译缓存，删除后游戏需要重新编译 shader，用 `clean_deep.py` 扫描确定 |
| **剪映缓存** | `%LOCALAPPDATA%\JianyingPro` | 1~5 GB | 视频编辑缓存。**仅可清 `Cache/` 和 `CEF/Cache/`**。`ComponentStore/`（ONNX Runtime, ~1.7GB）、`SupplysStore/`（ASR 模型, ~1.1GB）是运行时依赖，不是缓存 |
| **Steam 下载缓存** | `%LOCALAPPDATA%\Steam` | 0.5~10+ GB | 游戏下载缓存，删除 Steam 需重新验证 |
| **Edge 数据** | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default` | 0.5~2 GB | 浏览器数据。通过 Edge 内置清理更安全（保留 Login Data/Profile） |
| **EBWebView 残留** | `%LOCALAPPDATA%\EBWebView` | ~100~150 MB | Electron 嵌入式浏览器残留文件，是缓存不是数据 |

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
