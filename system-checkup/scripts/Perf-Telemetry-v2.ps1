# Perf-Telemetry-v2.ps1 - 5-minute performance sampler (SYSTEM scheduled task) for SPECTRE-16.
# Supersedes Perf-Telemetry.ps1 (v1). v1 data (perf-samples.csv / perf-processes.csv) is left untouched
# as history; v2 writes monthly files under C:\performance-diagnostics\telemetry\.
#
# Why v2 exists (both v1 failure modes were silent):
#   * v1 -Register used a -Once trigger with no RepetitionDuration -> the trigger expired and the task
#     vanished (2026-08-15). The 2026-09-10 re-registration also left no task behind. v2 registers a
#     10-year repetition + an AtStartup trigger, verifies the task after registering, and writes a
#     heartbeat so -Status (and the monthly checkup skill) can detect a dead sampler within minutes.
#   * v1 sampled working set only. The problem on this box is COMMIT (16 GB soldered RAM + WSL), so v2
#     records commit charge/limit, standby, modified list, disk throughput and per-process private bytes.
#
# Usage:
#   .\Perf-Telemetry-v2.ps1                       # take one sample (what the task runs)
#   .\Perf-Telemetry-v2.ps1 -Register [-Phase x]  # admin: (re)register the SYSTEM task, verify it
#   .\Perf-Telemetry-v2.ps1 -Unregister           # admin
#   .\Perf-Telemetry-v2.ps1 -SetPhase <label>     # tag subsequent samples (shared with v1)
#   .\Perf-Telemetry-v2.ps1 -Status               # task state, last sample age, error count
#   .\Perf-Telemetry-v2.ps1 -Report [-Days 30]    # per-phase percentiles
[CmdletBinding()]
param(
    [string]$Phase,
    [switch]$Register,
    [switch]$Unregister,
    [string]$SetPhase,
    [switch]$Status,
    [switch]$Report,
    [int]$Days = 30
)
$ErrorActionPreference = 'Stop'
$Root      = 'C:\performance-diagnostics'
$Dir       = Join-Path $Root 'telemetry'
$PhaseFile = Join-Path $Root 'current-phase.txt'
$TaskName  = 'Perf Telemetry Sampler'
$Month     = Get-Date -Format 'yyyy-MM'
$Csv       = Join-Path $Dir "perf-samples-$Month.csv"
$ProcCsv   = Join-Path $Dir "perf-processes-$Month.csv"
$Heartbeat = Join-Path $Dir 'heartbeat.txt'
$ErrLog    = Join-Path $Dir 'errors.log'
New-Item -ItemType Directory -Force -Path $Dir | Out-Null

# Process names tracked individually (Get-Process names, no .exe)
$Tracked = @('chrome','msedge','msedgewebview2','Comet','vmmemWSL','wslservice','wezterm-gui','Code','claude','codex','node',
             'Discord','slack','Beeper','Obsidian','OpenWhispr','Everything','MsMpEng','SearchIndexer','explorer','dwm',
             'ProcessLasso','ProcessGovernor','logi_download_assistant-2.0.1020-win64','CrossDeviceService','Joplin',
             'Antigravity','Kiro','GoogleDriveFS','tailscaled','localsend_app','powershell','pwsh')

function Write-Err([string]$msg) { "[{0}] {1}" -f (Get-Date -Format 's'), $msg | Add-Content -Path $ErrLog -Encoding UTF8 }

if ($SetPhase) {
    Set-Content -Path $PhaseFile -Value $SetPhase -Encoding ASCII
    Write-Host "Phase set to '$SetPhase'." -ForegroundColor Green
    return
}

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host 'Sampler unregistered.' -ForegroundColor Yellow
    return
}

if ($Register) {
    if ($Phase) { Set-Content -Path $PhaseFile -Value $Phase -Encoding ASCII }
    $self = $PSCommandPath
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument "-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$self`""
    # 10 years: [TimeSpan]::MaxValue serialises out of range (0x80041318).
    $rep  = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
    $boot = New-ScheduledTaskTrigger -AtStartup
    $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
              -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 3) -Priority 7
    $prin = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($rep, $boot) -Settings $set -Principal $prin `
        -Description 'SPECTRE-16 5-min perf sampler (Perf-Telemetry-v2.ps1). Checked by the monthly system-checkup skill.' -Force | Out-Null
    $t = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $t) { Write-Host 'REGISTRATION FAILED: task not present after Register-ScheduledTask' -ForegroundColor Red; exit 1 }
    $end = $t.Triggers[0].Repetition.Duration
    Write-Host ("Registered '{0}': state={1} interval={2} duration={3} phase='{4}'" -f $TaskName, $t.State, $t.Triggers[0].Repetition.Interval, $end, (Get-Content $PhaseFile -ErrorAction SilentlyContinue)) -ForegroundColor Green
    return
}

if ($Status) {
    $t = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $i = if ($t) { $t | Get-ScheduledTaskInfo } else { $null }
    $hb = if (Test-Path $Heartbeat) { Get-Item $Heartbeat } else { $null }
    $age = if ($hb) { [math]::Round(((Get-Date) - $hb.LastWriteTime).TotalMinutes, 1) } else { $null }
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    [pscustomobject]@{
        # A SYSTEM task is invisible to an unelevated shell, so health is judged by the heartbeat.
        TaskPresent   = if ($t) { $true } elseif ($admin) { $false } else { 'not visible without admin' }
        TaskState     = if ($t) { "$($t.State)" } elseif ($admin) { 'MISSING' } else { 'unknown (run elevated to see)' }
        LastRun       = if ($i) { $i.LastRunTime } else { $null }
        LastResult    = if ($i) { '0x{0:X}' -f $i.LastTaskResult } else { $null }
        NextRun       = if ($i) { $i.NextRunTime } else { $null }
        LastSampleMin = $age
        Healthy       = [bool]($age -ne $null -and $age -lt 15)
        Phase         = (Get-Content $PhaseFile -ErrorAction SilentlyContinue)
        ErrorLines    = if (Test-Path $ErrLog) { (Get-Content $ErrLog).Count } else { 0 }
        CurrentCsv    = $Csv
    }
    return
}

if ($Report) {
    $files = Get-ChildItem $Dir -Filter 'perf-samples-*.csv' | Sort-Object Name
    if (-not $files) { Write-Host 'No v2 samples yet.' -ForegroundColor Red; return }
    $since = (Get-Date).AddDays(-$Days)
    $data = $files | ForEach-Object { Import-Csv $_.FullName } | Where-Object { [datetime]$_.Timestamp -ge $since }
    function P([double[]]$s, [double]$p) { if (-not $s) { return $null }; $s = $s | Sort-Object; $s[[math]::Floor(($s.Count - 1) * $p)] }
    $data | Group-Object Phase | ForEach-Object {
        $g = $_.Group
        [pscustomobject]@{
            Phase = $_.Name; Samples = $g.Count
            RamPct_p50 = P ($g.RamPct | ForEach-Object { [double]$_ }) 0.5;  RamPct_p95 = P ($g.RamPct | ForEach-Object { [double]$_ }) 0.95
            CommitPct_p50 = P ($g.CommitPct | ForEach-Object { [double]$_ }) 0.5; CommitPct_p95 = P ($g.CommitPct | ForEach-Object { [double]$_ }) 0.95
            HardFaults_p50 = P ($g.HardFaultsSec | ForEach-Object { [double]$_ }) 0.5; HardFaults_p95 = P ($g.HardFaultsSec | ForEach-Object { [double]$_ }) 0.95
            AvailMB_p05 = P ($g.AvailMB | ForEach-Object { [double]$_ }) 0.05
            Over90Commit = ($g | Where-Object { [double]$_.CommitPct -ge 90 }).Count
        }
    } | Format-Table -AutoSize
    return
}

# ------------------------------------------------------------------ take one sample
try {
    $phaseNow = if ($Phase) { $Phase } elseif (Test-Path $PhaseFile) { (Get-Content $PhaseFile -Raw).Trim() } else { 'unlabeled' }
    $counters = @(
        '\Memory\Available MBytes', '\Memory\Committed Bytes', '\Memory\Commit Limit', '\Memory\Pages Input/sec',
        '\Memory\Standby Cache Normal Priority Bytes', '\Memory\Standby Cache Reserve Bytes', '\Memory\Standby Cache Core Bytes',
        '\Memory\Modified Page List Bytes', '\Memory\Pool Nonpaged Bytes', '\Paging File(_Total)\% Usage',
        '\Processor(_Total)\% Processor Time', '\Processor Information(_Total)\% Processor Performance',
        '\PhysicalDisk(_Total)\Disk Read Bytes/sec', '\PhysicalDisk(_Total)\Disk Write Bytes/sec', '\PhysicalDisk(_Total)\Avg. Disk Queue Length'
    )
    $c = @{}
    try {
        (Get-Counter -Counter $counters -ErrorAction SilentlyContinue).CounterSamples | ForEach-Object {
            $c[($_.Path -replace '^\\\\[^\\]+', '').ToLower()] = $_.CookedValue
        }
    } catch { Write-Err "Get-Counter: $($_.Exception.Message)" }
    function CV([string]$k) { $v = $c[$k.ToLower()]; if ($null -eq $v) { -1 } else { $v } }

    $os = Get-CimInstance Win32_OperatingSystem
    $totalMB = [math]::Round($os.TotalVisibleMemorySize / 1KB)
    $availMB = [math]::Round((CV '\memory\available mbytes'))
    $commit  = CV '\memory\committed bytes'; $limit = CV '\memory\commit limit'
    $standby = (CV '\memory\standby cache normal priority bytes') + (CV '\memory\standby cache reserve bytes') + (CV '\memory\standby cache core bytes')
    $pf = Get-CimInstance Win32_PageFileUsage | Select-Object -First 1
    $bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | Select-Object -First 1
    $scheme = try { (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes' -ErrorAction Stop).ActivePowerScheme } catch { '' }
    $procs = Get-Process -ErrorAction SilentlyContinue
    $chrome = @($procs | Where-Object Name -eq 'chrome')
    $vmm = $procs | Where-Object Name -eq 'vmmemWSL' | Select-Object -First 1

    $row = [pscustomobject]@{
        Timestamp      = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        Phase          = $phaseNow
        RamPct         = [math]::Round(($totalMB - $availMB) / $totalMB * 100, 2)
        AvailMB        = $availMB
        StandbyMB      = [math]::Round($standby / 1MB)
        ModifiedMB     = [math]::Round((CV '\memory\modified page list bytes') / 1MB)
        CommitMB       = [math]::Round($commit / 1MB)
        CommitLimitMB  = [math]::Round($limit / 1MB)
        CommitPct      = if ($limit -gt 0) { [math]::Round($commit / $limit * 100, 2) } else { -1 }
        PagefileMB     = if ($pf) { $pf.CurrentUsage } else { 0 }
        PagefilePct    = [math]::Round((CV '\paging file(_total)\% usage'), 2)
        HardFaultsSec  = [math]::Round((CV '\memory\pages input/sec'), 1)
        NonpagedMB     = [math]::Round((CV '\memory\pool nonpaged bytes') / 1MB)
        CpuPct         = [math]::Round((CV '\processor(_total)\% processor time'), 1)
        CpuPerfPct     = [math]::Round((CV '\processor information(_total)\% processor performance'), 1)
        DiskReadMBs    = [math]::Round((CV '\physicaldisk(_total)\disk read bytes/sec') / 1MB, 2)
        DiskWriteMBs   = [math]::Round((CV '\physicaldisk(_total)\disk write bytes/sec') / 1MB, 2)
        DiskQueue      = [math]::Round((CV '\physicaldisk(_total)\avg. disk queue length'), 2)
        ProcCount      = $procs.Count
        ChromeCount    = $chrome.Count
        ChromePrivMB   = [math]::Round((($chrome | Measure-Object PrivateMemorySize64 -Sum).Sum) / 1MB)
        VmmemWsMB      = if ($vmm) { [math]::Round($vmm.WorkingSet64 / 1MB) } else { 0 }
        OnAC           = if ($bat) { [int]($bat.BatteryStatus -eq 2) } else { 1 }
        BatteryPct     = if ($bat) { $bat.EstimatedChargeRemaining } else { '' }
        PowerScheme    = $scheme
        UptimeMin      = [math]::Round(((Get-Date) - $os.LastBootUpTime).TotalMinutes)
        LassoRunning   = [int][bool]($procs | Where-Object Name -eq 'ProcessGovernor')
    }
    $row | Export-Csv -Path $Csv -NoTypeInformation -Append -Encoding UTF8

    $stamp = $row.Timestamp
    $procs | Where-Object { $Tracked -contains $_.Name } | Group-Object Name | ForEach-Object {
        [pscustomobject]@{
            Timestamp = $stamp; Phase = $phaseNow; Process = $_.Name; Instances = $_.Count
            WsMB      = [math]::Round((($_.Group | Measure-Object WorkingSet64 -Sum).Sum) / 1MB, 1)
            PrivMB    = [math]::Round((($_.Group | Measure-Object PrivateMemorySize64 -Sum).Sum) / 1MB, 1)
            MaxWsMB   = [math]::Round((($_.Group | Measure-Object WorkingSet64 -Maximum).Maximum) / 1MB, 1)
            CpuSec    = [math]::Round((($_.Group | Measure-Object CPU -Sum).Sum), 1)
        }
    } | Export-Csv -Path $ProcCsv -NoTypeInformation -Append -Encoding UTF8

    Set-Content -Path $Heartbeat -Value $stamp -Encoding ASCII
} catch {
    Write-Err "sample failed: $($_.Exception.Message) @ $($_.InvocationInfo.ScriptLineNumber)"
    exit 1
}
