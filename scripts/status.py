"""C 盘状态快速查看。"""
import ctypes, io, sys, subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

free = ctypes.c_ulonglong(0)
total = ctypes.c_ulonglong(0)
ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))

used = total.value - free.value
pct = used / total.value * 100

print(f"C:   Total: {total.value/1e9:.1f} GB")
print(f"     Used:  {used/1e9:.1f} GB  ({pct:.0f}%)")
print(f"     Free:  {free.value/1e9:.1f} GB")
print(f"     (字节: {total.value:,} 总 / {free.value:,} 可用)")

try:
    r = subprocess.run(["powershell", "-Command", "(Get-PSDrive C).Free"],
                      capture_output=True, text=True, timeout=5)
    if r.stdout.strip().isdigit():
        ps_free = int(r.stdout.strip())
        fe_free = ps_free - int(700 * 1024 * 1024)
        fe_gb = fe_free / 1e9
        print(f"     Win11 资源管理器: {fe_gb:.2f} GB")
except:
    pass

if free.value < 2e9:
    print("\n[!!] 紧急：C 盘不足 2 GB，停止写入")
elif free.value < 5e9:
    print("\n[!]  警告：C 盘不足 5 GB，建议清理")
else:
    print("\n[i]  正常")
