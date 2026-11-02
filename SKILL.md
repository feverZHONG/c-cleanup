---
name: c-cleanup
description: C盘安全清理与空间回收技能。当用户提到清理C盘、释放空间、清理缓存、清理磁盘、C盘满了时触发。安全清理是最高优先级。
---

# C 盘安全清理技能

## ⚠️ 最高原则：安全清理

**绝不删除系统关键文件、不碰正在使用的程序数据、不执行未经确认的危险操作。**

- ✅ **安全删除**：临时文件、updater缓存、旧驱动缓存、可重新生成的缓存
- ⚠️ **需确认**：当前驱动缓存（会重建但耗时）、program files残留（需确认是否仍在使用）
- ❌ **绝对不碰**：系统文件、注册表、正在运行的程序数据、用户重要文件

---

## 文件索引

| 文件 | 内容 |
|------|------|
| `scripts/status.py` | C 盘空间快速查看 |
| `scripts/clean.py` | 统一入口，推荐使用（支持 `--dry-run`/`--log`/`--level`） |
| `scripts/clean_safe.py` | 安全清理：updater + 旧DXCache + Temp + ima + NEO + GameViewer + OfficePLUS |
| `scripts/clean_conservative.py` | 保守清理：Edge缓存 + PowerToys + Steam + Doubao + bililive |
| `scripts/clean_deep.py` | 深度清理：当前 DXCache（`--force` 才删） |
| `scripts/clean_winupdate.py` | Windows Update 缓存（`--force` 才删，需管理员） |
| `scripts/clean_driverstore.py` | DriverStore 旧 NVIDIA 驱动清理（扫描+`--force`，自动识别当前版本） |
| `scripts/clean_admin.ps1` | **⭐ 提权批处理**：Nsight×2 + Installer2 + WinUpdate 缓存（`-DriverStore` 走 pnputil，`-DriverStoreFiles` 走文件级直删）。需用户在管理员 PowerShell 里跑 |
| `scripts/scan_appdata.py` | 扫描 AppData\Local 大户 |
| `targets.md` | 清理目标分级表（Safe / Confirm / NoTouch） |
| `reference.md` | 脚本详情 + 大户参考表 + Windows Update 参考 + 清理历史 |
| `README.md` | 人/AI 双向说明书（比本文件更细的操作手册） |

---

## 文档导航（何时读哪个文件）

| 场景 | 先读 | 再读 |
|------|------|------|
| 任何清理前 | `targets.md`（分级表，确认 Safe / Confirm / NoTouch） | `reference.md`（对应脚本详情与参数） |
| 用户要预览/记录 | `reference.md` 脚本详情节 | 直接用 `clean.py --dry-run` / `--log` |
| 目标需管理员权限 | `targets.md` 提权说明节 | `clean_admin.ps1` 用法（见下方执行流程） |
| 驱动相关（DXCache / DriverStore / OTA 缓存） | `targets.md` Confirm / NoTouch 表 | `reference.md` 实战记录（含 2026-09-25 重要纠正） |
| 完全不懂怎么上手 | `README.md` | 本文件（索引 + 流程 + 坑） |

> 原则：**`targets.md` 是清理目标唯一权威**，脚本与之一一对应；改脚本必须同步 targets.md / reference.md / README（见「维护纪律」）。

---

## 执行流程

1. **先读 `targets.md`** - 确认要清哪些、是否需要用户确认（Safe 可直接清，Confirm 先问，NoTouch 不碰）
2. **推荐使用统一入口** - `python scripts/clean.py --level safe|conservative|all`
   也支持 `--dry-run`（预览）和 `--log`（记录到清理历史）
3. **或直接执行对应脚本** - `python scripts/<脚本名>.py`
4. **提权目标单独走一步** - `C:\Program Files\*` 和 `C:\Windows\*` 下的目标普通会话删不掉，
   交给用户在**管理员 PowerShell** 里跑 `scripts/clean_admin.ps1`（Hermes 里自动提权会被 UAC 取消）
   - 默认：Nsight×2 + Installer2 + Windows Update 缓存
   - `-DriverStoreFiles`：清 DriverStore 旧驱动（文件级直删，自动保留当前版本）
   - 先加 `-DryRun` 预览

---

## 安全纪律（与 targets.md 三档对应）

| 档位 | 含义 | 处理方式 |
|------|------|----------|
| **Safe** | 可直接清理，无需确认 | updater 缓存、Temp、旧驱动缓存、可再生成的浏览器缓存——直接跑对应脚本 |
| **Confirm** | 需用户确认 | 当前 DXCache（重建耗时）、DriverStore 旧驱动（失去回滚能力）、剪映/Steam/Doubao 缓存、OTA 缓存——**先 `--dry-run` 列出将释放量与代价，用户点头才 `--force`** |
| **NoTouch** | 绝对不碰 | 系统文件、注册表、运行中程序数据、用户文档、剪映 AI 模型（onnxruntime/ASR）、豆包 IndexedDB 聊天记录、QClaw 记忆——只报告不操作 |

**红线（无论用户怎么要求都不做）**：
- 不删 `System32` / `DriverStore` 当前驱动 / `Program Files` 本体 / `WinSxS`
- 不用 `pnputil /delete-driver /force`（会把设备搞成无驱动状态）
- 删 NVIDIA OTA 缓存前**先杀 NVIDIA 进程**（App 更新中删缓存会卡死在 -505413605）
- 剪映只清 `Cache/` 与 `CEF/Cache/`；`ComponentStore/`（ONNX Runtime）、`SupplysStore/`（ASR 模型）是运行时依赖不是缓存
- 用户没点名的 Confirm 项一律不清；「清理垃圾」等笼统表述不构成对 Confirm / NoTouch 的授权

---

## 维护纪律（每次改动必须遵守）

1. **功能更新必须同步文档再提交**：新增/修改脚本后，同步 targets.md（分级）、reference.md（详情）、README.md / README.en.md（一览表）——PLAN.md 同款约定，文档落后 = 提交不合格
2. **新增清理目标**：先评估三档归属（Safe / Confirm / NoTouch）再落 `targets.md`，同时把路径补进对应脚本（updater 硬编码列表记得手动加）
3. **参数/档位变化**：`clean.py --level` 的档位、各脚本 `--force`/`--dry-run`/`--log` 行为变化，必须同步 reference.md 速查表与 README 脚本一览
4. **SKILL.md 索引与 scripts/ 一一对应**：加脚本就加索引行，删脚本就删索引行
5. 新建 `.ps1` 存 UTF-8 with BOM；YAML frontmatter / Markdown 不要 BOM（见下方踩坑）

---

## ⚠️ 踩过的坑

### 自动提权会失败

Hermes 会话里 `Start-Process powershell -Verb RunAs` 会报 **"The operation was canceled by the user"**（UAC 弹窗被取消），
且 `-Verb RunAs` 与 `-RedirectStandardOutput` 参数集冲突（`AmbiguousParameterSet`）。
**结论：不要尝试自动提权**，直接输出 `clean_admin.ps1` 的命令让用户手动跑。

### `.ps1` 必须存为 UTF-8 **with BOM**

PS 5.1 读无 BOM 的 `.ps1` 会按 GBK 解码，中文注释里的多字节序列会把引号/大括号吃掉 →
报一堆 `Array index expression is missing`、`Missing closing '}'`，但报错行号跟真正的问题无关。
本技能目录下的 `clean_admin.ps1` 已存为 UTF-8 with BOM。新建 `.ps1` 记得同样处理：

```powershell
$c=[IO.File]::ReadAllText($p,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($p,$c,[Text.UTF8Encoding]::new($true))
```

> 注意：这条只适用于 `.ps1`。**YAML frontmatter / Markdown 反而不能有 BOM**（见 `writing-standards` 的 bom-encoding-pitfall.md）。

### 驱动包会自己回来（2026-09-12 实测）

NVIDIA App 每次走更新/修复流程，会把 `Program Files\NVIDIA Corporation\` 下的 Nsight / Installer2 **重新装回来**。
这三个目录属于「清了还会再来」的目标，清完记得复查，别以为一劳永逸。

---

*本技能按需加载子文件，安全清理是最高优先级。*
