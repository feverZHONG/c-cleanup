"""小米互联服务（MI ContinuityApp / AIService）清理
默认只读扫描；--force 才真正删除。

2026-11-14 首次摸底：整套占 C 盘 2.97 GB，其中只有两笔是可再生的缓存：
  - micloud\\gallery           相册同步缓存（手机端保留原件，删了下次同步重下）
  - AIService\\search\\cache    AI 搜索索引库 ai_database1.db（会重建，也会随使用持续增长）

⚠ 治本不是在设置清理里反复删索引，而是关掉小米互联的「AI 搜索 / 本地索引」。
⚠ 绝不碰：Program Files\\MI 本体、miclaw.sqlite（状态库）、micloud\\note\\attachments（笔记附件）、
          Partitions\\*\\Preferences / SharedStorage（WebView 分区状态，删了要重新登录配置）。

用法:
  python clean_mi.py            # 只读扫描，列出各处占用
  python clean_mi.py --force    # 清 gallery + search cache（清内容保留目录，被占用则跳过）
"""
import os, sys, io
from utils import human, rm_dir_contents, get_c_drive_free

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FORCE = "--force" in sys.argv

LOCAL = os.path.expandvars(r"%LOCALAPPDATA%")
PROGRAMDATA = os.path.expandvars(r"%PROGRAMDATA%")

APP = os.path.join(LOCAL, "MI", "ContinuityApp")
TARGETS = [
    (os.path.join(APP, "micloud", "gallery"),
     "相册同步缓存 (gallery)"),
    (os.path.join(PROGRAMDATA, "MI", "AIService", "search", "cache"),
     "AI 搜索索引库 (search/cache)"),
]
# 顺带报告的小缓存（不主动清，随保守清理带走）
MINOR = [
    (os.path.join(APP, "Cache"), "应用缓存 (Cache)"),
    (os.path.join(APP, "GPUCache"), "GPU 缓存 (GPUCache)"),
    (os.path.join(APP, "logs"), "日志 (logs)"),
]

def dir_size(p):
    t = 0
    if not os.path.isdir(p):
        return 0
    for root, dirs, files in os.walk(p):
        for f in files:
            try:
                t += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return t

def file_size(p):
    try:
        return os.path.getsize(p) if os.path.isfile(p) else 0
    except OSError:
        return 0

print("=== 小米互联服务清理 %s ===" % ("[--force 执行]" if FORCE else "[只读扫描]"))
print()

free_before = get_c_drive_free()
reclaimed = 0

for path, label in TARGETS:
    if not os.path.isdir(path):
        print("  --  %s: 不存在" % label)
        continue
    sz = dir_size(path)
    if FORCE:
        freed = rm_dir_contents(path, label)
        reclaimed += freed
    else:
        print("  [DRY] %s: %s" % (label, human(sz)))

print()
print("--- 顺带报告（小缓存，未清理）---")
minor_total = 0
for path, label in MINOR:
    sz = dir_size(path)
    minor_total += sz
    if sz > 0:
        print("  %s: %s" % (label, human(sz)))
print("  小计: %s" % human(minor_total))

print()
print("--- 不碰（用户数据/程序本体）---")
for path, label in [
    (os.path.join(APP, "miclaw.sqlite"), "对话/状态库 miclaw.sqlite"),
    (os.path.join(APP, "micloud", "note", "attachments"), "笔记附件"),
    (r"C:\Program Files\MI", "程序本体"),
]:
    sz = file_size(path) or dir_size(path)
    print("  %s: %s" % (label, human(sz)))

print()
if FORCE:
    print("=== 释放: %s ===" % human(reclaimed))
else:
    print("[WARN] 只读模式。要真正清理请执行:")
    print("   python scripts/clean_mi.py --force")
    print("   注意: 相册同步缓存删了，下次打开相册会重新下载。")
    print("   AI 搜索索引删了会重建，且会继续增长 —— 治本请在小爱/小米互联设置里关掉 AI 搜索。")

free_now = get_c_drive_free()
print("C 盘剩余: %.2f GB" % (free_now / 1e9))
