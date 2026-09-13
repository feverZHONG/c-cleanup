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
| `scripts/clean_admin.ps1` | **⭐ 提权批处理**：Nsight×2 + Installer2 + WinUpdate 缓存（`-DriverStore` 带上旧驱动）。需阁下在管理员 PowerShell 里跑 |
| `scripts/scan_appdata.py` | 扫描 AppData\Local 大户 |
| `targets.md` | 清理目标分级表（Safe / Confirm / NoTouch） |
| `reference.md` | 脚本详情 + 大户参考表 + Windows Update 参考 + 清理历史 |

## 执行流程

1. **先读 `targets.md`** - 确认要清哪些、是否需要用户确认
2. **推荐使用统一入口** - `python scripts/clean.py --level safe|conservative|all`
   也支持 `--dry-run`（预览）和 `--log`（记录到清理历史）
3. **或直接执行对应脚本** - `python scripts/<脚本名>.py`
4. **提权目标单独走一步** - `C:\Program Files\*` 和 `C:\Windows\*` 下的目标普通会话删不掉，
   交给阁下在**管理员 PowerShell** 里跑 `scripts/clean_admin.ps1`（Hermes 里自动提权会被 UAC 取消）

---

## ⚠️ 踩过的坑

### 自动提权会失败

Hermes 会话里 `Start-Process powershell -Verb RunAs` 会报 **"The operation was canceled by the user"**（UAC 弹窗被取消），
且 `-Verb RunAs` 与 `-RedirectStandardOutput` 参数集冲突（`AmbiguousParameterSet`）。
**结论：不要尝试自动提权**，直接输出 `clean_admin.ps1` 的命令让阁下手动跑。

### `.ps1` 必须存为 UTF-8 **with BOM**

PS 5.1 读无 BOM 的 `.ps1` 会按 GBK 解码，中文注释里的多字节序列会把引号/大括号吃掉 →
报一堆 `Array index expression is missing`、`Missing closing '}'`，但报错行号跟真正的问题无关。
本技能目录下的 `clean_admin.ps1` 已存为 UTF-8 with BOM。新建 `.ps1` 记得同样处理：

```powershell
$c=[IO.File]::ReadAllText($p,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($p,$c,[Text.UTF8Encoding]::new($true))
```

> 注意：这条只适用于 `.ps1`。**YAML frontmatter / Markdown 反而不能有 BOM**（见 `writing-standards` 的 bom-encoding-pitfall.md）。

---

*本技能按需加载子文件，安全清理是最高优先级。*
