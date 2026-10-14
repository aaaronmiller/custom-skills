# Elevated-Audit.ps1 - admin-only checks for the periodic SPECTRE-16 checkup (first used 2026-10-13).
# NO reboot, NO wsl --shutdown, NO service restarts that affect WSL/agents.
# Only writes: (a) log files under raw\elevated, (b) SFC's own repairs,
# (c) un-ticking "Allow the computer to turn off this device" on the wireless keyboard/mouse
#     HID entries (re-applies the 2026-10 input fix if a driver update re-enabled it).
# Everything else is read-only. Takes 30-40 min (SFC + DISM ScanHealth dominate).
#Requires -RunAsAdministrator
param([string]$Out = ("C:\performance-diagnostics\checkup-{0}\raw\elevated" -f (Get-Date -Format yyyyMMdd)))
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$log = Join-Path $Out 'pass1.log'
function L($m) { $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m; $line | Tee-Object -FilePath $log -Append }
function J($obj, $name) { $obj | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 (Join-Path $Out $name) }
L "=== Elevated-Pass1 start (elevated=$(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)))"

# ---------------- Task 3 preconditions ----------------
$rbKey = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
$pre = Test-Path $rbKey
L "RebootPending (pre): $pre"
$ci = Get-ComputerInfo -Property WindowsProductName, WindowsVersion, OsBuildNumber, OsHardwareAbstractionLayer
J $ci 'computerinfo.json'
L ("Build: {0} / {1} / {2}" -f $ci.WindowsProductName, $ci.WindowsVersion, $ci.OsBuildNumber)

$svc = Get-Service wuauserv, bits, cryptsvc, UsoSvc, TrustedInstaller, WaaSMedicSvc | Select-Object Name, Status, StartType
J $svc 'wu-services.json'
$pol  = Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue
$polA = Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU' -ErrorAction SilentlyContinue
L ("WU policy keys present: WindowsUpdate={0} AU={1}" -f [bool]$pol, [bool]$polA)

# ---------------- Task 4: WER triage (read-only) ----------------
$wer = 'C:\ProgramData\Microsoft\Windows\WER\ReportArchive'
$werItems = Get-ChildItem $wer -Directory -Force -ErrorAction SilentlyContinue
$werRows = $werItems | ForEach-Object {
  $parts = $_.Name -split '_'
  [pscustomobject]@{ Kind = $parts[0]; App = if ($parts.Count -gt 1) { $parts[1] } else { '' }; Name = $_.Name; Modified = $_.LastWriteTime }
}
J $werRows 'wer-reportarchive.json'
L "WER ReportArchive entries: $($werItems.Count)"
$werRows | Group-Object Kind | ForEach-Object { L ("  {0}: {1}" -f $_.Name, $_.Count) }
foreach ($app in 'dwm.exe','wslservice.exe') {
  $n = $werRows | Where-Object { $_.App -like "$app*" } | Sort-Object Modified -Descending | Select-Object -First 1
  L ("  newest {0}: {1}" -f $app, $(if ($n) { $n.Modified } else { 'none' }))
}
$werQ = Get-ChildItem 'C:\ProgramData\Microsoft\Windows\WER\ReportQueue' -Directory -Force -ErrorAction SilentlyContinue
L "WER ReportQueue entries: $($werQ.Count)"

# ---------------- Task 2 step 6: HID power management ----------------
$pm = Get-CimInstance -Namespace root\wmi -ClassName MSPower_DeviceEnable -ErrorAction SilentlyContinue
$pmRows = foreach ($p in $pm) {
  $id = ($p.InstanceName -replace '_\d+$','')
  $dev = Get-PnpDevice -InstanceId $id -ErrorAction SilentlyContinue
  [pscustomobject]@{ InstanceName = $p.InstanceName; Device = $dev.FriendlyName; Class = $dev.Class; Enabled = $p.Enable }
}
$pmInput = $pmRows | Where-Object { $_.InstanceName -match 'VID_046D|00001812|BTHLE|PID_B017|D88512A3F888|C85696FA97A5' -or $_.Class -in 'Keyboard','Mouse' -or $_.Device -match 'Bluetooth' }
J $pmInput 'hid-power-mgmt-before.json'
L "Power-management entries for input/BT devices: $(@($pmInput).Count)"
foreach ($r in $pmInput) { L ("  before: allow-off={0}  {1}  [{2}]" -f $r.Enabled, $r.Device, $r.InstanceName) }
# Authorized write: wireless keyboard/mouse HID entries only (Logitech receiver/BLE mouse, Varmilo BLE keyboard).
$targets = $pm | Where-Object { $_.Enable -eq $true -and $_.InstanceName -match 'VID_046D|PID_B017|D88512A3F888|C85696FA97A5' }
foreach ($t in $targets) {
  try { Set-CimInstance -InputObject $t -Property @{ Enable = $false } -ErrorAction Stop; L "  UNCHECKED allow-off: $($t.InstanceName)" }
  catch { L "  FAILED to uncheck $($t.InstanceName): $($_.Exception.Message)" }
}
if (-not $targets) { L "  no wireless kb/mouse entry had allow-off checked (nothing changed)" }

# ---------------- extra admin-only health data (read-only) ----------------
L "Collecting storage reliability, shadow storage, BitLocker, Defender, Lasso counters..."
Get-PhysicalDisk | ForEach-Object { $_ | Get-StorageReliabilityCounter -ErrorAction SilentlyContinue | Select-Object @{n='Disk';e={$_.DeviceId}}, Temperature, TemperatureMax, Wear, PowerOnHours, ReadErrorsTotal, WriteErrorsTotal, ReadErrorsUncorrected, WriteErrorsUncorrected } | ForEach-Object { $_ } | ConvertTo-Json | Out-File -Encoding UTF8 (Join-Path $Out 'storage-reliability.json')
(vssadmin list shadowstorage 2>&1) | Out-File -Encoding UTF8 (Join-Path $Out 'vss-shadowstorage.txt')
(vssadmin list shadows 2>&1) | Select-Object -First 80 | Out-File -Encoding UTF8 (Join-Path $Out 'vss-shadows.txt')
(manage-bde -status C: 2>&1) | Out-File -Encoding UTF8 (Join-Path $Out 'bitlocker.txt')
Get-MpComputerStatus -ErrorAction SilentlyContinue | Select-Object AMProductVersion, AMEngineVersion, AntivirusSignatureVersion, AntivirusSignatureAge, RealTimeProtectionEnabled, IsTamperProtected, QuickScanAge, FullScanAge | ConvertTo-Json | Out-File -Encoding UTF8 (Join-Path $Out 'defender.json')
(Get-MpPreference -ErrorAction SilentlyContinue).ExclusionPath | Out-File -Encoding UTF8 (Join-Path $Out 'defender-exclusion-paths.txt')
$cnt = 'HKLM:\SOFTWARE\Bitsum\Counters'
if (Test-Path $cnt) { Get-ChildItem $cnt -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.Name } | Out-File -Encoding UTF8 (Join-Path $Out 'lasso-counter-keys.txt') }
# Affinity of elevated/background processes (verifies Lasso E-core pins; unelevated reads 0x0)
Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(Everything|tailscaled|usbipd|ABDownloadManager|localsend_app|logi_download_assistant.*|SearchIndexer|esrv|esrv_svc|vmmemWSL|MsMpEng|claude|codex|wezterm-gui|chrome|Code|OpenWhispr)$' } |
  ForEach-Object { try { [pscustomobject]@{ Name=$_.Name; Id=$_.Id; Affinity=('0x{0:X4}' -f [int64]$_.ProcessorAffinity); Priority="$($_.PriorityClass)"; WS_MB=[math]::Round($_.WorkingSet64/1MB) } } catch { [pscustomobject]@{ Name=$_.Name; Id=$_.Id; Affinity='denied'; Priority=''; WS_MB=0 } } } |
  Sort-Object Name | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $Out 'process-affinity.csv')
# Sizes of admin-only caches
$sz = foreach ($p in 'C:\Windows\Temp','C:\Windows\SoftwareDistribution\Download','C:\Windows\SoftwareDistribution\DataStore','C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization','C:\Windows\Logs\CBS','C:\Windows\Installer','C:\Windows\Installer\$PatchCache$','C:\ProgramData\Package Cache','C:\Windows\LiveKernelReports','C:\Windows\Minidump','C:\Windows\Prefetch','C:\$WINDOWS.~BT','C:\$SysReset','C:\Windows\WinSxS\Backup') {
  $m = Get-ChildItem $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum
  [pscustomobject]@{ Path=$p; Files=$m.Count; GB=[math]::Round($m.Sum/1GB,2) }
}
$sz | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $Out 'admin-cache-sizes.csv')
foreach ($r in $sz) { L ("  {0,-90} {1,8} GB" -f $r.Path, $r.GB) }
try { Get-DeliveryOptimizationPerfSnap -ErrorAction Stop | ConvertTo-Json | Out-File -Encoding UTF8 (Join-Path $Out 'delivery-opt.json') } catch {}
(powercfg /batteryreport /output (Join-Path $Out 'battery-report.html') 2>&1) | Out-Null
(powercfg /list 2>&1) | Out-File -Encoding UTF8 (Join-Path $Out 'powercfg-list.txt')

# ---------------- Task 3: SFC then DISM ScanHealth ----------------
L "Running sfc /scannow (10-25 min)..."
$sfcOut = Join-Path $Out 'sfc.txt'
cmd /c "sfc /scannow > `"$sfcOut`" 2>&1"
L "sfc exit code: $LASTEXITCODE"
$sfcText = (Get-Content $sfcOut -Raw -Encoding Unicode) -replace "`0",''
$sfcFinal = ($sfcText -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 3) -join ' | '
L "sfc final: $sfcFinal"

L "Running DISM /ScanHealth (5-20 min)..."
$dismOut = Join-Path $Out 'dism-scanhealth.txt'
DISM /Online /Cleanup-Image /ScanHealth /English *> $dismOut
L "DISM ScanHealth exit code: $LASTEXITCODE"
L ("DISM tail: " + ((Get-Content $dismOut | Where-Object { $_.Trim() } | Select-Object -Last 3) -join ' | '))

L "Running DISM /AnalyzeComponentStore (read-only)..."
DISM /Online /Cleanup-Image /AnalyzeComponentStore /English *> (Join-Path $Out 'dism-analyze.txt')
L "AnalyzeComponentStore exit code: $LASTEXITCODE"

# CBS 0x800f0805 check + reboot flag (post)
$cbs = 'C:\Windows\Logs\CBS\CBS.log'
$hits = Select-String -Path $cbs -Pattern '0x800f0805' -ErrorAction SilentlyContinue | Select-Object -Last 8
$hits | ForEach-Object { $_.Line } | Out-File -Encoding UTF8 (Join-Path $Out 'cbs-0x800f0805.txt')
L "CBS 0x800f0805 lines in current CBS.log: $(@($hits).Count) (last: $(if ($hits) { $hits[-1].Line.Substring(0,[Math]::Min(120,$hits[-1].Line.Length)) }))"
Select-String -Path $cbs -Pattern 'corrupt|Corruption|CSI Payload' -ErrorAction SilentlyContinue | Select-Object -Last 60 | ForEach-Object { $_.Line } | Out-File -Encoding UTF8 (Join-Path $Out 'cbs-corruption-lines.txt')
$post = Test-Path $rbKey
L "RebootPending (post): $post"
L "=== Elevated-Pass1 done"
