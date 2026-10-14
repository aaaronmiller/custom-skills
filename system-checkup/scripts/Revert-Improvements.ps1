# Revert-Improvements.ps1 - undo Apply-Improvements.ps1 using raw\elevated\revert-state.json.
# Restores: service start modes (and starts services that were running), StartupApproved values,
# and the pre-change prolasso.ini (GUI is closed first so it cannot overwrite the restore).
# Leaves telemetry v2 registered (it only observes) and does not downgrade winget packages.
#Requires -RunAsAdministrator
param([Parameter(Mandatory)][string]$State)   # <checkup>\raw\elevated\revert-state.json
$ErrorActionPreference = 'Continue'
if (-not (Test-Path $State)) { Write-Host "no revert state at $State" -ForegroundColor Red; exit 1 }
$r = Get-Content $State -Raw | ConvertFrom-Json
foreach ($s in $r.services) {
    $mode = switch ($s.startMode) { 'Auto' { 'Automatic' } 'Manual' { 'Manual' } 'Disabled' { 'Disabled' } default { 'Manual' } }
    Set-Service -Name $s.name -StartupType $mode -ErrorAction SilentlyContinue
    if ($s.state -eq 'Running') { Start-Service -Name $s.name -ErrorAction SilentlyContinue }
    Write-Host ("service {0} -> {1} ({2})" -f $s.name, $mode, $s.state)
}
foreach ($a in $r.startupApproved) {
    if ($a.previous) { Set-ItemProperty -Path $a.key -Name $a.name -Value ([Convert]::FromBase64String($a.previous)) -Type Binary }
    else { Remove-ItemProperty -Path $a.key -Name $a.name -ErrorAction SilentlyContinue }
    Write-Host "startup entry '$($a.name)' restored"
}
if ($r.lassoIniBackup -and (Test-Path -LiteralPath $r.lassoIniBackup)) {
    Get-Process -Name ProcessLasso -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Copy-Item -LiteralPath $r.lassoIniBackup -Destination $r.lassoIni -Force
    Write-Host "prolasso.ini restored from $($r.lassoIniBackup) (governor reloads automatically; reopen the GUI from the Start menu)"
}
Write-Host 'Revert complete.' -ForegroundColor Green
