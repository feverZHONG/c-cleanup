# c-cleanup 迭代升级计划 v0.2

> 计划文档，不纳入 Git 版本管理。下次开工直接翻这页。
>
> 编制：莉娅 · 2026-05-25

---

## 一、总体路线

稳定 > 自动 > 可视。基础修完了，下一步让这工具学会自己判断。

```
v0.1  (done)  基础脚本 + 安全/保守/深度三档
v0.15 (done)  去重、自动检测、文档同步
v0.2  (done)  统一入口 + --dry-run/--log
v0.3  (next)  自动决策 + 数据可视化
v0.4  (maybe) 交互模式
```

---

## 二、v0.3 目标

### P0 — `--auto` 智能推荐

```bash
python scripts/clean.py --auto
```

根据 C 盘剩余空间自动决策执行等级：

| 剩余空间 | 动作 | 是否提示 |
|---------|------|---------|
| > 10 GB | 安全清理 | 不提示，直接跑 |
| 5~10 GB | 安全 + 保守 | 不提示，直接跑 |
| 2~5 GB | 安全 + 保守 | 提示「是否深度清理」|
| < 2 GB | 全部 + WinUpdate | 建议管理员权限 + 停止写入 |

**实现思路：**
- `clean.py` 新增 `--auto` 参数
- 先调 `get_c_drive_free()` 获取当前空间
- 按阈值决策要跑哪些子脚本
- `--auto` 时自动加 `--log`

**更激进的优化：** `--auto` 可以跨 `--log` 的历史记录取参考——上次安全清理释放了 2.7 GB，现在又不到 10 GB 了，说明生成速度和上次差不多，可以加一句「上次清理后约 X 天再次触发」的趋势提示。

### P1 — `--report` 空间报告

```bash
python scripts/clean.py --report          # 终端输出
python scripts/clean.py --report --file   # 输出到文件 C_drive_report.md
```

一份完整的快照报告，包含：

```
# C 盘空间报告 · 2026-05-25

## 概览
总容量    237 GB
已使用    228 GB (96%)
剩余       9.0 GB

## 大目录 Top 10 (AppData\Local)
| 目录 | 大小 | 可清理 | 建议 |
|------|------|--------|------|
| Steam | 3.2 GB | 1.2 GB | --level conservative |
| Microsoft\Edge| 2.1 GB | 0.5 GB | --level conservative |
| Temp | 1.8 GB | 1.8 GB | ✅ --level safe |

## 可释放潜力估算
- 安全清理    ~2.5 GB (直接释放)
- 保守清理    ~1.2 GB (缓存类)
- 深度清理    ~0.8 GB (需重建)

## 上次清理
2026-05-25 · 安全清理 · 释放 2.7 GB
C 盘从 6.5 GB → 9.2 GB
```

**实现思路：**
- 新建 `scripts/report.py`（也可以集成进 `clean.py`）
- 扫描逻辑复用 `get_c_drive_info()` 和 `scan_appdata.py` 的迭代 walk
- 可释放潜力估算 = 各脚本 `--dry-run` 结果的汇总（调用子进程或函数复用）
- `--file` 参数输出到 `scripts/` 目录，可重复覆盖

### P2 — 追加清理目标

| 目标 | 说明 | 等级 |
|------|------|------|
| `C:\Windows\Temp` | 系统临时文件（需管理员） | 保守 | 
| `C:\Temp` | 某些软件遗留 | 安全 |
| 微信/QQ 缓存 | `%USERPROFILE%\Documents\WeChat Files` | 保守（需确认） |
| 旧 Windows 安装 | `C:\Windows.old`（需管理员 + disk cleanup） | 深度 |

**注意：** 微信/QQ 缓存按文件夹算，用户文件不能碰，但部分可大幅释放。

---

## 三、技术考量

### 代码结构

```
scripts/
├── clean.py               # 统一入口（已有）
├── clean_safe.py          # 安全清理（已有，--dry-run/--log）
├── clean_conservative.py  # 保守清理（已有，--dry-run/--log）
├── clean_deep.py          # 深度清理（已有）
├── clean_winupdate.py     # Windows Update（已有）
├── status.py              # 状态查看（已有）
├── scan_appdata.py        # AppData 扫描（已有）
├── report.py              # 空间报告（新建，v0.3）
├── utils.py               # 共享工具（已有）
├── cleanup_history.md     # 清理记录（已有）
└── planner.py             # --auto 的决策引擎（新建，v0.3）
```

### planner.py 核心逻辑草案

```python
THRESHOLDS = {
    "critical": 2e9,    # 2 GB
    "warning":  5e9,    # 5 GB
    "normal":   10e9,   # 10 GB
}

def plan(free_bytes):
    """根据剩余空间返回推荐清理方案。"""
    if free_bytes < THRESHOLDS["critical"]:
        return {
            "level": "all",
            "force_deep": True,
            "hint_admin": True,
            "message": "C 盘不足 2 GB，建议立即全量清理",
        }
    elif free_bytes < THRESHOLDS["warning"]:
        return {
            "level": "all",
            "force_deep": False,
            "hint_admin": False,
            "message": "C 盘不足 5 GB，推荐安全+保守清理",
        }
    elif free_bytes < THRESHOLDS["normal"]:
        return {
            "level": "safe",
            "force_deep": False,
            "hint_admin": False,
            "message": "C 盘空间充裕，执行日常安全清理",
        }
    else:
        return None  # 不需要清理
```

---

## 四、不纳入版本管理的说明

本文件（`PLAN.md`）不进入 Git。

其余文档文件（`README.md`、`reference.md`、`targets.md`、`SKILL.md`）全部在 Git 内，
每次功能更新必须同步文档再提交。

---

## 五、后续可能方向

- `--interactive` 交互模式：checkbox 选择清理项（依赖外部库？还是纯 CLI 逐条确认？）
- 定时任务集成：配合 cron 每周自动 `--auto --log`
- 生成 HTML 报告（带图表，适合发给其他人看）
- 跨磁盘扫描（D 盘、E 盘也能用类似逻辑清缓存）
