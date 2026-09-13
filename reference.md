# C 盘清理参考

## 脚本速查

| 脚本 | 用途 | 运行方式 |
|------|------|----------|
| `python scripts/clean.py` | 🏆 统一入口，推荐使用 | `--level safe`（默认）<br>`--level conservative`<br>`--level all`<br>`--level deep` |
| `python scripts/status.py` | 查看 C 盘空间 | 直接运行 |
| `python scripts/scan_appdata.py` | 扫描 AppData\Local >100MB 目录 | 直接运行 |
| `python scripts/clean_safe.py` | 安全清理（updater/Temp/旧DXCache/ima/NEO/GameViewer/OfficePLUS） | 直接运行<br>`--dry-run` 预览<br>`--log` 记录 |
| `python scripts/clean_conservative.py` | 保守清理（Edge缓存/PowerToys/Steam/Doubao/bililive） | 直接运行<br>`--dry-run` 预览<br>`--log` 记录 |
| `python scripts/clean_deep.py` | 深度清理（当前DXCache） | 默认只读；`--force` 才删 |
| `python scripts/clean_winupdate.py` | Windows Update 缓存 | `--force` 才删（需管理员） |

---

## 统一入口 clean.py（推荐）

整合安全清理、保守清理、深度清理。单命令覆盖多数场景。

| 命令 | 说明 |
|------|------|
| `python scripts/clean.py` | 安全清理（默认） |
| `python scripts/clean.py --level conservative` | 保守清理 |
| `python scripts/clean.py --level all` | 安全 + 保守 |
| `python scripts/clean.py --level all --dry-run` | 预览全部可释放空间 |
| `python scripts/clean.py --level all --log` | 安全+保守并记录到清理历史 |
| `python scripts/clean.py --level deep --force` | 执行深度清理 |

**所有子脚本支持的参数也适用于 clean.py**（`--dry-run`/`--log`/`--force` 自动透传）。

---

## 脚本详情

### 安全清理 clean_safe.py

覆盖目标：updater 缓存（`@*`、`*-updater` 等）+ `C:\temp_ts_merge` + 旧 DXCache（自动检测，排除当前驱动前缀）+ Temp + pip/npm 缓存 + ima.copilot + NEO 编译器缓存 + GameViewer webviewcache + OfficePLUS WebView2

| 参数 | 说明 |
|------|------|
| （无参数） | 正常执行删除 |
| `--dry-run` | 预览模式：只扫描报告将释放空间，不执行删除 |
| `--log` | 清理后自动追加记录到 `scripts/cleanup_history.md` |

Temp 清理采用分批暂停的温和模式，遇锁文件自动跳过。

### 保守清理 clean_conservative.py

覆盖目标：PowerToys Updates + Edge Cache/Code Cache/Service Worker + D3DSCache + npm-cache + Steam htmlcache + bililive + Doubao（update_downloads + Code Cache）

| 参数 | 说明 |
|------|------|
| （无参数） | 正常执行删除 |
| `--dry-run` | 预览模式：只扫描报告将释放空间，不执行删除 |
| `--log` | 清理后自动追加记录到 `scripts/cleanup_history.md` |

仅清缓存目录，不动 Login Data/Profile 等配置。

### 深度清理 clean_deep.py

| 模式 | 命令 | 说明 |
|------|------|------|
| 只读扫描 | `python scripts/clean_deep.py` | 扫描当前 DXCache 分布，列出大文件 |
| 真正执行 | `python scripts/clean_deep.py --force` | 删除当前驱动着色器缓存 |

首次使用时先运行扫描模式确认当前驱动前缀。
**逻辑：** 自动检测最大大小的前缀为当前驱动（大小比时间更稳定）。
**风险：** 游戏 shader 会重新编译，首次加载变慢（几分钟到几十分钟不等），对稳定性无影响。

**占用文件坑（2026-08-05 实战）：** 有 GPU 进程运行时会删不掉部分 `.nvph` 文件（WinError 32 另一个程序正在使用此文件）。这是正常的，删除失败的会被跳过，其余正常释放。**重启后再跑一次 `--force` 就能清掉剩余的**，无需杀进程硬删。

### Windows Update 清理 clean_winupdate.py

| 模式 | 命令 | 说明 |
|------|------|------|
| 只读扫描 | `python scripts/clean_winupdate.py` | 查看缓存大小 |
| 真正执行 | `python scripts/clean_winupdate.py --force` | 停服务 → 清理 → 启服务 |

需以管理员身份运行。

**非管理员会话提权方法（2026-08-05 实战验证）：**
```powershell
$script = "D:\Hermes Agent CN Desktop\data\hermes-home\skills\c-cleanup\scripts\clean_winupdate.py"
$p = Start-Process python -ArgumentList "`"$script`" --force" -Verb RunAs -PassThru -Wait
# 会弹 UAC 确认框，用户点「是」后执行；ExitCode 0 = 成功
```
脚本自身检测到非管理员会退出并报错，所以必须提权跑。Windows Update 下载缓存（SoftwareDistribution\Download）可达 3~6 GB，**系统更新卡住/空间不足时优先清它**——它往往就是更新失败的元凶。

### 状态查看 status.py

快速查看 C 盘空间。同时显示 GB（十进制）和 GiB（二进制），解资源管理器与脚本数字不同的问题。

### AppData 扫描 scan_appdata.py

列出 `%LOCALAPPDATA%` 下所有 >100 MB 的目录 + 当前 C 盘空间，用于首次诊断。

---

## Windows Update 缓存参考

`C:\Windows\SoftwareDistribution\Download` 大小可达 3~6 GB。累积更新包可单个 4.5+ GB。

### 方案1：定期主动清理（推荐）

```python scripts/clean_winupdate.py
# 扫描：python scripts/clean_winupdate.py
# 清理：python scripts/clean_winupdate.py --force
```

### 方案2：mklink 转移目录（风险较高，不推荐新手）

需要管理员权限手动执行：
```
net stop wuauserv
move C:\Windows\SoftwareDistribution D:\WindowsUpdateCache
mklink /J C:\Windows\SoftwareDistribution D:\WindowsUpdateCache
net start wuauserv
```

---

## 清理历史

记录文件：`scripts/cleanup_history.md`

| 日期 | 类型 | 清理前 (GB) | 清理后 (GB) | 释放 (GB) |
|------|------|-------------|-------------|-----------|
| 2026-05-29 | 手动（NVIDIA App OTA crd+grd） | 0.11 | 10.95 | 10.87 |
| 2026-05-29 | 装完610.47后最终状态 | — | 7.75 | — |

使用 `--log` 参数执行清理时会自动追加记录。

---

## DriverStore 旧驱动：原本是干什么的（2026-08-25 补充）

**位置：** `C:\Windows\System32\DriverStore\FileRepository\`（Windows 驱动仓库，所有装过的驱动都留一份副本）

**旧驱动（如 oem131.inf ver=32.0.16.1074）的原本用途：**
1. **回滚保险**：当前驱动出问题时，设备管理器可以「回滚驱动程序」退回旧版——旧版在 DriverStore 里才有得回
2. **兼容冗余**：某些子设备/老硬件可能仍绑定旧驱动文件（这就是 pnputil 报 "One or more devices are presently installed" 的原因——引用计数未清，说明系统里还有组件在引用它）

**删了会怎样：**
- 当前驱动（如 610.88/oem246）完全不受影响
- 失去回滚到该旧版的能力（若旧版远早于当前版，回滚价值低）
- 若引用计数一直没清 → 说明系统确实还在用，别强删（勿用 /force）

**判断标准（先问再删）：**
- 用户是否靠 NVIDIA App 自动更新驱动、出问题直接装新版？→ 回滚保险价值低，可删
- 旧版与当前版差距大吗？差距大且稳定 → 可删
- 重启后引用计数是否已清？清了才删，没清就留着

**用户决定（2026-08-25）：** oem131 (32.0.16.1074) 被引用计数挡着 → **留着，不删**。用户原则：**没东西在沿用的话一般都能清；有引用就留着**。

---

## 实战记录：NVIDIA App OTA 缓存

**路径：** `C:\ProgramData\NVIDIA Corporation\NVIDIA app\UpdateFramework\ota-artifacts\grd\` + `crd\`

**典型大小：** 3~11 GB

**来源：** NVIDIA App 自动下载的新版驱动安装包（包括安装包 .exe 和提取后的 Display.Driver 等文件）。`grd` = Game Ready Driver 分支，`crd` = NSD（NVIDIA Studio Driver）分支。两个分支可能同时缓存同一版本的常规版和 NSD 版驱动。

**风险判断：**
- 文件名含版本号（如 `610.47-notebook-win10-win64-64bit-international-dch-whql-g.exe`）
- 通过 nvidia-smi 或 WMI Win32_VideoController 确认当前驱动版本
- 未安装的更新版 → 可直接删除
- 旧版（低于当前版本） → 可直接删除
- 当前版本缓存 → NVIDIA App 可能用于修复/增量升级，删除无害但 App 会重新下载

**⚠ 致命坑：** 先检查 NVIDIA App 没有正在进行的更新流程再删。如果 App 正在「准备安装」或「下载中」状态下删了缓存文件，App UI 会卡在安装界面报错（-505413605），安装流程无法恢复，只能手动重装驱动。**检查方法：** 看 NVIDIA App 窗口有没有进度条/安装提示，或直接杀掉进程再删。

**清理方式：** 杀掉 `NVIDIA App` / `nvcontainer` / `NVDisplay.Container` 进程后，直接删除 `crd/` 和 `grd/` 目录（整个 ota-artifacts 子目录），NVIDIA App 下次更新自动重建。用 `shutil.rmtree()`。**先杀进程再删，避免 App 卡住。**

**实战：2026-05-29**

**第一轮（翻车记录）：**
- `grd/`: 7.38 GB（596.49 当前驱动 + 610.47 新版本，两份完整驱动安装包）
- `crd/`: 3.73 GB（610.47 NSD Studio Driver + Display.Driver 散件）
- 没检查 NVIDIA App 状态就删了缓存，App 卡在安装界面，错误码 -505413605
- 杀了 NVIDIA 进程重启 App 也没用（状态已损毁）
- 最终结果：阁下手动从官网下载 610.47 装好

**最终状态：**
- 删 OTA 缓存 10.87 GB，安装新驱动后又占回一些
- C 盘从 0.11 GB → 7.75 GB
- 驱动从 596.49 → 610.47（跨分支升级：590→610）

## C 盘告警阈值

- **< 5 GB** → 报告用户，建议清理
- **< 2 GB** → 停止写入，优先清理
---

## 实战记录：2026-07-19（NVIDIA OTA 缓存版本检测 + Nsight 清理）

**场景：** C 盘 99%（1.86 GiB），需更新驱动

**发现：** C:\ProgramData\NVIDIA Corporation\NVIDIA app\UpdateFramework\ota-artifacts\grd\ 下缓存了两套完整驱动安装包：

| GUID | 版本号 | 对应驱动 | 大小 | 结论 |
|------|--------|---------|------|------|
| c7e7f7f193b666518aebfa5d488dcfe7 | 32.0.16.1047 | 610.47（旧版） | ~3.7 GB | 🗑️ 删 |
| 977ee8409ba720ac629bc9681b290220 | 32.0.16.1074 | 610.74（当前版） | ~3.0 GB | 可留/可删 |

**版本判断方法：** 每个 GUID 子目录下 Display.Driver\*.inf 文件中有字段 DriverVer = MM/DD/YYYY, 32.0.16.xxxx
- 版本号转换：32.0.16.1074 → 610.74（取后三位小数 + 首位）
- 用 
vidia-smi 或 (Get-WmiObject Win32_VideoController).DriverVersion 确认当前版本

**本次清理清单：**
- 旧版 OTA 缓存（c7e7f7f1, ~3.7 GB）→ 待删
- Nsight Compute（624 MB）→ 待删
- Nsight Systems（1,005 MB）→ 待删
- NVIDIA Installer2（302 MB）→ 待删
- 当前 DXCache（4.16 GB）→ 已删（反正更新驱动后失效）
- 剪映缓存（751 MB）→ 已删
- qclaw-updater（518 MB）→ 已删
- Temp + Edge 缓存 + npm-cache + 其他（367 MB）→ 已删

## 实战记录：2026-08-24（驱动 610.74→610.88 更新后清理）

**场景：** C 盘 99%（0.82 GiB），需更新驱动；更新完成后 C 盘又掉回 3.86 GB

**第一轮（更新前）：**
- 安全清理（旧 DXCache 1.61 GB + Temp 75 MB）→ 1.69 GB
- 当前 DXCache（--force，3.49 GB，9 个 .nvph 被占用跳过）→ 3.49 GB
- 剪映 Cache + CEF Cache → 0.17 GB
- pnpm-cache + D3DSCache + @deepseek-aidsh-desktop-updater → 0.67 GB
- 合计 6.0 GB → C 盘 7.13 GB，驱动安装成功

**第二轮（更新后，驱动 610.88）：**
- Installer2（320 MB）+ Nsight Compute（624 MB）+ Nsight Systems（1,005 MB）+ chatglm-updater（63 MB）→ 1.97 GB
- OTA 缓存 GUID 33571502（32.0.16.1088 当前版，2.91 GB）→ 已删（驱动已装完，留缓存无意义；删除前未在更新流程中）
- DriverStore 旧驱动 oem131.inf（nvami 32.0.16.1074，对应旧 610.74）→ **删除失败**：pnputil 报 "One or more devices are presently installed"，但 /enum-devices 里搜不到引用 → 疑似引用计数未清，**重启后再试 pnputil /delete-driver oem131.inf**（可释放 ~2.63 GB）
- Doubao Cache/Code Cache/GPUCache/Service Worker（~100 MB）+ CalabiYau cache/QtWebEngine（44 MB）+ GenerativeGame .sentry-native（0.5 MB）→ 0.14 GB
- 合计 5.02 GB → C 盘 7.19 GB

**待办：** 重启后删 oem131.inf（2.63 GB）；再跑一次 `python scripts/clean_deep.py --force` 清掉之前被占用的 9 个 .nvph

**C 盘结果：** 1.86 GiB → 7.31 GiB（+5.45 GB）

> **2026-07-19 补充：** Nsight Compute、Nsight Systems、Installer2 位于 C:\Program Files\NVIDIA Corporation\，删除需**管理员权限**。当前 Hermes 进程无管理员 token，无法删除。可手动在管理员终端执行：
>
> **2026-08-24 修正：** 上述结论过时——实测普通权限即可删除 Nsight Compute / Nsight Systems / Installer2（本天使直接在 Hermes 进程里 Remove-Item 成功，共 1.97 GB）。Program Files 下这些目录不需要管理员。若遇权限拒绝再提权。DriverStore 旧驱动（pnputil）同样普通权限可执行，障碍只有引用计数。
>
> **🔴 2026-09-12 再修正（推翻上一条）：** **必须管理员权限，普通会话绝对删不掉。** ACL 实测：
> ```
> BUILTIN\Administrators   FullControl                 Allow
> BUILTIN\Users            ReadAndExecute, Synchronize Allow   ← 只有读+执行
> Owner: NT AUTHORITY\SYSTEM
> ```
> 非提权会话下 `Remove-Item`、`Rename-Item` 一律报「对路径的访问被拒绝」，连目录里的单个 `EULA.txt` 都删不了。
> 8-24 那条「Remove-Item 成功」记录**不可复现**，别再信——今天的三个目录（Nsight Systems 1,005 MB / Nsight Compute 624 MB / Installer2 320 MB）
> 尺寸与 8-24 记录**完全一致地存在**，说明那次删除要么没生效、要么被后续驱动包重新解压覆盖（见下）。
> **正确做法：交给阁下的管理员 PowerShell 跑 `scripts/clean_admin.ps1`**（已封装 Nsight×2 + Installer2 + WinUpdate 缓存，`-DriverStore` 带上旧驱动，支持 `-DryRun`）。

## 实战记录：2026-09-12（驱动持续 610.88，OTA 新周期后清理）

**场景：** C 盘 99%（2.05 GiB），阁下要求检查并清理

**第一轮（普通权限，全部实删成功）：**

| 目标 | 释放 | 说明 |
|------|------|------|
| Temp | 871 MB | 3,365 项，18 项被占用跳过 |
| com.ugreen.desktop-updater | 213 MB | UGREEN NAS 客户端更新缓存 |
| Edge Cache + Code Cache + Service Worker | 434 MB | |
| Doubao Cache + Code Cache + GPUCache + SW + DawnGraphite | 285 MB | IndexedDB（聊天记录）未碰 |
| 旧 DXCache（fc52a938 以外的 3 个前缀） | 2 MB | |
| Steam htmlcache | 21 MB | |
| **当前 DXCache（`clean_deep.py --force`）** | **2.17 GB** | 67 个 .nvph；7 个被占用跳过（含 2.15 GB 那个大文件已删） |
| CrashDumps（手动清，已补进 `clean_safe.py`） | 204 MB | 崩溃转储 |

**第二轮（需管理员，未执行 —— 交给阁下跑 `clean_admin.ps1`）：**

| 目标 | 待释放 | 说明 |
|------|--------|------|
| Nsight Systems 2022.4.2 | 1,005 MB | CUDA 调试工具，剪辑用户用不到 |
| Nsight Compute 2022.3.0 | 624 MB | 同上 |
| NVIDIA Installer2 | 320 MB | 安装器残留 |
| Windows Update 下载缓存 | 681 MB | SoftwareDistribution\Download |
| **小计** | **≈ 2.6 GB** | |
| DriverStore oem131.inf（32.0.16.1074，旧 610.74） | 2.63 GB | 需 `-DriverStore`；注意 8-24 曾报 pnputil 引用计数未清 |

**C 盘结果：** 2.05 GiB → 5.41 GiB（**+3.36 GB**，纯普通权限部分）

**⚠ 新发现 · 驱动包会自己回来：** OTA 缓存出现**新的 GUID `420b76ed491bc58a93b21a298a235674`**（`ota-artifacts\nvapp\post-processing\` 699 MB + `nvapp\` 175 MB，
共 874 MB，属当前版本 32.0.16.1088）。这说明 610.88 之后 NVIDIA App 又走过一次更新/修复流程，
**驱动包重新解压会把 `Program Files\NVIDIA Corporation\` 下的 Nsight/Installer2 一起装回来**——
所以这三个目录属于「清了还会再来」的目标，不值得逐次纠结，但要记得每次清完复查。

**其他观察：**
- `%LOCALAPPDATA%\SquirrelTemp` 已是空目录（KOOK 残留此前已清），已补进 `clean_safe.py` 作为常备目标
- `%LOCALAPPDATA%\JianyingPro\User Data` 2.89 GB 全部是 ComponentStore（ONNX Runtime 1,694 MB）+ SupplysStore（ASR 模型 1,124 MB）→ **NoTouch，正确跳过**
- `C:\ProgramData\NVIDIA\NGX` 1.28 GB = DLSS 模型，**NoTouch**
- `C:\ProgramData\Package Cache` 1.37 GB = VS/安装器缓存，删除有风险，未动
- `C:\Recovery` 6.43 GB = WinRE 镜像，**NoTouch**

**🆕 2026-09-12 新增工具：`scripts/clean_admin.ps1`**（已沙箱验证删除+报告逻辑）
```powershell
# 在管理员 PowerShell 里
powershell -NoProfile -ExecutionPolicy Bypass -File clean_admin.ps1 -DryRun      # 先预览
powershell -NoProfile -ExecutionPolicy Bypass -File clean_admin.ps1              # 实删
powershell -NoProfile -ExecutionPolicy Bypass -File clean_admin.ps1 -DriverStore # 带上旧驱动
```

