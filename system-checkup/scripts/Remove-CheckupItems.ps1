# Remove-CheckupItems.ps1 - apply the reviewed removal manifest from the 2026-10 checkup.
#
# DRY RUN BY DEFAULT. Nothing is touched unless you pass -Execute.
#
#   .\Remove-CheckupItems.ps1                          # show what the default set would do
#   .\Remove-CheckupItems.ps1 -Execute                 # do the default (safe) set
#   .\Remove-CheckupItems.ps1 -Only WSL,'Windows caches' -Execute
#   .\Remove-CheckupItems.ps1 -Only WIN-123,WSL-140 -IncludeOptional -Execute   # opt-in items by id
#   .\Remove-CheckupItems.ps1 -LivingDocExport .\downloads-desktop-cleanup-change-request.json -Execute
#
#   APPROVAL MODE (preferred): decide item by item in Cleanup-Approvals.html, export, then
#   .\Remove-CheckupItems.ps1 -Approvals <exported.json>            # dry run of exactly what you approved
#   .\Remove-CheckupItems.ps1 -Approvals <exported.json> -Execute   # apply it
#   Only approved ids from cleanup-plan.json run; rejected and undecided items are never touched.
#
# Rules this script enforces at run time (not just at manifest-build time):
#   * Protected roots are never touched (C:\0.defenderexclusions, the Obsidian vault, the live Process
#     Lasso Data folder on the Desktop, .claude/.config/.ssh, the WSL distro package, the Acronis backup,
#     this checkup folder, the living document).
#   * Temp items must still be >= min_age_days old and must open without a lock.
#   * WSL swap folders are removed only if their swap.vhdx opens EXCLUSIVELY and predates the running
#     vmmemWSL process.
#   * Items that need an app closed are skipped while that app runs. Admin items are skipped unless elevated.
#   * Duplicates and living-document deletions are MOVED into a sibling _REVIEW-then-delete folder, never
#     deleted. Empty those folders yourself once you have looked.
#   * Every action is logged to removal\run-<timestamp>.csv with bytes before/after.
[CmdletBinding()]
param(
    [string]$Manifest,
    [switch]$Execute,
    [string[]]$Only,
    [switch]$IncludeOptional,
    [string]$LivingDocExport,
    [switch]$UseRecycleBin,
    [string]$Approvals,
    [string]$Plan
)
$ErrorActionPreference = 'Continue'
$Here = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if ($Approvals) {
    if (-not $Plan) { $Plan = Join-Path $Here 'cleanup-plan.json' }
    $Manifest = $Plan
}
if (-not $Manifest) { $Manifest = Join-Path $Here 'removal-manifest.json' }
Add-Type -AssemblyName Microsoft.VisualBasic
$m = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
$approvedIds = $null
if ($Approvals) {
    $ap = Get-Content -LiteralPath $Approvals -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($ap.plan_id -ne $m.plan_id) { Write-Host "Approvals file is for plan '$($ap.plan_id)' but the plan is '$($m.plan_id)'. Stopping." -ForegroundColor Red; exit 2 }
    $approvedIds = @($ap.approved)
    Write-Host ("Approvals: {0} approved, {1} rejected (scope: {2})" -f @($ap.approved).Count, @($ap.rejected).Count, $ap.scope) -ForegroundColor Magenta
    foreach ($it in $m.items) { if (-not $it.PSObject.Properties['section']) { $it | Add-Member -NotePropertyName section -NotePropertyValue $it.folder }; if (-not $it.PSObject.Properties['title']) { $it | Add-Member -NotePropertyName title -NotePropertyValue $it.name } }
}
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logCsv = Join-Path $Here "run-$stamp.csv"
$quarantine = Join-Path (Split-Path $Here -Parent) "quarantine\$stamp"
$results = New-Object System.Collections.Generic.List[object]
$protected = @($m.protected) | ForEach-Object { $_.TrimEnd('\').ToLowerInvariant() }

function Write-Result($item, $path, $status, $bytes, $detail) {
    $results.Add([pscustomobject]@{ id = $item.id; section = $item.section; title = $item.title; path = $path; status = $status; mb = [math]::Round($bytes / 1MB, 1); detail = $detail })
    $color = switch -Wildcard ($status) { 'DONE*' { 'Green' } 'WOULD*' { 'Cyan' } 'SKIP*' { 'DarkYellow' } 'FAIL*' { 'Red' } default { 'Gray' } }
    Write-Host ("  [{0,-13}] {1,-9} {2,8:N1} MB  {3}  {4}" -f $status, $item.id, ($bytes / 1MB), $path, $detail) -ForegroundColor $color
}
function Test-Protected([string]$p) {
    $lp = $p.TrimEnd('\').ToLowerInvariant()
    foreach ($r in $protected) { if ($lp -eq $r -or $lp.StartsWith($r + '\')) { return $true } }
    return $false
}
function Get-Bytes([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) { return 0 }
    $i = Get-Item -LiteralPath $p -Force
    if ($i.PSIsContainer) { return [int64]((Get-ChildItem -LiteralPath $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum) }
    return [int64]$i.Length
}
function Get-NewestWrite([string]$p) {
    $i = Get-Item -LiteralPath $p -Force
    if (-not $i.PSIsContainer) { return $i.LastWriteTime }
    $n = Get-ChildItem -LiteralPath $p -Recurse -File -Force -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($n) { return $n.LastWriteTime } else { return $i.LastWriteTime }
}
function Test-Locked([string]$file, [switch]$Exclusive) {
    try {
        $share = if ($Exclusive) { [IO.FileShare]::None } else { [IO.FileShare]::ReadWrite }
        $fs = [IO.File]::Open($file, [IO.FileMode]::Open, [IO.FileAccess]::Read, $share); $fs.Close(); return $false
    } catch { return $true }
}
function Test-Requirements($item) {
    foreach ($req in @($item.requires)) {
        if (-not $req) { continue }
        if ($req -eq 'admin' -and -not $isAdmin) { return 'needs admin' }
        if ($req -like 'closed:*') {
            $app = $req.Substring(7)
            if (Get-Process -Name $app -ErrorAction SilentlyContinue) { return "$app is running" }
        }
    }
    return $null
}
function Remove-PathNow([string]$p) {
    $i = Get-Item -LiteralPath $p -Force
    if ($UseRecycleBin) {
        if ($i.PSIsContainer) { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($p, 'OnlyErrorDialogs', 'SendToRecycleBin') }
        else { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($p, 'OnlyErrorDialogs', 'SendToRecycleBin') }
    } else { Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Stop }
}
function Move-ToReview([string]$p) {
    $root = Split-Path $p -Parent
    $review = Join-Path $root '_REVIEW-then-delete'
    New-Item -ItemType Directory -Force -Path $review | Out-Null
    $dest = Join-Path $review (Split-Path $p -Leaf)
    if (Test-Path -LiteralPath $dest) { $dest = Join-Path $review ("{0}.{1}" -f (Split-Path $p -Leaf), $stamp) }
    Move-Item -LiteralPath $p -Destination $dest -ErrorAction Stop
    return $dest
}

$freeBefore = Get-CimInstance Win32_LogicalDisk | Where-Object DeviceID -in 'C:', 'D:' | ForEach-Object { [pscustomobject]@{ d = $_.DeviceID; gb = [math]::Round($_.FreeSpace / 1GB, 2) } }
Write-Host ("`n=== Remove-CheckupItems  mode={0}  admin={1}  manifest={2}" -f $(if ($Execute) { 'EXECUTE' } else { 'DRY-RUN' }), $isAdmin, $m.generated) -ForegroundColor Magenta
$vmStart = try { (Get-Process vmmemWSL -ErrorAction Stop | Select-Object -First 1).StartTime } catch { $null }

$selected = @($m.items) | Where-Object {
    $it = $_
    if ($null -ne $approvedIds) { return ($approvedIds -contains $it.id) }   # approval mode: exactly what you approved
    if ($it.action -eq 'stage-by-name') { return $false }        # handled by -LivingDocExport below
    $picked = (-not $Only) -or ($Only -contains $it.id) -or ($Only -contains $it.section)
    $picked -and ($it.default -or $IncludeOptional -or ($Only -contains $it.id))
}
# moves first, so a folder that is both organized and has stale siblings ends up in the right place
$selected = @($selected | Sort-Object { if ($_.action -eq 'move') { 0 } else { 1 } })
foreach ($it in $selected) {
    $why = Test-Requirements $it
    if ($why) { Write-Result $it ($it.path, $it.command, $it.wsl | Where-Object { $_ } | Select-Object -First 1) 'SKIP-req' 0 $why; continue }
    switch ($it.action) {
        'move' {
            $p = $it.path; $dest = $it.target
            if (Test-Protected $p) { Write-Result $it $p 'SKIP-protect' 0 'inside a protected root'; continue }
            if (-not (Test-Path -LiteralPath $p)) { Write-Result $it $p 'SKIP-gone' 0 'already gone or already moved'; continue }
            if ((Split-Path $p -Parent).TrimEnd('\') -ieq $dest.TrimEnd('\')) { Write-Result $it $p 'SKIP-there' 0 'already in place'; continue }
            $final = Join-Path $dest (Split-Path $p -Leaf)
            if (Test-Path -LiteralPath $final) { Write-Result $it $p 'SKIP-exists' 0 "a file with that name is already in $dest"; continue }
            if (-not (Get-Item -LiteralPath $p -Force).PSIsContainer -and (Test-Locked $p)) { Write-Result $it $p 'SKIP-locked' 0 'file is open'; continue }
            $bytes = Get-Bytes $p
            if (-not $Execute) { Write-Result $it $p 'WOULD-move' $bytes "-> $dest"; continue }
            try { New-Item -ItemType Directory -Force -Path $dest | Out-Null; Move-Item -LiteralPath $p -Destination $final -ErrorAction Stop; Write-Result $it $p 'DONE-moved' $bytes "-> $dest" }
            catch { Write-Result $it $p 'FAIL' 0 $_.Exception.Message }
        }
        { $_ -in 'delete', 'delete-contents', 'quarantine', 'stage', 'delete-wsl-swap' } {
            $paths = @(); if ($it.path) { $paths += $it.path }; if ($it.paths) { $paths += @($it.paths) }
            foreach ($p in $paths) {
                if (Test-Protected $p) { Write-Result $it $p 'SKIP-protect' 0 'inside a protected root'; continue }
                if (-not (Test-Path -LiteralPath $p)) { Write-Result $it $p 'SKIP-gone' 0 'already gone'; continue }
                if ($it.min_age_days) {
                    $age = ((Get-Date) - (Get-NewestWrite $p)).TotalDays
                    if ($age -lt [double]$it.min_age_days) { Write-Result $it $p 'SKIP-young' 0 ("touched {0:N1} d ago" -f $age); continue }
                    if (-not (Get-Item -LiteralPath $p -Force).PSIsContainer -and (Test-Locked $p)) { Write-Result $it $p 'SKIP-locked' 0 'file is open'; continue }
                }
                if ($it.action -eq 'delete-wsl-swap') {
                    $vh = Get-ChildItem -LiteralPath $p -Filter *.vhdx -Force -ErrorAction SilentlyContinue | Select-Object -First 1
                    if ($vh -and (Test-Locked $vh.FullName -Exclusive)) { Write-Result $it $p 'SKIP-live' 0 'swap.vhdx is attached to a running VM'; continue }
                    if ($vh -and $vmStart -and $vh.LastWriteTime -gt $vmStart.AddMinutes(-5)) { Write-Result $it $p 'SKIP-live' 0 'created by the current WSL VM'; continue }
                }
                if ($it.action -eq 'quarantine' -and $p -like '*Bitsum*') {
                    $cfg = (Get-ItemProperty 'HKLM:\SOFTWARE\ProcessLasso' -Name ConfigFolderEx -ErrorAction SilentlyContinue).ConfigFolderEx
                    if ($cfg -and $cfg.ToLowerInvariant().StartsWith($p.ToLowerInvariant())) { Write-Result $it $p 'SKIP-protect' 0 'Process Lasso reads its config from here'; continue }
                }
                $bytes = Get-Bytes $p
                if (-not $Execute) { Write-Result $it $p "WOULD-$($it.action)" $bytes $it.why.Substring(0, [Math]::Min(60, $it.why.Length)); continue }
                try {
                    switch ($it.action) {
                        'delete-contents' {
                            $svcs = @($it.requires | Where-Object { $_ -like 'service-stop:*' } | ForEach-Object { $_.Substring(13) -split ',' })
                            $svcs | ForEach-Object { Stop-Service $_ -Force -ErrorAction SilentlyContinue }
                            Get-ChildItem -LiteralPath $p -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                            $svcs | ForEach-Object { Start-Service $_ -ErrorAction SilentlyContinue }
                            Write-Result $it $p 'DONE' ($bytes - (Get-Bytes $p)) 'contents removed'
                        }
                        'quarantine' { New-Item -ItemType Directory -Force -Path $quarantine | Out-Null; Move-Item -LiteralPath $p -Destination (Join-Path $quarantine $it.id) -ErrorAction Stop; Write-Result $it $p 'DONE-moved' $bytes "-> $quarantine" }
                        'stage' { $d = Move-ToReview $p; Write-Result $it $p 'DONE-staged' $bytes "-> $d" }
                        default { Remove-PathNow $p; Write-Result $it $p 'DONE' $bytes $(if ($UseRecycleBin) { 'to Recycle Bin' } else { 'deleted' }) }
                    }
                } catch { Write-Result $it $p 'FAIL' 0 $_.Exception.Message }
            }
        }
        'command' {
            $exe = ($it.command -split ' ')[0]
            if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { Write-Result $it $it.command 'SKIP-missing' 0 "$exe not found"; continue }
            if (-not $Execute) { Write-Result $it $it.command 'WOULD-run' ([int64]($it.gb * 1GB)) 'estimated'; continue }
            $o = cmd /c "$($it.command) 2>&1"; Write-Result $it $it.command $(if ($LASTEXITCODE -eq 0) { 'DONE' } else { 'FAIL' }) ([int64]($it.gb * 1GB)) (($o | Select-Object -Last 1) -as [string])
        }
        'command-ps' {
            if (-not $Execute) { Write-Result $it $it.command 'WOULD-run' ([int64]($it.gb * 1GB)) 'estimated'; continue }
            try { $o = Invoke-Expression $it.command 2>&1 | Out-String; Write-Result $it $it.command 'DONE' ([int64]($it.gb * 1GB)) ($o.Trim() -split "`n" | Select-Object -Last 1) }
            catch { Write-Result $it $it.command 'FAIL' 0 $_.Exception.Message }
        }
        'wsl' {
            if (-not $Execute) { Write-Result $it $it.wsl 'WOULD-wsl' ([int64]($it.gb * 1GB)) 'estimated'; continue }
            $o = wsl.exe -d Ubuntu -e bash -lc $it.wsl 2>&1 | Out-String
            Write-Result $it $it.wsl $(if ($LASTEXITCODE -eq 0) { 'DONE' } else { 'FAIL' }) ([int64]($it.gb * 1GB)) ($o.Trim() -split "`n" | Select-Object -Last 1)
        }
    }
}

# ------------------------------------------------------------- living-document decisions (user folders)
if ($LivingDocExport) {
    Write-Host "`n--- Living document decisions: $LivingDocExport" -ForegroundColor Magenta
    $cr = Get-Content -LiteralPath $LivingDocExport -Raw -Encoding UTF8 | ConvertFrom-Json
    $roots = @{ 'Downloads' = "$env:USERPROFILE\Downloads"; 'Desktop' = "$env:USERPROFILE\Desktop"; 'Documents' = "$env:USERPROFILE\Documents";
                'Pictures' = "$env:USERPROFILE\Pictures"; 'Videos' = "$env:USERPROFILE\Videos"; 'Music' = "$env:USERPROFILE\Music";
                'Home' = $env:USERPROFILE; 'C:' = 'C:\'; 'D:' = 'D:\'; 'Temp' = $env:TEMP }
    foreach ($d in $cr.proposalDecisions) {
        $loc, $file = $d.target -split ' :: ', 2
        $name = ($file -split '  ')[0].Trim()
        $item = [pscustomobject]@{ id = 'LD'; section = 'User folders'; title = $name }
        $cands = @($roots.Keys | Where-Object { $loc -match [regex]::Escape($_) } | ForEach-Object { Join-Path $roots[$_] $name } | Where-Object { Test-Path -LiteralPath $_ })
        if (-not $cands) { Write-Result $item "$loc :: $name" 'SKIP-gone' 0 'not found'; continue }
        foreach ($p in $cands) {
            if (Test-Protected $p) { Write-Result $item $p 'SKIP-protect' 0 'protected'; continue }
            $dec = [string]$d.decision
            $bytes = Get-Bytes $p
            if ($dec -match '^(Keep|No action)') { continue }
            elseif ($dec -match 'Delete|REVIEW|Stage') {
                if ($Execute) { try { $dest = Move-ToReview $p; Write-Result $item $p 'DONE-staged' $bytes "-> $dest" } catch { Write-Result $item $p 'FAIL' 0 $_.Exception.Message } }
                else { Write-Result $item $p 'WOULD-stage' $bytes $dec }
            } elseif ($dec -match '(?:Move|Isolate)[^/]*(/[^)\s]+)') {
                $target = Join-Path (Split-Path $p -Parent) ($matches[1].TrimStart('/'))
                if ($Execute) { try { New-Item -ItemType Directory -Force -Path $target | Out-Null; Move-Item -LiteralPath $p -Destination $target -ErrorAction Stop; Write-Result $item $p 'DONE-moved' $bytes "-> $target" } catch { Write-Result $item $p 'FAIL' 0 $_.Exception.Message } }
                else { Write-Result $item $p 'WOULD-move' $bytes "-> $target" }
            } else { Write-Result $item $p 'SKIP-manual' $bytes $dec }
        }
    }
}

$results | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $logCsv
$freeAfter = Get-CimInstance Win32_LogicalDisk | Where-Object DeviceID -in 'C:', 'D:' | ForEach-Object { [pscustomobject]@{ d = $_.DeviceID; gb = [math]::Round($_.FreeSpace / 1GB, 2) } }
$sum = ($results | Where-Object { $_.status -like 'DONE*' -or $_.status -like 'WOULD*' } | Measure-Object mb -Sum).Sum
Write-Host ("`n{0}: {1:N1} GB across {2} actions. Log: {3}" -f $(if ($Execute) { 'Reclaimed/staged' } else { 'Would reclaim/stage' }), ($sum / 1024), ($results | Where-Object { $_.status -like 'DONE*' -or $_.status -like 'WOULD*' }).Count, $logCsv) -ForegroundColor Magenta
foreach ($f in $freeBefore) { $a = $freeAfter | Where-Object d -eq $f.d; Write-Host ("  {0} free: {1} GB -> {2} GB" -f $f.d, $f.gb, $a.gb) }
if (-not $Execute) { Write-Host "`nDry run only. Re-run with -Execute to apply." -ForegroundColor Yellow }
