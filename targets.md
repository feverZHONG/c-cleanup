# 清理目标分级

## Safe Targets（可直接清理，无需确认）

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|----------|------|
| **Updater 缓存** | `AppData\Local\` 下所有 `*-updater` 和 `@*` 文件夹 | 0.1~3 GB | 各软件的更新缓存，删后自动重建 |
| **C 盘根目录残留** | `C:\temp_ts_merge` | 0.1~1 GB | TS 下载残留片段，可疑视频下载中断留下 |
| **旧 NVIDIA 驱动缓存** | `NVIDIA\DXCache\` 中非当前驱动前缀的文件 | 几十 MB~数 GB | 不同前缀=不同驱动版本，旧前缀可直接删。当前驱动前缀通过 `clean_deep.py` 扫描确认 |
| **用户 Temp** | `%TEMP%` | 几十~几百 MB | 临时文件，无实际用途 |
| **npm/pip 缓存** | `%LOCALAPPDATA%\pip\cache`、`%LOCALAPPDATA%\npm-cache` | 几十~几百 MB | 删除后下次安装会重新下载 |
| **Steam htmlcache** | `%LOCALAPPDATA%\Steam\htmlcache` | 200~300 MB | Steam 内置浏览器缓存，无害 |
| **bililive** | `%LOCALAPPDATA%\bililive` | 100~200 MB | B站直播缓存 |
| **ima.copilot 缓存** | `%LOCALAPPDATA%\ima.copilot` | 600~700 MB | IMA 知识库客户端缓存，用户确认后可清 |
| **NEO 编译器缓存** | `%LOCALAPPDATA%\NEO\neo_compiler_cache` | ~200 MB | OpenCL 着色器编译缓存（.cl_cache），删后下次启动重建 |
| **GameViewer webviewcache** | `%LOCALAPPDATA%\GameViewer\webviewcache` | ~125 MB | 网页视图缓存，可安全清 |
| **OfficePLUS WebView2** | `%LOCALAPPDATA%\OfficePLUS\webview2` | ~130 MB | OfficePLUS 插件 WebView2 缓存，可安全清 |

## Confirm Targets（需用户确认）

| 目标 | 路径 | 典型大小 | 说明 |
|------|------|------|------|
| **当前 NVIDIA DXCache** | `NVIDIA\DXCache\` 中当前驱动前缀的文件 | 几百 MB~数 GB | 着色器编译缓存，删除后游戏需重新编译 shader。运行 `clean_deep.py` 扫描确认 |
| **剪映项目缓存** | `%LOCALAPPDATA%\JianyingPro` | 1~5 GB | 视频编辑缓存，可删但项目工程文件需保留 |
| **Steam 下载缓存** | `%LOCALAPPDATA%\Steam` | 0.5~10+ GB | 游戏更新缓存，删后 Steam 会重新验证 |
| **Edge 缓存** | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default` | 0.5~2 GB | 浏览器缓存。建议通过 Edge 内置设置清理，不动 Login Data/Profile |
| **浏览器衍生缓存** | `%LOCALAPPDATA%\EBWebView` | ~100~150 MB | Electron 嵌入式浏览器框架程序文件，非缓存不可清 |

## 不可删参考

以下为常见大目录但属于程序文件或用户数据，不可清理：

| 路径 | 说明 |
|------|------|
| `%LOCALAPPDATA%\Programs\Python` | Python/ML 开发环境 |
| `%LOCALAPPDATA%\Doubao\User Data\Default\IndexedDB` | 豆包聊天记录 |
| `%LOCALAPPDATA%\RimSort\instances` | RimWorld 模组实例数据 |
| `%LOCALAPPDATA%\Tencent\QQGuild` | QQ 频道客户端程序 |
| `%LOCALAPPDATA%\Packages` | Windows Store UWP 系统包 |
| `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA app` | NVIDIA 控制面板程序 |

## C 盘警告阈值

- C 盘 < 5 GB → 报告用户，建议清理
- C 盘 < 2 GB → 停止写入，优先清理

## 清理记录格式

每次清理后追加到 `reference.md` 的清理历史表：

```
| YYYY-MM-DD | 清理前 | 清理后 | 释放 | 主要来源 |
```
