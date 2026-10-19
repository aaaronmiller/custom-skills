# Apply-Improvements.ps1 - checkup 2026-10-13, improvement pass (approved by the user 2026-10-14).
# Reversible changes only. No file deletions, no reboot, no wsl --shutdown, nothing that stops WSL,
# the agents, or their terminals. Every change records its previous state in revert-state.json;
# Revert-Improvements.ps1 -State <that file> undoes it.
#   1. Telemetry v2: register the SYSTEM sampler task, phase 'checkup-20261013'
#   2. Intel Connectivity Performance Suite: stop + disable 3 services
#   3. Logitech Download Assistant: stop leaked instances, disable its startup entry (StartupApproved)
#   4. Process Lasso v3 rules in the live (Desktop) config
#   5. winget: apps that are not running and cannot interrupt the agents
#   6. Defender signatures
#Requires -RunAsAdministrator
[CmdletBinding()]
param([string]$Out = ("C:\performance-diagnostics\checkup-{0}\raw\elevated" -f (Get-Date -Format yyyyMMdd)))
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$log = Join-Path $Out 'apply.log'
$revertFile = Join-Path $Out 'revert-state.json'
function L($m) { $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m; Write-Host $line; Add-Content -Path $log -Value $line -Encoding UTF8 }
$revert = [ordered]@{ created = (Get-Date).ToString('s'); services = @(); startupApproved = @(); lassoIni = $null; lassoIniBackup = $null }
L '=== Apply-Improvements start'

# ---------------------------------------------------------------- 1. telemetry v2
L '--- 1. telemetry v2'
& 'C:\performance-diagnostics\Perf-Telemetry-v2.ps1' -SetPhase 'checkup-20261013' | Out-Null
$r = & 'C:\performance-diagnostics\Perf-Telemetry-v2.ps1' -Register 2>&1 | Out-String
L ("    " + $r.Trim())

# ---------------------------------------------------------------- 2. Intel ICPS
L '--- 2. Intel Connectivity Performance Suite'
foreach ($name in 'Intel Connectivity Network Service', 'IntelConnectService', 'IDBWM') {
    $s = Get-CimInstance Win32_Service -Filter "Name='$name'" -ErrorAction SilentlyContinue
    if (-not $s) { L "    $name : not present"; continue }
    $mb = 0; if ($s.ProcessId) { try { $mb = [math]::Round((Get-Process -Id $s.ProcessId -ErrorAction Stop).PrivateMemorySize64 / 1MB) } catch {} }
    $revert.services += [ordered]@{ name = $name; startMode = $s.StartMode; state = $s.State }
    Stop-Service -Name $name -Force -ErrorAction SilentlyContinue
    Set-Service -Name $name -StartupType Disabled -ErrorAction SilentlyContinue
    $a = Get-CimInstance Win32_Service -Filter "Name='$name'"
    L ("    {0,-36} {1}/{2} -> {3}/{4}  (held ~{5} MB private)" -f $name, $s.StartMode, $s.State, $a.StartMode, $a.State, $mb)
}

# ---------------------------------------------------------------- 3. Logitech Download Assistant
L '--- 3. Logitech Download Assistant'
$procs = @(Get-Process | Where-Object { $_.Name -like 'logi_download_assistant*' })
L ("    stopping {0} instance(s)" -f $procs.Count)
$procs | Stop-Process -Force -ErrorAction SilentlyContinue
$sa = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
$valName = 'Logi Download Assistant'
if (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name $valName -ErrorAction SilentlyContinue) {
    if (-not (Test-Path $sa)) { New-Item -Path $sa -Force | Out-Null }
    $prev = (Get-ItemProperty $sa -Name $valName -ErrorAction SilentlyContinue).$valName
    $revert.startupApproved += [ordered]@{ key = $sa; name = $valName; previous = $(if ($prev) { [Convert]::ToBase64String($prev) } else { $null }) }
    [byte[]]$val = @(3, 0, 0, 0) + [BitConverter]::GetBytes((Get-Date).ToFileTime())
    Set-ItemProperty -Path $sa -Name $valName -Value $val -Type Binary
    L "    startup entry disabled (Task Manager > Startup apps can re-enable it)"
} else { L "    no HKLM Run entry named '$valName'" }

# ---------------------------------------------------------------- 4. Process Lasso v3 rules
L '--- 4. Process Lasso v3 rules'
$cfgDir = (Get-ItemProperty 'HKLM:\SOFTWARE\ProcessLasso' -Name ConfigFolderEx -ErrorAction SilentlyContinue).ConfigFolderEx
$ini = if ($cfgDir) { Join-Path $cfgDir 'prolasso.ini' } else { $null }
if (-not $ini -or -not (Test-Path -LiteralPath $ini)) {
    L "    live ini not found via ConfigFolderEx ($cfgDir) - SKIPPED"
} else {
    $bak = "$ini.checkup-bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Copy-Item -LiteralPath $ini -Destination $bak -Force
    $revert.lassoIni = $ini; $revert.lassoIniBackup = $bak
    L "    live ini: $ini"; L "    backup  : $bak"
    $gui = Get-Process -Name ProcessLasso -ErrorAction SilentlyContinue
    if ($gui) { $gui | Stop-Process -Force; Start-Sleep -Seconds 2; L '    GUI closed (governor keeps enforcing; it reloads the file itself)' }
    $text = [IO.File]::ReadAllText($ini, [Text.Encoding]::Unicode)
    $rules = [ordered]@{
        'DefaultAffinitiesEx'      = 'notepad.exe,0,0-7,notepad++.exe,0,0-7,everything.exe,0,8-15,tailscaled.exe,0,8-15,usbipd.exe,0,8-15,abdownloadmanager.exe,0,8-15,localsend_app.exe,0,8-15,logi_download_assistant*.exe,0,8-15,searchindexer.exe,0,8-15,esrv.exe,0,8-15,esrv_svc.exe,0,8-15,mdnsresponder.exe,0,8-15,schedul2.exe,0,8-15,googledrivefs.exe,0,8-15,crossdeviceservice.exe,0,8-15,intel_pie_service.exe,0,8-15'
        'CPUSets'                  = 'discord.exe,(0/8-15),slack.exe,(0/8-15),beeper.exe,(0/8-15),joplin.exe,(0/8-15),phoneexperiencehost.exe,(0/8-15),msedgewebview2.exe,(0/8-15)'
        'EfficiencyMode'           = 'wezterm-gui.exe,0,openwhispr.exe,0,sherpa-onnx-ws-win32-x64.exe,0,claude.exe,0,codex.exe,0,code.exe,0,logi_download_assistant*.exe,1,googledrivefs.exe,1,crossdeviceservice.exe,1,searchindexer.exe,1,mdnsresponder.exe,1,schedul2.exe,1,intel_pie_service.exe,1'
        'DefaultIOPriorities'      = 'searchindexer.exe,0,logi_download_assistant*.exe,0,everything.exe,1,googledrivefs.exe,1,schedul2.exe,1,crossdeviceservice.exe,1'
        'DefaultMemoryPriorities'  = 'discord.exe,2,slack.exe,2,beeper.exe,2,joplin.exe,2,phoneexperiencehost.exe,2,googledrivefs.exe,1,crossdeviceservice.exe,1,searchindexer.exe,1,intel_pie_service.exe,1,logi_download_assistant*.exe,0'
        'InstanceLimitedProcesses' = 'logi_download_assistant*.exe;1'
        'ApplyInstanceCountLimitsToAllUsers' = 'true'
        'DefaultPriorities'        = 'discord.exe,below normal,slack.exe,below normal,beeper.exe,below normal,msedgewebview2.exe,below normal,googledrivefs.exe,below normal,crossdeviceservice.exe,below normal,joplin.exe,below normal,phoneexperiencehost.exe,below normal'
        'OocExclusions'            = 'claude.exe,codex.exe,openwhispr.exe,sherpa-onnx-ws-win32-x64.exe,vmmemwsl,vmmemwsl.exe,wezterm-gui.exe'
    }
    foreach ($k in $rules.Keys) {
        $pat = '(?m)^[ \t]*' + [regex]::Escape($k) + '=.*$'
        $n = ([regex]::Matches($text, $pat)).Count
        if ($n) { $text = [regex]::Replace($text, $pat, "$k=$($rules[$k])"); L "    set $k ($n line(s))" }
        else { $text = $text.TrimEnd("`r", "`n") + "`r`n$k=$($rules[$k])`r`n"; L "    added $k" }
    }
    [IO.File]::WriteAllText($ini, $text, (New-Object System.Text.UnicodeEncoding($false, $true)))
    L '    written; waiting 15 s for the governor to reload'
    Start-Sleep -Seconds 15
    $lg = Join-Path (Split-Path $cfgDir -Parent) 'processlasso.log'
    if (Test-Path -LiteralPath $lg) { Get-Content -LiteralPath $lg -Tail 8 | ForEach-Object { L "    log> $_" } }
    $chk = Get-Process | Where-Object { $_.Name -in 'mDNSResponder', 'schedul2', 'GoogleDriveFS', 'Everything', 'tailscaled' } | ForEach-Object { try { '{0}=0x{1:X4}' -f $_.Name, [int64]$_.ProcessorAffinity } catch { "$($_.Name)=denied" } }
    L ('    affinity check (expect 0xFF00): ' + ($chk -join ' '))
}

# ---------------------------------------------------------------- 5. winget
L '--- 5. winget (not-running apps; Git, Tailscale, radio drivers, WSL packages deferred)'
foreach ($id in 'Microsoft.EdgeWebView2Runtime', 'Microsoft.Edge', 'Microsoft.DotNet.Runtime.8', 'Microsoft.DotNet.AspNetCore.8', 'Microsoft.DotNet.DesktopRuntime.8', 'Microsoft.DotNet.DesktopRuntime.9', 'Microsoft.DotNet.DesktopRuntime.10', 'Microsoft.PowerToys', 'Perplexity.Comet', 'Amazon.Kiro', 'UnslothAI.Unsloth') {
    $o = winget upgrade --id $id --exact --silent --accept-package-agreements --accept-source-agreements --disable-interactivity 2>&1 | Out-String
    $tail = ($o -split "`r?`n" | Where-Object { $_.Trim() -and $_ -notmatch '^\s*[-\\|/]\s*$' -and $_ -notmatch '[\u2580-\u259F]' } | Select-Object -Last 1)
    L ("    {0,-36} exit={1}  {2}" -f $id, $LASTEXITCODE, $tail)
}

# ---------------------------------------------------------------- 6. Defender
L '--- 6. Defender signatures'
try { Update-MpSignature -ErrorAction Stop; $s = Get-MpComputerStatus; L ("    signature {0}, age {1} d" -f $s.AntivirusSignatureVersion, $s.AntivirusSignatureAge) } catch { L "    failed: $($_.Exception.Message)" }

$revert | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $revertFile
L "revert state -> $revertFile"
L ('RebootPending: ' + (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'))
L '=== Apply-Improvements done'
