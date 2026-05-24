"""C盘保守清理 — PowerToys Updates + Edge 缓存 + D3DSCache + npm-cache + Steam htmlcache + bililive + Doubao
适用于定期维护，不会破坏核心数据。"""
import os, shutil, ctypes, sys, io
# Force UTF-8 output to avoid GBK console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def human(sz):
    if sz > 1e9: return f"{sz/1e9:.2f} GB"
    if sz > 1e6: return f"{sz/1e6:.0f} MB"
    return f"{sz/1e3:.0f} KB"

def rm_dir(path, label):
    if os.path.isdir(path):
        sz = 0
        with os.scandir(path) as it:
            for e in it:
                try: sz += e.stat().st_size
                except: pass
        shutil.rmtree(path, ignore_errors=True)
        print(f"  [OK] {label}: {human(sz)}")
        return sz
    return 0

def rm_dir_contents(path, label):
    """Remove contents of a directory but keep the directory itself.
    Safely handles locked files - skips them gracefully."""
    if not os.path.isdir(path):
        print(f"  --  {label}: not exists")
        return 0
    sz = 0
    skipped = 0
    for entry in os.scandir(path):
        try:
            if entry.is_file(follow_symlinks=False):
                sz += entry.stat().st_size
                try:
                    os.remove(entry.path)
                except PermissionError:
                    skipped += 1
            elif entry.is_dir():
                sub_sz = sum(e.stat().st_size for e in os.scandir(entry.path) if e.is_file())
                sz += sub_sz
                try:
                    shutil.rmtree(entry.path, onexc=lambda *a: None)
                except PermissionError:
                    skipped += 1
        except (PermissionError, OSError):
            skipped += 1
    if sz > 0:
        meta = f" ({skipped} skipped)" if skipped else ""
        print(f"  [OK] {label}: {human(sz)}{meta}")
    return sz

localappdata = os.path.expandvars("%LOCALAPPDATA%")
reclaimed = 0

print("=== C盘保守清理 ===")
print()

# ── PowerToys Updates ──
reclaimed += rm_dir(os.path.join(localappdata, "Microsoft", "PowerToys", "Updates"), "PowerToys Updates")

# ── Edge 缓存（清内容不删目录）──
edge_default = os.path.join(localappdata, "Microsoft", "Edge", "User Data", "Default")
reclaimed += rm_dir_contents(os.path.join(edge_default, "Cache"), "Edge Cache")
reclaimed += rm_dir_contents(os.path.join(edge_default, "Code Cache"), "Edge Code Cache")

# ── Service Worker 缓存 ──
sw_path = os.path.join(edge_default, "Service Worker")
if os.path.isdir(sw_path):
    reclaimed += rm_dir_contents(sw_path, "Edge Service Worker")

# ── D3DSCache ──
reclaimed += rm_dir(os.path.join(localappdata, "D3DSCache"), "D3DSCache")

# ── npm-cache ──
reclaimed += rm_dir(os.path.join(localappdata, "npm-cache"), "npm-cache")

# ── Steam htmlcache（清内容）──
steam_htmlcache = os.path.join(localappdata, "Steam", "htmlcache")
reclaimed += rm_dir_contents(steam_htmlcache, "Steam htmlcache")

# ── bililive ──
reclaimed += rm_dir(os.path.join(localappdata, "bililive"), "bililive")

# ── Doubao 缓存 ──
# update_downloads at root level
reclaimed += rm_dir(os.path.join(localappdata, "Doubao", "User Data", "update_downloads"), "Doubao update_downloads")
# Code Cache in Default
doubao_cc = os.path.join(localappdata, "Doubao", "User Data", "Default", "Code Cache")
reclaimed += rm_dir_contents(doubao_cc, "Doubao Code Cache")

print()
print(f"=== 总计释放: {human(reclaimed)} ===")

free = ctypes.c_ulonglong(0)
total = ctypes.c_ulonglong(0)
ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))
print(f"C 盘剩余: {free.value/1e9:.1f} GB")
