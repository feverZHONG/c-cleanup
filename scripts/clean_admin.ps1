# C盘提权清理 — 需要管理员权限的目标，一次 UAC 全搞定
#
# 用法（在「管理员」PowerShell 里跑）：
#     powershell -NoProfile -ExecutionPolicy Bypass -File clean_admin.ps1
#     powershell -NoProfile -ExecutionPolicy Bypass -File clean_admin.ps1 -DryRun
#     powershell -NoProfile -ExecutionPolicy Bypass -File clean_admin.ps1 -DriverStore
#
# Hermes 会话里无法自动提权（Start-Process -Verb RunAs 会被 UAC 取消，
# 且 -Verb RunAs 与 -RedirectStandardOutput 参数集冲突），所以由阁下手动以管理员身份运行。
#
# 本文件必须存为 UTF-8 with BOM，否则 PS 5.1 按 GBK 读会吃掉引号导致解析失败。
#
# 只清理 targets.md 中标注为 Safe 的目标，外加 DriverStore 旧驱动（需 -DriverStore 开关）。

param(
    [switch]$DriverStore,       # 清 DriverStore 旧驱动（pnputil 正规卸载路径）
    [switch]$DriverStoreFiles,  # ⭐ 清 DriverStore 旧驱动（文件级直删，绕过 pnputil 引用计数）
    [switch]$DryRun
)

$ErrorActionPreference = 'Continue'
$script:freed = 0
$script:rows  = @()

function Remove-Target {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) { $script:rows += ("[SKIP] {0} : 不存在" -f $Label); return }
    $size = (Get-ChildItem $Path -Recurse -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
    if ($DryRun) { $script:rows += ("[DRY]  {0} : {1:N0} MB" -f $Label, ($size/1MB)); return }
    try {
        Remove-Item $Path -Recurse -Force -EA Stop
        $script:freed += $size
        $script:rows += ("[OK]   {0} : {1:N0} MB" -f $Label, ($size/1MB))
    } catch {
        # 被占用时退化为「清内容保留目录」
        Get-ChildItem $Path -Force -EA SilentlyContinue | Remove-Item -Recurse -Force -EA SilentlyContinue
        $after = (Get-ChildItem $Path -Recurse -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
        $got = $size - $after
        $script:freed += $got
        $script:rows += ("[PART] {0} : {1:N0} MB (目录保留)" -f $Label, ($got/1MB))
    }
}

# 管理员自检
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] 需要管理员权限。请以管理员身份重开 PowerShell 再运行。" -ForegroundColor Red
    exit 1
}

$nv = 'C:\Program Files\NVIDIA Corporation'

# --- Safe: CUDA 开发调试工具（剪辑/游戏用户用不到，几百 MB ~ 1 GB 每个）---
Remove-Target (Join-Path $nv 'Nsight Systems 2022.4.2') 'Nsight Systems (CUDA调试)'
Remove-Target (Join-Path $nv 'Nsight Compute 2022.3.0')  'Nsight Compute (CUDA调试)'

# --- Safe: NVIDIA 安装器残留 ---
Remove-Target (Join-Path $nv 'Installer2') 'NVIDIA Installer2 残留'

# --- Safe: Windows Update 下载缓存（停 wuauserv 再清，不动 TrustedInstaller）---
$wu = 'C:\Windows\SoftwareDistribution\Download'
if (Test-Path $wu) {
    if ($DryRun) {
        $s = (Get-ChildItem $wu -Recurse -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
        $script:rows += ("[DRY]  Windows Update 下载缓存 : {0:N0} MB" -f ($s/1MB))
    } else {
        $s = (Get-ChildItem $wu -Recurse -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
        net stop wuauserv /y 2>&1 | Out-Null
        Get-ChildItem $wu -Force -EA SilentlyContinue | Remove-Item -Recurse -Force -EA SilentlyContinue
        net start wuauserv 2>&1 | Out-Null
        $a = (Get-ChildItem $wu -Recurse -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
        $script:freed += ($s - $a)
        $script:rows += ("[PART] Windows Update 下载缓存 : {0:N0} MB (目录保留)" -f (($s-$a)/1MB))
    }
}

# --- Confirm: DriverStore 旧 NVIDIA 驱动 ---
# 两条路：
#   -DriverStore      → pnputil /delete-driver（正规卸载）。⚠ 实测走不通：
#                        nvami.inf 多版本共存时永远报 "One or more devices are presently installed"，
#                        重启无效（2026-09-22 重启后仍失败）。保留此开关仅为兼容/留证。
#   -DriverStoreFiles → ⭐ 文件级直删 DriverStore 目录，绕过 pnputil 的引用计数。
#                        自动读每个 nvami.inf 的 DriverVer，与当前驱动版本比对，
#                        只删版本低于当前的目录，保留当前版本。删前打印清单。
$dsRepo = 'C:\Windows\System32\DriverStore\FileRepository'

if ($DriverStore) {
    $dsScript = Join-Path $PSScriptRoot 'clean_driverstore.py'
    if (Test-Path $dsScript) {
        $flag = if ($DryRun) { '' } else { '--force' }
        python $dsScript $flag 2>&1 | ForEach-Object { $script:rows += ("       {0}" -f $_) }
    } else {
        $script:rows += "[WARN] 找不到 clean_driverstore.py"
    }
} else {
    $script:rows += "[SKIP] DriverStore 旧驱动 (pnputil 路径) : 未加 -DriverStore 开关"
}

if ($DriverStoreFiles) {
    # 1. 当前驱动版本（registry 权威，比 nvidia-smi 的 616.92 格式更直接可比）
    $curVer = $null
    $cls = 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
    Get-ChildItem $cls -EA SilentlyContinue | ForEach-Object {
        $p = Get-ItemProperty $_.PSPath -EA SilentlyContinue
        if ($p.InfPath -eq 'oem280.inf' -or $p.DriverDesc -match 'RTX 4060') { $curVer = $p.DriverVersion }
    }
    if (-not $curVer) {
        $script:rows += "[WARN] 无法确定当前驱动版本，跳过 DriverStore 文件级清理（保险起见不删）"
    } else {
        $script:rows += ("       当前驱动版本: {0}" -f $curVer)

        # 2. 枚举 nvami 目录 + 读各自的 DriverVer
        $cands = @()
        Get-ChildItem $dsRepo -Directory -Filter 'nvami.inf_amd64_*' -EA SilentlyContinue | ForEach-Object {
            $infFile = Join-Path $_.FullName 'nvami.inf'
            if (Test-Path $infFile) {
                $line = (Select-String -Path $infFile -Pattern '^\s*DriverVer' | Select-Object -First 1).Line
                if ($line -match ',\s*([\d.]+)\s*$') {
                    $ver = $Matches[1]
                    $sz = (Get-ChildItem $_.FullName -Recurse -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
                    $cands += [pscustomobject]@{ Name = $_.Name; Full = $_.FullName; Ver = $ver; Size = $sz }
                }
            }
        }

        if (-not $cands) {
            $script:rows += "       未找到任何 nvami.inf_amd64_* 目录"
        } else {
            # 3. 版本比对：低于当前的删，等于当前的留
            $toDel = $cands | Where-Object { $_.Ver -ne $curVer }
            $keep  = $cands | Where-Object { $_.Ver -eq $curVer }

            foreach ($k in $keep)  { $script:rows += ("       [KEEP] {0} : ver={1} {2:N0} MB (当前驱动)" -f $k.Name, $k.Ver, ($k.Size/1MB)) }
            foreach ($d in $toDel) { $script:rows += ("       [DEL]  {0} : ver={1} {2:N0} MB" -f $d.Name, $d.Ver, ($d.Size/1MB)) }

            if (-not $toDel) {
                $script:rows += "       没有旧版本可删 ✓"
            } elseif ($DryRun) {
                $sum = ($toDel | Measure-Object Size -Sum).Sum
                $script:rows += ("       [DRY]  将释放 {0:N0} MB" -f ($sum/1MB))
            } else {
                foreach ($d in $toDel) {
                    try {
                        Remove-Item $d.Full -Recurse -Force -EA Stop
                        $script:freed += $d.Size
                        $script:rows += ("       [OK]   已删 {0} : {1:N0} MB" -f $d.Name, ($d.Size/1MB))
                    } catch {
                        $script:rows += ("       [FAIL] {0} : {1}" -f $d.Name, $_.Exception.Message)
                    }
                }
                $script:rows += "       ⚠ 已失去回滚到上述旧版驱动的能力（当前驱动不受影响）"
            }
        }
    }
    $script:rows += "       ⚠ 下次驱动更新后重跑本开关，才能清掉本次保留下来的上一版"
} else {
    $script:rows += "[SKIP] DriverStore 旧驱动 (文件级直删) : 未加 -DriverStoreFiles 开关"
}

$script:rows | ForEach-Object { Write-Host $_ }
Write-Host "=============================="
if ($DryRun) {
    Write-Host "预览模式，未删除任何文件。"
} else {
    Write-Host ("释放合计: {0:N2} GB" -f ($script:freed/1GB))
}
Write-Host ("C盘剩余: {0:N2} GiB" -f ((Get-PSDrive C).Free/1GB))
Write-Host "=============================="
