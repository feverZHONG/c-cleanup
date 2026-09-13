"""DriverStore 旧 NVIDIA 驱动清理 - 删除多个版本的 nvami 驱动镜像，保留当前版本
用法:
  python clean_driverstore.py            # 只读扫描，列出可删项
  python clean_driverstore.py --force    # 实际删除旧版本
  python clean_driverstore.py --dry-run  # 预览（同无参）
"""
import os, re, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FORCE = "--force" in sys.argv

# ---- 1. 获取当前驱动版本 (nvidia-smi) ----
def get_current_driver_version():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=30)
        v = out.stdout.strip()
        # 610.88 -> 32.0.16.1088 的换算：最后一位是 8，前面 610 拆成 32.0.16.10?? 
        # 实际转换规则：610.88 -> 61088，前面补 32.0.16. -> 32.0.16.1088（即取版本号去掉点号，前 5 位 + 后 3 位）
        # 但更稳妥的是直接读 DriverStore 里 oem*.inf 的 DriverVer 字段，用 nvidia-smi 版本只做参考
        return v
    except Exception as e:
        print(f"  [!] nvidia-smi 不可用: {e}")
        return None

# ---- 2. 枚举 pnputil 驱动列表，找出 nvami.inf 的 oem 编号 + DriverVer ----
def enum_nvami_drivers():
    """返回 [{oem, ver, date}], ver 形如 32.0.16.1088"""
    result = []
    try:
        out = subprocess.run(["pnputil", "/enum-drivers"], capture_output=True, text=True, timeout=60)
        lines = out.stdout.splitlines()
    except Exception as e:
        print(f"  [!] pnputil 不可用: {e}")
        return result

    cur = {}
    for line in lines:
        line = line.strip()
        m = re.match(r"Published Name:\s+(oem\d+\.inf)", line)
        if m:
            cur = {"oem": m.group(1)}
            continue
        m = re.match(r"Original Name:\s+(\S+)", line)
        if m:
            cur["orig"] = m.group(1)
            continue
        m = re.match(r"Driver Version:\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)", line)
        if m:
            cur["date"] = m.group(1)
            cur["ver"] = m.group(2)
            if cur.get("orig") == "nvami.inf":
                result.append(dict(cur))
    return result

# ---- 3. 排序：把版本号转成可比较的元组 ----
def ver_tuple(v):
    return tuple(int(x) for x in v.split("."))

# ---- 4. 删除 ----
def delete_driver(oem):
    r = subprocess.run(["pnputil", "/delete-driver", oem], capture_output=True, text=True, timeout=60)
    return r.returncode == 0, r.stdout.strip()

def main():
    print("=== DriverStore 旧 NVIDIA 驱动清理 ===")
    if not FORCE:
        print("  [只读扫描模式] 加 --force 才会真正删除\n")
    else:
        print("  [--force] 开始删除旧版本\n")

    current_smi = get_current_driver_version()
    print(f"nvidia-smi 当前驱动: {current_smi}")

    drivers = enum_nvami_drivers()
    if not drivers:
        print("  [!] 未找到 nvami.inf 驱动（可能没有 NVIDIA 驱动或 pnputil 不可用）")
        return

    # 找版本号最大者为当前驱动
    drivers_sorted = sorted(drivers, key=lambda d: ver_tuple(d["ver"]))
    current = drivers_sorted[-1]
    old = drivers_sorted[:-1]

    print(f"\n  当前驱动 (保留): oem={current['oem']}  ver={current['ver']} ({current['date']})")
    if not old:
        print("  没有旧版本驱动可清理 ✓")
        return

    print(f"\n  可清理旧版本 ({len(old)} 个):")
    for d in old:
        print(f"    oem={d['oem']}  ver={d['ver']} ({d['date']})")

    total = 0
    for d in old:
        if not FORCE:
            continue
        ok, msg = delete_driver(d["oem"])
        if ok:
            print(f"\n  [OK] 删除 {d['oem']} ({d['ver']})")
        else:
            print(f"\n  [FAIL] {d['oem']} ({d['ver']}):")
            print(f"    {msg}")
            print("    → 若提示 'One or more devices are presently installed'：")
            print("      引用计数未清，重启后再试即可。不要用 /force 强删。")

    if not FORCE:
        print("\n  使用 --force 实际删除。")

if __name__ == "__main__":
    main()
