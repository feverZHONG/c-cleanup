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
| `scripts/clean_safe.py` | 安全清理：updater + 旧DXCache + Temp + ima + NEO + GameViewer + OfficePLUS |
| `scripts/clean_conservative.py` | 保守清理：Edge缓存 + PowerToys + Steam + Doubao + bililive |
| `scripts/clean_deep.py` | 深度清理：当前 DXCache（`--force` 才删） |
| `scripts/clean_winupdate.py` | Windows Update 缓存（`--force` 才删，需管理员） |
| `scripts/scan_appdata.py` | 扫描 AppData\Local 大户 |
| `targets.md` | 清理目标分级表（Safe / Confirm） |
| `reference.md` | 脚本详情 + 大户参考表 + Windows Update 参考 + 清理历史 |

## 执行流程

1. **先读 `targets.md`** - 确认要清哪些、是否需要用户确认
2. **再执行对应脚本** - `python scripts/<脚本名>.py`
3. **清理后记录** - 追加到 `reference.md` 的清理历史表

---

*本技能按需加载子文件，安全清理是最高优先级。*
