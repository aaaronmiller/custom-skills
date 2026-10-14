# Getting an expired Insider build current (in-place upgrade from ISO)

Verified 2026-10-13 against blogs.windows.com, learn.microsoft.com release notes, and the UUP dump API.

## Why Windows Update cannot do it
Insider flight-signing certificates expired **2026-08-11**. A build older than its channel's renewal floor (Experimental 26H1 >= 28120.2630, Beta 26H1 >= 28020.2623, Future Platforms >= 29634.1000) gets `0x800B0101` on every feature update, including the one WU offers (28020.2207 was below the floor). Re-enrolling, flight signing, root-store refresh and OfflineInsiderEnroll do not help.

## Find the current target
```bash
curl -s "https://api.uupdump.net/listid.php?search=28120&sortByDate=1" | python -c "import json,sys;b=json.load(sys.stdin)['response']['builds'];[print(x['build'],x['arch'],x['title'],x['uuid']) for x in (b.values() if isinstance(b,dict) else b)][:6]"
```
Pick the newest amd64 "Feature Update" on the 26H1 line. Cross-check the build on learn.microsoft.com/windows-insider/release-notes/experimental-26-h1/. As of 2026-10-13: **28120.3181**, UUID `cb37f441-7218-4f4b-966d-885cd3b44c9b`.

## Build the ISO (on D:, needs admin, about 6-10 GB download and 30-40 GB of scratch space)
1. UUP dump: choose the UUID, language en-us, edition Professional, "Download and convert to ISO". Extract to a short path such as `D:\UUP\28120.3181`.
2. `ConvertConfig.ini`: `AutoStart=1`, `AddUpdates=1`, `Cleanup=1`, `ResetBase=0`, `NetFx3=0`, `SkipEdge=0`, `wim2esd=0`.
3. Run `uup_download_windows.cmd` elevated. Keep the ISO until the rollback window closes.

## Pre-flight and stage (no restart)
```cmd
:: mount the ISO, say as E:
E:\setup.exe /auto upgrade /compat scanonly /dynamicupdate disable /quiet
::   exit 0xC1900210 = no blockers; 0xC1900208 = incompatible app (read C:\$WINDOWS.~BT\Sources\Panther\CompatData*.xml)
E:\setup.exe /auto upgrade /noreboot /dynamicupdate disable /eula accept /showoobe none /copylogs D:\SetupLogs
::   downlevel done when setupact.log reports it is ready for reboot; 30-90 min
```
Staging changes the next boot: any restart, including a crash, continues the upgrade. Stage only when the user agrees it may happen at the next restart.

## After the restart
- `winver`; `Get-ComputerInfo | Select WindowsProductName,OsBuildNumber`; Settings > Windows Insider Program channel.
- `DISM /Online /Set-OSUninstallWindow /Value:60` (default rollback is 10 days).
- `sfc /scannow` should be clean (the 187 `UserExperience-FileExp` icon mismatches go away).
- Re-check: `wsl -l -v`, ProcessGovernor service, telemetry `-Status`, Windows Search still disabled, services from `memory-remediation.ps1`, power plan, Intel ICPS services, Edge update services.
- Run Windows Update once; it should succeed now that the build carries the renewed certificate.
