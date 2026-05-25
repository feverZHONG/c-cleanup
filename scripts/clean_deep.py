"""C盘深度清理 - 当前 NVIDIA DXCache (当前驱动着色器缓存)
默认只扫描不删除，需要传 --force 参数才会真正执行。"""
import os, sys, io
from utils import human, get_dxcache_prefixes, get_c_drive_free

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

localappdata = os.path.expandvars(r"%LOCALAPPDATA%")
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
    print("无法获取 NVIDIA 驱动版本 (nvidia-smi 不可用)")

# 扫描 DXCache
prefixes, current_prefix = get_dxcache_prefixes(dxcache)

print(f"DXCache 文件分布 (当前前缀: {current_prefix}):")
for p, info in sorted(prefixes.items(), key=lambda x: -x[1]["size"]):
    tag = " <<< 当前" if p == current_prefix else ""
    print(f"  {p}: {human(info['size'])} ({info['count']} files){tag}")

print()
if current_prefix:
    current_info = prefixes[current_prefix]
    print(f"当前驱动 ({current_prefix}) 文件数: {current_info['count']}, 总计: {human(current_info['size'])}")

    # 重新扫描当前前缀的大文件列表
    current_files = []
    if os.path.isdir(dxcache):
        with os.scandir(dxcache) as it:
            for entry in it:
                if entry.is_file() and entry.name.startswith(current_prefix):
                    current_files.append((entry.name, entry.stat().st_size))

    print()
    print("前 10 大文件:")
    for name, sz in sorted(current_files, key=lambda x: -x[1])[:10]:
        print(f"  {human(sz):>10}  {name}")

    print()
    if "--force" in sys.argv:
        print("--force 已传，开始删除当前驱动 DXCache...")
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
        print("   python scripts/clean_deep.py --force")
        print()
        print("  风险: 游戏 shader 会重新编译，首次加载会变慢 (几分钟到几十分钟不等)")
        print("  对稳定性无影响。")
else:
    print("DXCache 目录不存在或为空。")

free = get_c_drive_free()
print(f"\nC 盘剩余: {free/1e9:.1f} GB")
