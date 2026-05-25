"""C盘保守清理 - PowerToys Updates + Edge 缓存 + D3DSCache + npm-cache + Steam htmlcache + bililive + Doubao
适用于定期维护，不会破坏核心数据。"""
import os, sys, io
from utils import human, rm_dir, rm_dir_contents, get_c_drive_free, log_cleanup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DRY_RUN = "--dry-run" in sys.argv
LOG = "--log" in sys.argv

if DRY_RUN:
    print("=== C盘保守清理 [预览模式 --dry-run] ===")
else:
    print("=== C盘保守清理 ===")
print()

def _dry_rm_dir(path, label):
    """Dry-run: scan dir size, no delete."""
    if os.path.isdir(path):
        sz = 0
        try:
            with os.scandir(path) as it:
                for e in it:
                    try: sz += e.stat().st_size
                    except: pass
        except: pass
        print(f"  [DRY] {label}: {human(sz)}")
        return sz
    return 0

def _dry_rm_dir_contents(path, label):
    """Dry-run: scan dir contents size, no delete."""
    if not os.path.isdir(path):
        print(f"  --  {label}: not exists")
        return 0
    sz = 0
    for entry in os.scandir(path):
        try:
            if entry.is_file(follow_symlinks=False):
                sz += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                with os.scandir(entry.path) as it:
                    for e in it:
                        if e.is_file():
                            sz += e.stat().st_size
        except: pass
    if sz > 0:
        print(f"  [DRY] {label}: {human(sz)}")
    return sz

localappdata = os.path.expandvars(r"%LOCALAPPDATA%")
reclaimed = 0

# -- PowerToys Updates --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "Microsoft", "PowerToys", "Updates"), "PowerToys Updates")

# -- Edge 缓存 (清内容不删目录) --
edge_default = os.path.join(localappdata, "Microsoft", "Edge", "User Data", "Default")
reclaimed += (_dry_rm_dir_contents if DRY_RUN else rm_dir_contents)(os.path.join(edge_default, "Cache"), "Edge Cache")
reclaimed += (_dry_rm_dir_contents if DRY_RUN else rm_dir_contents)(os.path.join(edge_default, "Code Cache"), "Edge Code Cache")

# -- Service Worker 缓存 --
sw_path = os.path.join(edge_default, "Service Worker")
if os.path.isdir(sw_path):
    reclaimed += (_dry_rm_dir_contents if DRY_RUN else rm_dir_contents)(sw_path, "Edge Service Worker")

# -- D3DSCache --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "D3DSCache"), "D3DSCache")

# -- npm-cache --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "npm-cache"), "npm-cache")

# -- Steam htmlcache (清内容) --
reclaimed += (_dry_rm_dir_contents if DRY_RUN else rm_dir_contents)(os.path.join(localappdata, "Steam", "htmlcache"), "Steam htmlcache")

# -- bililive --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "bililive"), "bililive")

# -- Doubao 缓存 --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "Doubao", "User Data", "update_downloads"), "Doubao update_downloads")
doubao_cc = os.path.join(localappdata, "Doubao", "User Data", "Default", "Code Cache")
reclaimed += (_dry_rm_dir_contents if DRY_RUN else rm_dir_contents)(doubao_cc, "Doubao Code Cache")

print()
tag = "将释放" if DRY_RUN else "释放"
print(f"=== 总计{tag}: {human(reclaimed)} ===")

free_before = get_c_drive_free()
print(f"C 盘剩余: {free_before/1e9:.1f} GB")

if LOG and not DRY_RUN and reclaimed > 0:
    free_after = get_c_drive_free()
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleanup_history.md")
    log_cleanup("保守清理", free_before / 1e9, free_after / 1e9, reclaimed / 1e9, log_path)
