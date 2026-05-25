"""Unified C盘清理入口

一键执行各类清理操作。将所有脚本整合为统一命令。

用法:
  python scripts/clean.py                     安全清理 (默认)
  python scripts/clean.py --level safe       安全清理
  python scripts/clean.py --level conservative  保守清理
  python scripts/clean.py --level all         安全 + 保守
  python scripts/clean.py --level deep        深度清理 (仅扫描)
  python scripts/clean.py --dry-run           预览模式 (不执行删除)
  python scripts/clean.py --force             含深度清理执行 (与 --level deep 或 --level all 联用)
  python scripts/clean.py --log               记录到清理历史

示例:
  python scripts/clean.py --level all --dry-run      预览全部可释放空间
  python scripts/clean.py --level all --log           安全+保守并记录
  python scripts/clean.py --level deep --force        执行深度清理
"""
import sys, os, io, subprocess, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(name, extra_args=None):
    """Run a script in the same Python process environment."""
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, name)]
    if extra_args:
        cmd.extend(extra_args)
    print(f"--- 执行: {name} ---")
    print()
    before = time.time()
    r = subprocess.run(cmd, cwd=os.path.dirname(SCRIPTS_DIR))
    elapsed = time.time() - before
    print()
    if r.returncode != 0:
        print(f"[WARN] {name} 返回非零退出码: {r.returncode}")
    print(f"--- {name} 完成 ({elapsed:.1f}s) ---")
    print()
    return r.returncode

# Parse args
args = set(sys.argv[1:])

level = "safe"
for lv in ["safe", "conservative", "all", "deep", "winupdate"]:
    if f"--level={lv}" in sys.argv or f"--level {lv}" in sys.argv or lv == sys.argv[sys.argv.index("--level") + 1] if "--level" in sys.argv else False:
        level = lv
        break

# If --level is followed by an arg
if "--level" in sys.argv:
    idx = sys.argv.index("--level")
    if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
        level = sys.argv[idx + 1]

# Collect extra args to pass to sub-scripts
extra = []
if "--dry-run" in args:
    extra.append("--dry-run")
if "--log" in args:
    extra.append("--log")

print("=== C盘清理工具 ===")
print(f"模式: {level}")
if "--dry-run" in args:
    print("预览模式: 仅扫描，不执行删除")
if "--log" in args:
    print("记录模式: 结果写入清理历史")
print()

exit_code = 0

if level in ("safe", "all"):
    run_script("clean_safe.py", extra)

if level in ("conservative", "all"):
    run_script("clean_conservative.py", extra)

if level == "deep":
    deep_args = list(extra)
    if "--force" in args:
        deep_args.append("--force")
    run_script("clean_deep.py", deep_args)

if level == "winupdate":
    win_args = list(extra)
    if "--force" in args:
        win_args.append("--force")
    run_script("clean_winupdate.py", win_args)

print("=== 全部完成 ===")
sys.exit(exit_code)
