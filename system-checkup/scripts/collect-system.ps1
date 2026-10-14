# collect-system.ps1 - read-only system + software inventory for the periodic checkup.
# Writes everything into <OutDir> (default: ..\raw relative to this script). ASCII only.
[CmdletBinding()]
param([string]$OutDir = (Join-Path (Split-Path $PSScriptRoot -Parent) 'raw'))
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
function Out-Csv2($obj, $name) { $obj | Export-Csv -NoTypeInformation -Encoding UTF8 -Path (Join-Path $OutDir $name) }
function Out-Txt($text, $name) { $text | Out-File -Encoding UTF8 -FilePath (Join-Path $OutDir $name) }
$t0 = Get-Date

# --- OS / hardware --------------------------------------------------------------
$os = Get-CimInstance Win32_OperatingSystem
$cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$bios = Get-CimInstance Win32_BIOS
$cs = Get-CimInstance Win32_ComputerSystem
$sys = [ordered]@{
  Collected = (Get-Date).ToString('s'); Computer = $env:COMPUTERNAME
  OS = $os.Caption; Build = "$($cv.CurrentBuild).$($cv.UBR)"; BuildLab = $cv.BuildLabEx; Display = $cv.DisplayVersion
  InstallDate = $os.InstallDate.ToString('s'); LastBoot = $os.LastBootUpTime.ToString('s')
  BIOS = "$($bios.Manufacturer) $($bios.SMBIOSBIOSVersion) $($bios.ReleaseDate)"; Model = "$($cs.Manufacturer) $($cs.Model)"
  RAM_GB = [math]::Round($cs.TotalPhysicalMemory/1GB,1); CommitLimitMB = [math]::Round($os.TotalVirtualMemorySize/1KB); CommitFreeMB = [math]::Round($os.FreeVirtualMemory/1KB)
  FreeRamMB = [math]::Round($os.FreePhysicalMemory/1KB)
}
$sys | ConvertTo-Json | Out-File -Encoding UTF8 (Join-Path $OutDir 'system.json')
Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage | ForEach-Object { $_ } | ConvertTo-Json | Out-File -Encoding UTF8 (Join-Path $OutDir 'pagefile.json')
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, VolumeName, FileSystem, @{n='SizeGB';e={[math]::Round($_.Size/1GB,1)}}, @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,1)}} | ForEach-Object { $_ } | ConvertTo-Json | Out-File -Encoding UTF8 (Join-Path $OutDir 'disks.json')

# --- Installed programs (registry) ---------------------------------------------
$keys = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
$progs = foreach ($k in $keys) { Get-ItemProperty $k -ErrorAction SilentlyContinue | Where-Object DisplayName | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation, @{n='SizeMB';e={[math]::Round($_.EstimatedSize/1KB,1)}}, @{n='Scope';e={ if ($k -like 'HKCU*') {'user'} else {'machine'} }} }
Out-Csv2 ($progs | Sort-Object DisplayName) 'installed-programs.csv'
Get-AppxPackage | Select-Object Name, Version, Publisher, InstallLocation | Sort-Object Name | ForEach-Object { $_ } | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir 'appx.csv')

# --- Drivers --------------------------------------------------------------------
Get-CimInstance Win32_PnPSignedDriver | Where-Object { $_.DeviceClass -in 'DISPLAY','NET','SYSTEM','MEDIA','BLUETOOTH','HDC','SCSIADAPTER','USB','CAMERA','BIOMETRIC','SOFTWARECOMPONENT','EXTENSION','FIRMWARE' -or $_.DeviceName -match 'Intel|Arc|Iris|Wi-Fi|Wireless|Bluetooth|Realtek|HP ' } |
  Select-Object DeviceClass, DeviceName, Manufacturer, DriverVersion, @{n='DriverDate';e={ if ($_.DriverDate) { $_.DriverDate.ToString('yyyy-MM-dd') } }}, InfName |
  Sort-Object DeviceClass, DeviceName -Unique | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir 'drivers.csv')

# --- Processes / services / tasks / startup --------------------------------------
Get-Process | Select-Object Name, Id, @{n='WS_MB';e={[math]::Round($_.WorkingSet64/1MB,1)}}, @{n='Private_MB';e={[math]::Round($_.PrivateMemorySize64/1MB,1)}}, @{n='CPU_s';e={[math]::Round($_.CPU,1)}}, Path, @{n='Start';e={ try { $_.StartTime.ToString('s') } catch { '' } }} |
  Sort-Object Private_MB -Descending | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir 'processes.csv')
Get-CimInstance Win32_Service | Select-Object Name, DisplayName, State, StartMode, PathName | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir 'services.csv')
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' } | ForEach-Object { $i = $_ | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue; [pscustomobject]@{Path=$_.TaskPath; Name=$_.TaskName; State=$_.State; LastRun=$i.LastRunTime; LastResult=('0x{0:X}' -f $i.LastTaskResult); Next=$i.NextRunTime; Action=(($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join ' | ')} } |
  Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir 'tasks-nonms.csv')
$startup = @()
foreach ($rk in 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run','HKLM:\Software\Microsoft\Windows\CurrentVersion\Run','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run') {
  $p = Get-ItemProperty $rk -ErrorAction SilentlyContinue
  if ($p) { $p.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object { $startup += [pscustomobject]@{Source=$rk; Name=$_.Name; Command=$_.Value} } }
}
foreach ($sf in "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup","$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup") { Get-ChildItem $sf -ErrorAction SilentlyContinue | ForEach-Object { $startup += [pscustomobject]@{Source=$sf; Name=$_.Name; Command=$_.FullName} } }
Out-Csv2 $startup 'startup.csv'

# --- Package managers -----------------------------------------------------------
$pm = [ordered]@{}
function Try-Run([string]$label, [scriptblock]$sb) { try { $r = & $sb 2>&1 | Out-String } catch { $r = "ERROR: $($_.Exception.Message)" }; $pm[$label] = $r }
Try-Run 'node' { node --version }
Try-Run 'npm' { npm --version }
Try-Run 'pnpm' { pnpm --version }
Try-Run 'bun' { bun --version }
Try-Run 'python' { python --version }
Try-Run 'uv' { uv --version }
Try-Run 'git' { git --version }
Try-Run 'gh' { gh --version }
Try-Run 'pwsh' { pwsh -NoProfile -Command '$PSVersionTable.PSVersion.ToString()' }
Try-Run 'wsl' { (wsl.exe --version) -replace "`0", '' }
Try-Run 'winget' { winget --version }
Try-Run 'scoop' { scoop --version }
Try-Run 'choco' { choco --version }
Try-Run 'npm-global' { npm ls -g --depth=0 }
Try-Run 'npm-outdated-global' { npm outdated -g }
Try-Run 'npm-cache-path' { npm config get cache }
Try-Run 'pnpm-global' { pnpm ls -g }
Try-Run 'pnpm-store-path' { pnpm store path }
Try-Run 'pip-outdated' { python -m pip list --outdated --disable-pip-version-check }
Try-Run 'scoop-list' { scoop list }
Try-Run 'scoop-status' { scoop status }
$pm | ConvertTo-Json -Depth 3 | Out-File -Encoding UTF8 (Join-Path $OutDir 'package-managers.json')

# winget is slow; keep it last. --accept-source-agreements avoids an interactive prompt.
try {
  winget list --accept-source-agreements --disable-interactivity 2>&1 | Out-File -Encoding UTF8 (Join-Path $OutDir 'winget-list.txt')
  winget upgrade --include-unknown --accept-source-agreements --disable-interactivity 2>&1 | Out-File -Encoding UTF8 (Join-Path $OutDir 'winget-upgrade.txt')
} catch { "winget failed: $($_.Exception.Message)" | Out-File (Join-Path $OutDir 'winget-upgrade.txt') }

"collect-system done in $([math]::Round(((Get-Date)-$t0).TotalSeconds))s -> $OutDir"
