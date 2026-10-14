# collect-events.ps1 - read-only event-log time series for the checkup report (no admin needed).
param([string]$OutFile = ("C:\performance-diagnostics\checkup-{0}\report\events.json" -f (Get-Date -Format yyyyMMdd)), [datetime]$Since = (Get-Date).AddDays(-120))
New-Item -ItemType Directory -Force -Path (Split-Path $OutFile -Parent) | Out-Null
$o = [ordered]@{ collected = (Get-Date).ToString('s') }
$wu = Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-WindowsUpdateClient/Operational'; Id=31; StartTime=$Since} -ErrorAction SilentlyContinue
$o.wu_fail_total = @($wu).Count
$o.wu_fail_weekly = @($wu | Group-Object { $d=$_.TimeCreated.Date; $d.AddDays(-[int]$d.DayOfWeek).ToString('yyyy-MM-dd') } | Sort-Object Name | ForEach-Object { [ordered]@{week=$_.Name; n=$_.Count} })
$ex = Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004; StartTime=$Since} -ErrorAction SilentlyContinue
$o.exhaustion_total = @($ex).Count
$o.exhaustion_daily = @($ex | Group-Object { $_.TimeCreated.ToString('yyyy-MM-dd') } | Sort-Object Name | ForEach-Object { [ordered]@{day=$_.Name; n=$_.Count} })
$sh = Get-WinEvent -FilterHashtable @{LogName='System'; Id=41,1001; StartTime=$Since} -ErrorAction SilentlyContinue
$o.unclean = @($sh | Sort-Object TimeCreated | ForEach-Object { $m = ($_.Message -replace '\s+',' '); [ordered]@{t=$_.TimeCreated.ToString('yyyy-MM-dd HH:mm'); id=$_.Id; msg=$m.Substring(0,[Math]::Min(120,$m.Length))} })
$bt = Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Kernel-PnP/Device Management'; Id=1010; StartTime=(Get-Date).AddDays(-45)} -ErrorAction SilentlyContinue
$o.bt_daily = @($bt | ForEach-Object { $k = if ($_.Message -match 'c85696fa97a5') {'mouse'} elseif ($_.Message -match 'd88512a3f888') {'kbd'} else {$null}; if ($k) { [pscustomobject]@{d=$_.TimeCreated.ToString('yyyy-MM-dd'); k=$k} } } | Group-Object d | Sort-Object Name | ForEach-Object { [ordered]@{day=$_.Name; mouse=@($_.Group | Where-Object k -eq 'mouse').Count; kbd=@($_.Group | Where-Object k -eq 'kbd').Count} })
$app = Get-WinEvent -FilterHashtable @{LogName='Application'; Level=1,2; StartTime=(Get-Date).AddDays(-30)} -ErrorAction SilentlyContinue
$o.app_errors_top = @($app | Group-Object { if ($_.Id -eq 1000 -and $_.Message -match 'Faulting application name: ([^,]+)') { "AppCrash: $($matches[1])" } else { "$($_.ProviderName) $($_.Id)" } } | Sort-Object Count -Descending | Select-Object -First 12 | ForEach-Object { [ordered]@{name=$_.Name; n=$_.Count} })
$sys = Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-30)} -ErrorAction SilentlyContinue
$o.sys_errors_top = @($sys | Group-Object { "$($_.ProviderName) $($_.Id)" } | Sort-Object Count -Descending | Select-Object -First 12 | ForEach-Object { [ordered]@{name=$_.Name; n=$_.Count} })
$o | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $OutFile
"wu fails: $($o.wu_fail_total) over $($o.wu_fail_weekly.Count) weeks | exhaustion: $($o.exhaustion_total) | unclean: $($o.unclean.Count) | bt days: $($o.bt_daily.Count)"
