# Undo-Moves.ps1 - put back everything an Apply-Plan run moved or staged.
# Reads the run log (run-<timestamp>.csv next to the plan) and reverses every DONE-move / DONE-stage row,
# newest first. Never overwrites: if the original location is occupied again, that row is skipped.
#   .\Undo-Moves.ps1 -Log .\run-20261014-150000.csv            # dry run
#   .\Undo-Moves.ps1 -Log .\run-20261014-150000.csv -Execute   # do it
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Log, [switch]$Execute)
$ErrorActionPreference = 'Continue'
$rows = @(Import-Csv -LiteralPath $Log -Encoding UTF8 | Where-Object { $_.status -like 'DONE-*' })
[array]::Reverse($rows)
$ok = 0; $skip = 0
foreach ($r in $rows) {
    $orig = $r.path; $now = $r.dest
    if (-not (Test-Path -LiteralPath $now)) { Write-Host "  [SKIP] not found: $now" -ForegroundColor DarkYellow; $skip++; continue }
    if (Test-Path -LiteralPath $orig) { Write-Host "  [SKIP] original location occupied: $orig" -ForegroundColor DarkYellow; $skip++; continue }
    if (-not $Execute) { Write-Host "  [WOULD] $now -> $orig" -ForegroundColor Cyan; $ok++; continue }
    try {
        New-Item -ItemType Directory -Force -Path (Split-Path $orig -Parent) | Out-Null
        Move-Item -LiteralPath $now -Destination $orig -ErrorAction Stop
        Write-Host "  [DONE] $now -> $orig" -ForegroundColor Green; $ok++
    } catch { Write-Host "  [FAIL] $now : $($_.Exception.Message)" -ForegroundColor Red; $skip++ }
}
# tidy up: remove destination folders left EMPTY by the undo, climbing upward but never to the item's original
# folder or anything above it, and never shallower than C:\Users\<name>\<folder>
if ($Execute) {
    foreach ($r in $rows) {
        $stop = (Split-Path $r.path -Parent).TrimEnd('\').ToLowerInvariant()
        $d = Split-Path $r.dest -Parent
        while ($d -and (Test-Path -LiteralPath $d) -and -not $stop.StartsWith($d.TrimEnd('\').ToLowerInvariant()) -and
               ($d.TrimEnd('\').Split('\').Count -gt 3) -and -not (Get-ChildItem -LiteralPath $d -Force | Select-Object -First 1)) {
            Remove-Item -LiteralPath $d -Force; $d = Split-Path $d -Parent
        }
    }
}
Write-Host ("`n{0}: {1} restored, {2} skipped." -f $(if ($Execute) { 'Undo' } else { 'Dry run' }), $ok, $skip) -ForegroundColor Magenta
if (-not $Execute) { Write-Host 'Re-run with -Execute to restore.' -ForegroundColor Yellow }
