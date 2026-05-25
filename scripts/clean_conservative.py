"""C盘保守清理 - PowerToys Updates + Edge 缓存 + D3DSCache + npm-cache + Steam htmlcache + bililive + Doubao
适用于定期维护，不会破坏核心数据。"""
import os, sys, io
from utils import human, rm_dir, rm_dir_contents, get_c_drive_free

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

localappdata = os.path.expandvars(r"%LOCALAPPDATA%")
reclaimed = 0

print("=== C盘保守清理 ===")
print()

# -- PowerToys Updates --
reclaimed += rm_dir(os.path.join(localappdata, "Microsoft", "PowerToys", "Updates"), "PowerToys Updates")

# -- Edge 缓存 (清内容不删目录) --
edge_default = os.path.join(localappdata, "Microsoft", "Edge", "User Data", "Default")
reclaimed += rm_dir_contents(os.path.join(edge_default, "Cache"), "Edge Cache")
reclaimed += rm_dir_contents(os.path.join(edge_default, "Code Cache"), "Edge Code Cache")

# -- Service Worker 缓存 --
sw_path = os.path.join(edge_default, "Service Worker")
if os.path.isdir(sw_path):
    reclaimed += rm_dir_contents(sw_path, "Edge Service Worker")

# -- D3DSCache --
reclaimed += rm_dir(os.path.join(localappdata, "D3DSCache"), "D3DSCache")

# -- npm-cache --
reclaimed += rm_dir(os.path.join(localappdata, "npm-cache"), "npm-cache")

# -- Steam htmlcache (清内容) --
reclaimed += rm_dir_contents(os.path.join(localappdata, "Steam", "htmlcache"), "Steam htmlcache")

# -- bililive --
reclaimed += rm_dir(os.path.join(localappdata, "bililive"), "bililive")

# -- Doubao 缓存 --
reclaimed += rm_dir(os.path.join(localappdata, "Doubao", "User Data", "update_downloads"), "Doubao update_downloads")
doubao_cc = os.path.join(localappdata, "Doubao", "User Data", "Default", "Code Cache")
reclaimed += rm_dir_contents(doubao_cc, "Doubao Code Cache")

print()
print(f"=== 总计释放: {human(reclaimed)} ===")

free = get_c_drive_free()
print(f"C 盘剩余: {free/1e9:.1f} GB")
