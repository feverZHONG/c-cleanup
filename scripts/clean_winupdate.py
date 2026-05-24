"""清理 Windows Update 下载缓存（SoftwareDistribution\Download）。
需要管理员权限。"""
import os, shutil, subprocess, sys, ctypes, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def human(sz):
    if sz > 1e9: return f"{sz/1e9:.2f} GB"
    if sz > 1e6: return f"{sz/1e6:.0f} MB"
    return f"{sz/1e3:.0f} KB"

sd = r"C:\Windows\SoftwareDistribution\Download"

# Check admin
if not ctypes.windll.shell32.IsUserAnAdmin():
    print("[ERROR] 需要管理员权限才能清理 Windows Update 缓存。请以管理员身份运行。")
    sys.exit(1)

if not os.path.isdir(sd):
    print("SoftwareDistribution\\Download: 不存在，无需清理。")
    sys.exit(0)

# Measure before
sz_before = 0
with os.scandir(sd) as it:
    for entry in it:
        try:
            if entry.is_file(follow_symlinks=False):
                sz_before += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                sz_before += sum(e.stat().st_size for e in os.scandir(entry.path) if e.is_file())
        except: pass

print(f"SoftwareDistribution\\Download 缓存: {human(sz_before)}")

if "--force" not in sys.argv:
    print("\n这是扫描模式。要真正清理，请加上 --force 参数。")
    sys.exit(0)

# Stop services
for svc in ["wuauserv", "TrustedInstaller"]:
    subprocess.run(["net", "stop", svc, "/y"], capture_output=True, text=True)

# Clean
try:
    with os.scandir(sd) as it:
        for entry in it:
            try:
                if entry.is_file():
                    os.remove(entry.path)
                elif entry.is_dir():
                    shutil.rmtree(entry.path, ignore_errors=True)
            except Exception as e:
                print(f"  删除失败: {entry.name}: {e}")
    print("清理完成。")
except Exception as e:
    print(f"清理失败: {e}")

# Restart services
subprocess.run(["net", "start", "wuauserv"], capture_output=True, text=True)

# Show result
after = sum(e.stat().st_size for e in os.scandir(sd) if e.is_file()) if os.path.isdir(sd) else 0
print(f"释放: {human(sz_before - after)}" if sz_before > after else "已清空。")
