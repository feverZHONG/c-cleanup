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
                             capture_output=True, text=True, encoding="mbcs", errors="replace", timeout=30)
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
        out = subprocess.run(["pnputil", "/enum-drivers"], capture_output=True, text=True,
                             encoding="mbcs", errors="replace", timeout=60)
        lines = out.stdout.splitlines()
    except Exception as e:
        print(f"  [!] pnputil 不可用: {e}")
        return result

    cur = {}
    for line in lines:
        line = line.strip()
        m = re.match(r"(?:Published Name|发布名称)[:：]\s+(oem\d+\.inf)", line)
        if m:
            cur = {"oem": m.group(1)}
            continue
        m = re.match(r"(?:Original Name|原始名称)[:：]\s+(\S+)", line)
        if m:
            cur["orig"] = m.group(1)
            continue
        m = re.match(r"(?:Driver Version|驱动程序版本)[:：]\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)", line)
        if m:
            cur["date"] = m.group(1)
            cur["ver"] = m.group(2)
            if cur.get("orig") == "nvami.inf":
                result.append(dict(cur))
    return result

# ---- 3. 排序：把版本号转成可比较的元组 ----
def ver_tuple(v):
    return tuple(int(x) for x in v.split("."))

# ---- 3.5 权威来源：设备实际绑定的驱动版本（注册表）----
# ⚠ 绝不能用「版本号最大」当当前驱动：NVIDIA App 可能已把新版包装进 DriverStore 却没绑到设备
#   （2026-11-14 实测：DriverStore 有 32.0.16.2101，设备实际仍绑 32.0.16.1742）。
#   按版本号最大判断会把「正在用的驱动」当旧版删掉。
def get_bound_driver_version():
    import winreg
    cls = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, cls)
    except OSError as e:
        print(f"  [!] 打不开显示适配器类键: {e}")
        return None
    bound = None
    i = 0
    try:
        while True:
            try:
                name = winreg.EnumKey(k, i)
            except OSError:
                break
            i += 1
            if not re.match(r"^\d{4}$", name):
                continue
            try:
                sk = winreg.OpenKey(k, name)
                try:
                    desc = winreg.QueryValueEx(sk, "DriverDesc")[0]
                    ver = winreg.QueryValueEx(sk, "DriverVersion")[0]
                finally:
                    winreg.CloseKey(sk)
            except OSError:
                continue
            if ver and "NVIDIA" in str(desc).upper():
                print(f"  绑定设备: {desc}  DriverVer={ver}")
                bound = ver
    finally:
        winreg.CloseKey(k)
    return bound

# ---- 4. 删除 ----
def delete_driver(oem):
    r = subprocess.run(["pnputil", "/delete-driver", oem], capture_output=True, text=True,
                       encoding="mbcs", errors="replace", timeout=60)
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

    # 当前驱动 = 设备实际绑定的版本（注册表权威），不是版本号最大的那个
    bound = get_bound_driver_version()
    if not bound:
        print("\n  [ABORT] 拿不到设备实际绑定的驱动版本，为避免删错驱动，本次不做任何判断。")
        return

    built = [d for d in drivers if d["ver"] == bound]
    if not built:
        print(f"\n  [ABORT] DriverStore 里找不到与绑定版本 {bound} 对应的 nvami 包，不做删除。")
        return

    current = built[-1]
    old = [d for d in drivers if d["ver"] != bound]

    print(f"\n  当前驱动 (保留): oem={current['oem']}  ver={current['ver']} ({current['date']})")
    if not old:
        print("  没有旧版本驱动可清理 ✓")
        return

    print(f"\n  可清理非当前版本 ({len(old)} 个)（未绑定到任何设备的驱动包）:")
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
