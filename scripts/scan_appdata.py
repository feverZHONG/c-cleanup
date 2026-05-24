"""扫描 AppData\Local 中大于 100MB 的目录。"""
import os

def folder_size(path):
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += folder_size(entry.path)
                except: pass
    except: pass
    return total

def human(sz):
    if sz > 1e9: return f"{sz/1e9:.2f} GB"
    if sz > 1e6: return f"{sz/1e6:.0f} MB"
    return f"{sz/1e3:.0f} KB"

localappdata = os.path.expandvars("%LOCALAPPDATA%")
print(f"=== AppData\\Local > 100MB ===\n")

results = []
with os.scandir(localappdata) as it:
    for entry in it:
        if entry.is_dir(follow_symlinks=False):
            sz = folder_size(entry.path)
            if sz > 100e6:
                results.append((entry.name, sz))

results.sort(key=lambda x: -x[1])
for name, sz in results:
    print(f"  {human(sz):>10}  {name}")

print()
# Also show C drive
import ctypes
free = ctypes.c_ulonglong(0)
total = ctypes.c_ulonglong(0)
ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))
print(f"C:   Total: {total.value/1e9:.1f} GB | Used: {(total.value-free.value)/1e9:.1f} GB | Free: {free.value/1e9:.1f} GB")
