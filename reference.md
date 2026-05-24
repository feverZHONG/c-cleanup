# C 盘清理参考

## 脚本速查

| 脚本 | 用途 | 运行方式 |
|------|------|----------|
| `python scripts/status.py` | 查看 C 盘空间 | 直接运行 |
| `python scripts/scan_appdata.py` | 扫描 AppData\Local >100MB 目录 | 直接运行 |
| `python scripts/clean_safe.py` | 安全清理（updater/Temp/旧DXCache/ima/NEO/GameViewer/OfficePLUS） | 直接运行 |
| `python scripts/clean_conservative.py` | 保守清理（Edge缓存/PowerToys/Steam/Doubao/bililive） | 直接运行 |
| `python scripts/clean_deep.py` | 深度清理（当前DXCache） | 默认只读；`--force` 才删 |
| `python scripts/clean_winupdate.py` | Windows Update 缓存 | `--force` 才删（需管理员） |

---

## 脚本详情

### 安全清理 clean_safe.py

覆盖目标：updater 缓存（`@*`、`*-updater` 等）+ `C:\temp_ts_merge` + 旧 DXCache（历史驱动前缀）+ Temp + pip/npm 缓存 + ima.copilot + NEO 编译器缓存 + GameViewer webviewcache + OfficePLUS WebView2

Temp 清理采用分批暂停的温和模式，遇锁文件自动跳过。

### 保守清理 clean_conservative.py

覆盖目标：PowerToys Updates + Edge Cache/Code Cache/Service Worker + D3DSCache + npm-cache + Steam htmlcache + bililive + Doubao（update_downloads + Code Cache）

仅清缓存目录，不动 Login Data/Profile 等配置。

### 深度清理 clean_deep.py

| 模式 | 命令 | 说明 |
|------|------|------|
| 只读扫描 | `python scripts/clean_deep.py` | 扫描当前 DXCache 分布，列出大文件 |
| 真正执行 | `python scripts/clean_deep.py --force` | 删除当前驱动着色器缓存 |

首次使用时先运行扫描模式确认当前驱动前缀。
**风险：** 游戏 shader 会重新编译，首次加载变慢（几分钟到几十分钟不等），对稳定性无影响。

### Windows Update 清理 clean_winupdate.py

| 模式 | 命令 | 说明 |
|------|------|------|
| 只读扫描 | `python scripts/clean_winupdate.py` | 查看缓存大小 |
| 真正执行 | `python scripts/clean_winupdate.py --force` | 停服务 → 清理 → 启服务 |

需以管理员身份运行。

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

| 日期 | 清理前 | 清理后 | 释放 | 主要来源 |
|------|--------|--------|------|----------|

## C 盘告警阈值

- **< 5 GB** → 报告用户，建议清理
- **< 2 GB** → 停止写入，优先清理
