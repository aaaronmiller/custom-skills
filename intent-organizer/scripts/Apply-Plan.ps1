# Apply-Plan.ps1 - step 7 of intent-organizer: carry out the approved part of an organizer plan.
#
# DRY RUN BY DEFAULT. Nothing moves unless you pass -Execute.
#   .\Apply-Plan.ps1 -Plan <workdir>\org-plan.json -Approvals .\organizer-approvals.json            # show what would happen
#   .\Apply-Plan.ps1 -Plan <workdir>\org-plan.json -Approvals .\organizer-approvals.json -Execute   # do it
#
# Only ids listed as approved in the export from Organizer.html run; everything else is left alone.
# Actions: move  -> into the item's target folder (created as needed)
#          stage -> into the target _REVIEW-then-delete folder (nothing is ever deleted by this script)
# Safety at run time: protected paths are refused; a missing source is skipped; an existing file or folder
# with the same name at the destination is never overwritten (the item is skipped and logged).
# Every row is logged to run-<timestamp>.csv next to the plan; Undo-Moves.ps1 reverses a run from that log.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$Approvals,
    [switch]$Execute
)
$ErrorActionPreference = 'Continue'
$p = Get-Content -LiteralPath $Plan -Raw -Encoding UTF8 | ConvertFrom-Json
$a = Get-Content -LiteralPath $Approvals -Raw -Encoding UTF8 | ConvertFrom-Json
if ($a.plan_id -ne $p.plan_id) {
    Write-Host "The approvals are for plan '$($a.plan_id)' but this plan is '$($p.plan_id)'. Rebuild the page or use the matching plan." -ForegroundColor Red
    exit 2
}
$approved = @{}; foreach ($id in @($a.approved)) { $approved[$id] = $true }
$protected = @($p.protected) | Where-Object { $_ } | ForEach-Object { $_.TrimEnd('\').ToLowerInvariant() }
function Test-Protected([string]$path) {
    $l = $path.TrimEnd('\').ToLowerInvariant()
    foreach ($x in $protected) { if ($l -eq $x -or $l.StartsWith($x + '\')) { return $true } }
    return $false
}
function Get-Bytes([string]$path) {
    try {
        $i = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if ($i.PSIsContainer) { return [long](Get-ChildItem -LiteralPath $path -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum }
        return [long]$i.Length
    } catch { return 0 }
}
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path (Split-Path -Parent (Resolve-Path -LiteralPath $Plan)) "run-$stamp.csv"
$rows = New-Object System.Collections.Generic.List[object]
function Log($it, $status, $bytes, $dest, $detail) {
    $rows.Add([pscustomobject]@{ id = $it.id; section = $it.section; group = $it.group; path = $it.path; action = $it.action
        status = $status; bytes = $bytes; dest = $dest; detail = $detail })
    $c = switch -Wildcard ($status) { 'DONE*' { 'Green' } 'WOULD*' { 'Cyan' } 'FAIL' { 'Red' } default { 'DarkYellow' } }
    Write-Host ("  [{0}] {1}  ->  {2} {3}" -f $status, $it.path, $dest, $detail) -ForegroundColor $c
}
$sel = @($p.items | Where-Object { $approved.ContainsKey($_.id) })
Write-Host ("`n=== Apply-Plan  {0}  plan={1}  approved={2} of {3}" -f $(if ($Execute) { 'EXECUTE' } else { 'DRY RUN' }), $p.plan_id, $sel.Count, @($p.items).Count) -ForegroundColor Magenta
foreach ($it in $sel) {
    $src = $it.path
    $destDir = $it.target
    $dest = Join-Path $destDir (Split-Path $src -Leaf)
    if (Test-Protected $src) { Log $it 'SKIP-protected' 0 $dest ''; continue }
    if (-not (Test-Path -LiteralPath $src)) { Log $it 'SKIP-gone' 0 $dest 'not found (already moved?)'; continue }
    if (Test-Path -LiteralPath $dest) { Log $it 'SKIP-exists' 0 $dest 'something with this name is already there'; continue }
    $bytes = Get-Bytes $src
    if (-not $Execute) { Log $it ('WOULD-' + $it.action) $bytes $dest ''; continue }
    try {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        Move-Item -LiteralPath $src -Destination $dest -ErrorAction Stop
        Log $it ('DONE-' + $it.action) $bytes $dest ''
    } catch { Log $it 'FAIL' 0 $dest $_.Exception.Message }
}
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $log
$moved = @($rows | Where-Object { $_.status -like 'DONE*' -or $_.status -like 'WOULD*' })
$staged = ($moved | Where-Object { $_.action -eq 'stage' } | Measure-Object bytes -Sum).Sum
Write-Host ("`n{0}: {1} items, {2:N2} GB staged for removal, {3} skipped, {4} failed. Log: {5}" -f `
    $(if ($Execute) { 'Done' } else { 'Would do' }), $moved.Count, ($staged / 1GB),
    @($rows | Where-Object { $_.status -like 'SKIP*' }).Count, @($rows | Where-Object { $_.status -eq 'FAIL' }).Count, $log) -ForegroundColor Magenta
if (-not $Execute) { Write-Host 'Nothing was changed. Re-run with -Execute to apply.' -ForegroundColor Yellow }
else { Write-Host "Undo: .\Undo-Moves.ps1 -Log `"$log`"  (dry run; add -Execute)" -ForegroundColor Yellow }
