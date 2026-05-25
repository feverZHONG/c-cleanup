"""C盘安全清理 - updater缓存 + 旧DXCache(自动检测) + Temp/pip/npm + ima.copilot + NEO + GameViewer + OfficePLUS
可直接执行，无需用户额外确认。"""
import os, sys, io
from utils import human, rm_dir, rm_dir_contents_gentle, rm_glob_files, get_dxcache_prefixes, get_c_drive_free, log_cleanup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DRY_RUN = "--dry-run" in sys.argv
LOG = "--log" in sys.argv

if DRY_RUN:
    print("=== C盘安全清理 [预览模式 --dry-run] ===")
else:
    print("=== C盘安全清理 ===")
print()

def _dry_rm_dir(path, label):
    """Dry-run: scan and report size, no delete."""
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

def _dry_rm_glob_files(directory, prefix):
    """Dry-run: count files by prefix, no delete."""
    total = 0
    count = 0
    if os.path.isdir(directory):
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file() and entry.name.startswith(prefix):
                    total += entry.stat().st_size
                    count += 1
    return total, count

def _dry_rm_dir_contents_gentle(path, label):
    """Dry-run: scan Temp contents, no delete."""
    if not os.path.isdir(path):
        print(f"  --  {label}: not exists")
        return 0
    total_sz = 0
    for entry in os.scandir(path):
        try:
            if entry.is_file(follow_symlinks=False):
                total_sz += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                with os.scandir(entry.path) as it:
                    for e in it:
                        if e.is_file():
                            total_sz += e.stat().st_size
        except: pass
    if total_sz > 0:
        print(f"  [DRY] {label}: {human(total_sz)}")
    return total_sz

localappdata = os.path.expandvars(r"%LOCALAPPDATA%")
reclaimed = 0

# -- Updater 缓存 --
updater_dirs = [
    "@guanjia-openclawelectron-updater",
    "autoclaw-updater", "cherrystudio-updater", "edm-updater",
    "anythingllm-desktop-updater", "bilibili-updater", "canva-updater",
    "qq-chat-updater", "motrix-updater", "quark-cloud-drive-updater",
    "@prompt-optimizerdesktop-updater",
]
for d in updater_dirs:
    reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, d), d)

# -- C盘根目录残留 --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(r"C:\temp_ts_merge", r"C:\temp_ts_merge")

# -- 旧 NVIDIA DXCache (自动检测：扫描全部前缀，跳过当前最大前缀) --
dxcache = os.path.join(localappdata, "NVIDIA", "DXCache")
prefixes, current_prefix = get_dxcache_prefixes(dxcache)
for prefix in prefixes:
    if prefix == current_prefix or prefix == "":
        continue
    if DRY_RUN:
        sz, count = _dry_rm_glob_files(dxcache, prefix)
    else:
        sz, count = rm_glob_files(dxcache, prefix)
    if sz > 0:
        tag = "[DRY]" if DRY_RUN else "[OK]"
        print(f"  {tag} 旧 DXCache ({prefix}): {human(sz)} ({count} files)")
        reclaimed += sz

# -- Temp (清内容不删目录) --
reclaimed += (_dry_rm_dir_contents_gentle if DRY_RUN else rm_dir_contents_gentle)(
    os.path.expandvars(r"%TEMP%"), "Temp")

# -- pip 缓存 --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "pip", "cache"), "pip cache")

# -- npm 缓存 --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "npm-cache"), "npm-cache")

# -- ima.copilot --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "ima.copilot"), "ima.copilot")

# -- NEO 编译器缓存 --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "NEO", "neo_compiler_cache"), "NEO compiler cache")

# -- GameViewer webviewcache --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "GameViewer", "webviewcache"), "GameViewer webviewcache")

# -- OfficePLUS WebView2 --
reclaimed += (_dry_rm_dir if DRY_RUN else rm_dir)(os.path.join(localappdata, "OfficePLUS", "webview2"), "OfficePLUS WebView2")

print()
tag = "将释放" if DRY_RUN else "释放"
print(f"=== 总计{tag}: {human(reclaimed)} ===")

free_before = get_c_drive_free()
print(f"C 盘剩余: {free_before/1e9:.1f} GB")

if LOG and not DRY_RUN and reclaimed > 0:
    free_after = get_c_drive_free()
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleanup_history.md")
    log_cleanup("安全清理", free_before / 1e9, free_after / 1e9, reclaimed / 1e9, log_path)
