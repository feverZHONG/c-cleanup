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
    [switch]$DriverStore,   # 加此开关才清 DriverStore 旧 NVIDIA 驱动
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

# --- Confirm: DriverStore 旧 NVIDIA 驱动（约 2.6 GB/份，删掉会失去回滚旧驱动的能力）---
if ($DriverStore) {
    $dsScript = Join-Path $PSScriptRoot 'clean_driverstore.py'
    if (Test-Path $dsScript) {
        $flag = if ($DryRun) { '' } else { '--force' }
        python $dsScript $flag 2>&1 | ForEach-Object { $script:rows += ("       {0}" -f $_) }
    } else {
        $script:rows += "[WARN] 找不到 clean_driverstore.py"
    }
} else {
    $script:rows += "[SKIP] DriverStore 旧驱动 : 未加 -DriverStore 开关"
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
