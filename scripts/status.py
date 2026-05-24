"""C 盘状态快速查看。"""
import ctypes, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

free = ctypes.c_ulonglong(0)
total = ctypes.c_ulonglong(0)
ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:", None, ctypes.byref(total), ctypes.byref(free))

used = total.value - free.value
pct = used / total.value * 100

print(f"C:   Total: {total.value/1e9:.1f} GB")
print(f"     Used:  {used/1e9:.1f} GB  ({pct:.0f}%)")
print(f"     Free:  {free.value/1e9:.1f} GB")

if free.value < 2e9:
    print("\n[!!] 紧急：C 盘不足 2 GB，停止写入")
elif free.value < 5e9:
    print("\n[!]  警告：C 盘不足 5 GB，建议清理")
else:
    print("\n[i]  正常")
