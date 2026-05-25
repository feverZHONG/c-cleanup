"""C 盘状态快速查看。"""
import sys, io
from utils import human, get_c_drive_info

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

total, free_avail, free_total = get_c_drive_info()
used = total - free_avail
pct = used / total * 100

# Decimal GB (10^9) - what Python/standard uses
gb_dec = free_avail / 1e9
# Binary GiB (1024^3) - what Windows Explorer uses
gib = free_avail / (1024 ** 3)

print(f"C:   Total: {total/1e9:.1f} GB")
print(f"     Used:  {used/1e9:.1f} GB  ({pct:.0f}%)")
print(f"     Free:  {gb_dec:.2f} GB  ({gib:.2f} GiB)")
print(f"     资源管理器显示的是 GiB 值 ({gib:.2f} GiB)，不是 GB")

if free_avail < 2e9:
    print("\n[!!] 紧急：C 盘不足 2 GB，停止写入")
elif free_avail < 5e9:
    print("\n[!]  警告：C 盘不足 5 GB，建议清理")
else:
    print("\n[i]  正常")
