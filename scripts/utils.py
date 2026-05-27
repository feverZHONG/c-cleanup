"""Shared utilities for c-cleanup scripts."""
import os, shutil, ctypes

def human(sz):
    if sz > 1e9: return f"{sz/1e9:.2f} GB"
    if sz > 1e6: return f"{sz/1e6:.0f} MB"
    return f"{sz/1e3:.0f} KB"

def rm_dir(path, label):
    """Delete entire directory and report size."""
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
                    shutil.rmtree(entry.path, onerror=lambda *a: None)
                except PermissionError:
                    skipped += 1
        except (PermissionError, OSError):
            skipped += 1
    if sz > 0:
        meta = f" ({skipped} skipped)" if skipped else ""
        print(f"  [OK] {label}: {human(sz)}{meta}")
    return sz

def rm_dir_contents_gentle(path, label):
    """Super gentle variant - process in batches with delay, for Temp."""
    import time
    if not os.path.isdir(path):
        print(f"  --  {label}: not exists")
        return 0
    total_sz = 0
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
                    except PermissionError:
                        total_skip += 1
                elif entry.is_dir():
                    sub_sz = sum(e.stat().st_size for e in os.scandir(entry.path) if e.is_file())
                    total_sz += sub_sz
                    try:
                        shutil.rmtree(entry.path, onerror=lambda *a: None)
                    except PermissionError:
                        total_skip += 1
            except (PermissionError, OSError):
                total_skip += 1
        format_progress(min(i + batch_size, len(entries)), len(entries), label)
        if i > 0 and i % 200 == 0:
            time.sleep(0.2)
    if total_sz > 0:
        meta = f" ({total_skip} skipped)" if total_skip else ""
        print(f"  [OK] {label}: {human(total_sz)}{meta}")
    else:
        print(f"  --  {label}: empty (skipped {total_skip})")
    return total_sz

def rm_glob_files(directory, prefix):
    """Delete all files in a directory that start with a given prefix."""
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


import datetime

def log_cleanup(cleanup_type, before_gb, after_gb, reclaimed_gb, log_path):
    """Append a cleanup record to the history file."""
    from datetime import date
    row = "| {} | {} | {:.1f} | {:.1f} | {:.1f} |\n".format(
        date.today().isoformat(), cleanup_type, before_gb, after_gb, reclaimed_gb
    )
    try:
        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        # If file doesn't exist or is empty, create with header
        if not os.path.isfile(log_path) or os.path.getsize(log_path) == 0:
            header = "# 清理记录\n\n| 日期 | 类型 | 清理前 (GB) | 清理后 (GB) | 释放 (GB) |\n|------|------|-------------|-------------|-----------|\n"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(header)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(row)
        return True
    except Exception as e:
        print(f"  [WARN] 写入清理记录失败: {e}")
        return False

def format_progress(current, total, label=""):
    """Print a progress indicator if total is large enough."""
    if total >= 100 and current % 100 == 0:
        pct = int(current / total * 100)
        meta = f" ({label})" if label else ""
        print(f"  ... 处理中: {current}/{total} ({pct}%){meta}")

def get_c_drive_free():
    """Get C drive free space in bytes (available to caller)."""
    free = ctypes.c_ulonglong(0)
    total = ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))
    return free.value

def get_c_drive_info():
    """Get C drive info as (total_bytes, free_avail_bytes, free_total_bytes)."""
    free_avail = ctypes.c_ulonglong(0)
    total_bytes = ctypes.c_ulonglong(0)
    free_total = ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        "C:",
        ctypes.byref(free_avail),
        ctypes.byref(total_bytes),
        ctypes.byref(free_total),
    )
    return total_bytes.value, free_avail.value, free_total.value

def get_dxcache_prefixes(dxcache_dir):
    """Scan DXCache and return (prefixes_dict, current_prefix).
    Prefixes dict: {prefix_8char: {"size": int, "count": int}}
    Current = prefix with largest total size (most reliable heuristic)."""
    files = []
    if os.path.isdir(dxcache_dir):
        with os.scandir(dxcache_dir) as it:
            for entry in it:
                if entry.is_file():
                    files.append((entry.name, entry.stat().st_size))

    prefixes = {}
    for name, sz in files:
        p = name[:8]
        if p not in prefixes:
            prefixes[p] = {"size": 0, "count": 0}
        prefixes[p]["size"] += sz
        prefixes[p]["count"] += 1

    current = max(prefixes, key=lambda p: prefixes[p]["size"]) if prefixes else ""
    return prefixes, current
