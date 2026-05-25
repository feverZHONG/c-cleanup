"""扫描 AppData\Local 中大于 100MB 的目录。"""
import os, sys, io
from utils import human, get_c_drive_info

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

localappdata = os.path.expandvars(r"%LOCALAPPDATA%")
print("=== AppData\Local > 100MB ===")
print()

results = []
with os.scandir(localappdata) as it:
    for entry in it:
        if entry.is_dir(follow_symlinks=False):
            sz = 0
            try:
                # Iterative walk (avoid deep recursion)
                stack = [entry.path]
                while stack:
                    current = stack.pop()
                    with os.scandir(current) as sub_it:
                        for sub_entry in sub_it:
                            try:
                                if sub_entry.is_file(follow_symlinks=False):
                                    sz += sub_entry.stat().st_size
                                elif sub_entry.is_dir(follow_symlinks=False):
                                    stack.append(sub_entry.path)
                            except: pass
            except: pass
            if sz > 100e6:
                results.append((entry.name, sz))

results.sort(key=lambda x: -x[1])
for name, sz in results:
    print(f"  {human(sz):>10}  {name}")

print()
total, free_avail, free_total = get_c_drive_info()
used = total - free_avail
print(f"C:   Total: {total/1e9:.1f} GB | Used: {used/1e9:.1f} GB | Free: {free_avail/1e9:.1f} GB")
