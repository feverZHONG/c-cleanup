"""C盘深度清理 — 当前 NVIDIA DXCache（当前驱动着色器缓存）
⚠️ 默认只扫描不删除，需要传 --force 参数才会真正执行。"""
import os, shutil, ctypes, sys, io
# Force UTF-8 output to avoid GBK console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def human(sz):
    if sz > 1e9: return f"{sz/1e9:.2f} GB"
    if sz > 1e6: return f"{sz/1e6:.0f} MB"
    return f"{sz/1e3:.0f} KB"

localappdata = os.path.expandvars("%LOCALAPPDATA%")
dxcache = os.path.join(localappdata, "NVIDIA", "DXCache")

# 先用 nvidia-smi 确认驱动版本
try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                       capture_output=True, text=True, timeout=10)
    ver = r.stdout.strip()
    if ver:
        print(f"NVIDIA 驱动版本: {ver}")
except:
    print("无法获取 NVIDIA 驱动版本（nvidia-smi 不可用）")

# 扫描 DXCache
files = []
if os.path.isdir(dxcache):
    with os.scandir(dxcache) as it:
        for entry in it:
            if entry.is_file():
                files.append((entry.name, entry.stat().st_size, entry.stat().st_mtime))

# 按前缀分组
prefixes = {}
for name, sz, mtime in files:
    p = name[:8]
    if p not in prefixes:
        prefixes[p] = {"size": 0, "count": 0, "newest": 0}
    prefixes[p]["size"] += sz
    prefixes[p]["count"] += 1
    if mtime > prefixes[p]["newest"]:
        prefixes[p]["newest"] = mtime

# 自动检测当前驱动前缀：最新修改时间的前缀
import datetime
current_prefix = max(prefixes, key=lambda p: prefixes[p]["newest"]) if prefixes else ""

print(f"DXCache 文件分布 (当前前缀: {current_prefix}):")
for p, info in sorted(prefixes.items(), key=lambda x: -x[1]["size"]):
    dt = datetime.datetime.fromtimestamp(info["newest"]).strftime("%m-%d %H:%M")
    tag = " <<< 当前" if p == current_prefix else ""
    print(f"  {p}: {human(info['size'])} ({info['count']} files, newest: {dt}){tag}")

print()
current_files = [(n, s) for n, s in files if n.startswith(current_prefix)]
total_current = sum(s for _, s in current_files)
print(f"当前驱动 ({current_prefix}) 文件数: {len(current_files)}, 总计: {human(total_current)}")

if current_files:
    print()
    print("前 10 大文件:")
    for name, sz in sorted(current_files, key=lambda x: -x[1])[:10]:
        print(f"  {human(sz):>10}  {name}")

print()
if "--force" in sys.argv:
    # 真正清理
    print("⚠️  --force 已传，开始删除当前驱动 DXCache...")
    deleted = 0
    for name, sz in current_files:
        try:
            os.remove(os.path.join(dxcache, name))
            deleted += sz
        except Exception as e:
            print(f"  删除失败: {name}: {e}")
    print(f"  删除完成: {human(deleted)}")
else:
    print("[WARN] 这是只读扫描模式。要真正删除当前驱动 DXCache，请执行:")
    print(f"   python scripts/clean_deep.py --force")
    print()
    print("  风险: 游戏 shader 会重新编译，首次加载会变慢（几分钟到几十分钟不等）")
    print("  对稳定性无影响。")

# 清理后状态
free = ctypes.c_ulonglong(0)
total = ctypes.c_ulonglong(0)
ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))
print(f"\nC 盘剩余: {free.value/1e9:.1f} GB")
