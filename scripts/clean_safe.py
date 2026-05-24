"""C盘安全清理 — updater缓存 + 旧DXCache + Temp/pip/npm + ima.copilot + NEO + GameViewer + OfficePLUS
可直接执行，无需用户额外确认。"""
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

def rm_glob_files(directory, prefix):
    total = 0
    count = 0
    if os.path.isdir(directory):
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file() and entry.name.startswith(prefix):
                    total += entry.stat().st_size
                    count += 1
                    try: os.remove(entry.path)
                    except: pass
    return total, count

def rm_dir_contents(path, label):
    """Remove contents of a directory but keep the directory itself.
    Safely handles locked files - skips them gracefully instead of hammering."""
    if not os.path.isdir(path):
        print(f"  --  {label}: not exists")
        return 0
    sz = 0
    count = 0
    skipped = 0
    for entry in os.scandir(path):
        try:
            if entry.is_file(follow_symlinks=False):
                sz += entry.stat().st_size
                try:
                    os.remove(entry.path)
                    count += 1
                except PermissionError:
                    skipped += 1
            elif entry.is_dir():
                sub_sz = sum(e.stat().st_size for e in os.scandir(entry.path) if e.is_file())
                sz += sub_sz
                try:
                    shutil.rmtree(entry.path, onexc=lambda *a: None)
                    count += 1
                except PermissionError:
                    skipped += 1
        except (PermissionError, OSError):
            skipped += 1
    if sz > 0:
        meta = f" ({skipped} skipped)" if skipped else ""
        print(f"  [OK] {label}: {human(sz)}{meta}")
    else:
        print(f"  --  {label}: empty or not exists (skipped {skipped})")
    return sz

def rm_dir_contents_gentle(path, label):
    """Super gentle variant - process in batches with delay, for Temp."""
    import time
    if not os.path.isdir(path):
        print(f"  --  {label}: not exists")
        return 0
    total_sz = 0
    total_ok = 0
    total_skip = 0
    entries = list(os.scandir(path))
    batch_size = 50
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        for entry in batch:
            try:
                if entry.is_file(follow_symlinks=False):
                    total_sz += entry.stat().st_size
                    try:
                        os.remove(entry.path)
                        total_ok += 1
                    except PermissionError:
                        total_skip += 1
                elif entry.is_dir():
                    sub_sz = sum(e.stat().st_size for e in os.scandir(entry.path) if e.is_file())
                    total_sz += sub_sz
                    try:
                        shutil.rmtree(entry.path, onexc=lambda *a: None)
                        total_ok += 1
                    except PermissionError:
                        total_skip += 1
            except (PermissionError, OSError):
                total_skip += 1
        if i > 0 and i % 200 == 0:
            time.sleep(0.2)
    if total_sz > 0:
        meta = f" ({total_skip} skipped)" if total_skip else ""
        print(f"  [OK] {label}: {human(total_sz)}{meta}")
    else:
        print(f"  --  {label}: empty (skipped {total_skip})")
    return total_sz

localappdata = os.path.expandvars("%LOCALAPPDATA%")
userprofile = os.path.expanduser("~")
reclaimed = 0

print("=== C盘安全清理 ===")
print()

# ── Updater 缓存 ──
reclaimed += rm_dir(os.path.join(localappdata, "@guanjia-openclawelectron-updater"), "@guanjia-openclawelectron-updater")
reclaimed += rm_dir(os.path.join(localappdata, "autoclaw-updater"), "autoclaw-updater")
reclaimed += rm_dir(os.path.join(localappdata, "cherrystudio-updater"), "cherrystudio-updater")
reclaimed += rm_dir(os.path.join(localappdata, "edm-updater"), "edm-updater")
reclaimed += rm_dir(os.path.join(localappdata, "anythingllm-desktop-updater"), "anythingllm-desktop-updater")
reclaimed += rm_dir(os.path.join(localappdata, "bilibili-updater"), "bilibili-updater")
reclaimed += rm_dir(os.path.join(localappdata, "canva-updater"), "canva-updater")
reclaimed += rm_dir(os.path.join(localappdata, "qq-chat-updater"), "qq-chat-updater")
reclaimed += rm_dir(os.path.join(localappdata, "motrix-updater"), "motrix-updater")
reclaimed += rm_dir(os.path.join(localappdata, "quark-cloud-drive-updater"), "quark-cloud-drive-updater")
reclaimed += rm_dir(os.path.join(localappdata, "@prompt-optimizerdesktop-updater"), "@prompt-optimizerdesktop-updater")

# ── C盘根目录残留 ──
reclaimed += rm_dir("C:\\temp_ts_merge", "C:\\temp_ts_merge")

# ── 旧 NVIDIA DXCache ──
dxcache = os.path.join(localappdata, "NVIDIA", "DXCache")
old_prefixes = ["43e0a938", "6d61a938", "0002a938", "f66ba938", "1a2ba938"]
for prefix in old_prefixes:
    sz, count = rm_glob_files(dxcache, prefix)
    if sz > 0:
        print(f"  [OK] 旧 DXCache ({prefix}): {human(sz)} ({count} files)")
        reclaimed += sz

# ── Temp (清内容不删目录) ──
temp_dir = os.path.expandvars("%TEMP%")
reclaimed += rm_dir_contents_gentle(temp_dir, "Temp")

# ── pip 缓存 ──
reclaimed += rm_dir(os.path.join(localappdata, "pip", "cache"), "pip cache")

# ── npm 缓存 ──
reclaimed += rm_dir(os.path.join(localappdata, "npm-cache"), "npm-cache")

# ── ima.copilot ──
reclaimed += rm_dir(os.path.join(localappdata, "ima.copilot"), "ima.copilot")

# ── NEO 编译器缓存 ──
reclaimed += rm_dir(os.path.join(localappdata, "NEO", "neo_compiler_cache"), "NEO compiler cache")

# ── GameViewer webviewcache ──
reclaimed += rm_dir(os.path.join(localappdata, "GameViewer", "webviewcache"), "GameViewer webviewcache")

# ── OfficePLUS WebView2 ──
reclaimed += rm_dir(os.path.join(localappdata, "OfficePLUS", "webview2"), "OfficePLUS WebView2")

print()
print(f"=== 总计释放: {human(reclaimed)} ===")

# 清理后 C 盘空间
free = ctypes.c_ulonglong(0)
total = ctypes.c_ulonglong(0)
ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))
print(f"C 盘剩余: {free.value/1e9:.1f} GB")
