"""C盘安全清理 - updater缓存 + 旧DXCache(自动检测) + Temp/pip/npm + ima.copilot + NEO + GameViewer + OfficePLUS
可直接执行，无需用户额外确认。"""
import os, sys, io
from utils import human, rm_dir, rm_dir_contents_gentle, rm_glob_files, get_dxcache_prefixes, get_c_drive_free

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

localappdata = os.path.expandvars(r"%LOCALAPPDATA%")
reclaimed = 0

print("=== C盘安全清理 ===")
print()

# -- Updater 缓存 --
updater_dirs = [
    "@guanjia-openclawelectron-updater",
    "autoclaw-updater", "cherrystudio-updater", "edm-updater",
    "anythingllm-desktop-updater", "bilibili-updater", "canva-updater",
    "qq-chat-updater", "motrix-updater", "quark-cloud-drive-updater",
    "@prompt-optimizerdesktop-updater",
]
for d in updater_dirs:
    reclaimed += rm_dir(os.path.join(localappdata, d), d)

# -- C盘根目录残留 --
reclaimed += rm_dir(r"C:	emp_ts_merge", r"C:	emp_ts_merge")

# -- 旧 NVIDIA DXCache (自动检测：扫描全部前缀，跳过当前最大前缀) --
dxcache = os.path.join(localappdata, "NVIDIA", "DXCache")
prefixes, current_prefix = get_dxcache_prefixes(dxcache)
for prefix in prefixes:
    if prefix == current_prefix or prefix == "":
        continue
    sz, count = rm_glob_files(dxcache, prefix)
    if sz > 0:
        print(f"  [OK] 旧 DXCache ({prefix}): {human(sz)} ({count} files)")
        reclaimed += sz

# -- Temp (清内容不删目录) --
reclaimed += rm_dir_contents_gentle(os.path.expandvars(r"%TEMP%"), "Temp")

# -- pip 缓存 --
reclaimed += rm_dir(os.path.join(localappdata, "pip", "cache"), "pip cache")

# -- npm 缓存 --
reclaimed += rm_dir(os.path.join(localappdata, "npm-cache"), "npm-cache")

# -- ima.copilot --
reclaimed += rm_dir(os.path.join(localappdata, "ima.copilot"), "ima.copilot")

# -- NEO 编译器缓存 --
reclaimed += rm_dir(os.path.join(localappdata, "NEO", "neo_compiler_cache"), "NEO compiler cache")

# -- GameViewer webviewcache --
reclaimed += rm_dir(os.path.join(localappdata, "GameViewer", "webviewcache"), "GameViewer webviewcache")

# -- OfficePLUS WebView2 --
reclaimed += rm_dir(os.path.join(localappdata, "OfficePLUS", "webview2"), "OfficePLUS WebView2")

print()
print(f"=== 总计释放: {human(reclaimed)} ===")

free = get_c_drive_free()
print(f"C 盘剩余: {free/1e9:.1f} GB")
