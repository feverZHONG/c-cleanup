"""C 盘状态快速查看。"""
import ctypes, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

free_avail = ctypes.c_ulonglong(0)
total_bytes = ctypes.c_ulonglong(0)
free_total = ctypes.c_ulonglong(0)

ctypes.windll.kernel32.GetDiskFreeSpaceExW(
    "C:",
    ctypes.byref(free_avail),
    ctypes.byref(total_bytes),
    ctypes.byref(free_total),
)

used = total_bytes.value - free_avail.value
pct = used / total_bytes.value * 100

# Decimal GB (10^9) - what Python/standard uses
gb_dec = free_avail.value / 1e9
# Binary GiB (1024^3) - what Windows Explorer uses
gib = free_avail.value / (1024 ** 3)

print(f"C:   Total: {total_bytes.value/1e9:.1f} GB")
print(f"     Used:  {used/1e9:.1f} GB  ({pct:.0f}%)")
print(f"     Free:  {gb_dec:.2f} GB  ({gib:.2f} GiB)")
print(f"     资源管理器显示的是 GiB 值 ({gib:.2f} GiB)，不是 GB")

if free_avail.value < 2e9:
    print("\n[!!] 紧急：C 盘不足 2 GB，停止写入")
elif free_avail.value < 5e9:
    print("\n[!]  警告：C 盘不足 5 GB，建议清理")
else:
    print("\n[i]  正常")
