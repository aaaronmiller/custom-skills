# SPECTRE-16 machine profile and known traps

Last verified: 2026-10-13 checkup. Re-verify anything you act on; this is a map, not ground truth.

## Hardware
- HP Spectre x360 2-in-1 16-f2xxx. i7-1360P: **4 P-cores = logical 0-7 (HT), 8 E-cores = logical 8-15**. Masks: P `0x00FF`, E `0xFF00`.
- **16 GB LPDDR4 soldered, no slots.** Memory is the binding constraint; nothing makes 5-7 agents + 40 Chrome tabs fit.
- Arc A370M 4 GB + Iris Xe. No NPU (no Copilot+ features on any channel).
- NVMe WD SN810 1 TB = C:. D: = "FRMW 1TB Card" (USB expansion card, NTFS, label UGLYBETTY) - slow for hashing; never defrag it.
- Intel Wireless Bluetooth + Wi-Fi combo (driver 23.160.0.9, Jul 2025 at last check). Logitech Unifying receiver C52B plugged in; MX Master (BLE, PID B017) and Varmilo VS-3 keyboard (BLE) pair over the Intel radio. Dell WD19TB Thunderbolt dock.
- Second machine: i7-13800H, 32 GB DDR5, reachable over Tailscale. The structural fix for memory is moving subagents there.

## OS / channel
- Windows 11 Pro Insider, build 27965.1 (`br_release.251006-1425`), registered CanaryChannel. **Insider flight-signing cert expired 2026-08-11**; every WU feature update fails `0x800B0101`. Only route: ISO in-place upgrade (see insider-upgrade.md). User refuses clean installs.
- After upgrading, check whether the device should move to Beta; Future Platforms (296xx) is the wrong track for this box.
- WSL is the Store package (3.0.3 at last check), kernel 6.18.x, systemd on, `.wslconfig`: memory=8GB, swap=4GB, autoMemoryReclaim=dropcache, sparseVhd=true, NAT. earlyoom installed in Ubuntu (`-m 8 -M 400`, avoid shells/agents, prefer LSPs/build tools). NODE_OPTIONS=--max-old-space-size=1536 (in ~/.bashrc).
- Pagefile on C:, ~29 GB, not system-managed. Commit limit ~45.6 GB.

## Traps that cost hours before - check these first
1. **Process Lasso is a split portable install.** Binaries: `C:\Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]\App\ProgramFiles64` (folder says v14; engine is 18.2.3.42). **Live config + log: the same-named folder on the Desktop**, `...\Data\config\prolasso.ini` (UTF-16LE). Proof: `HKLM\SOFTWARE\ProcessLasso\ConfigFolderEx`. The `C:\Bitsum...\Data` copy is dead. NEVER let a Desktop cleanup move the Desktop folder. See lasso-v18-ini.md.
2. **WSL swap disks in %TEMP%** (`<GUID>\swap.vhdx`): a new one per VM start. Age is NOT a safe discriminator; only an exclusive-open test plus "older than the running vmmemWSL" is. A read-only open succeeds even on the live one.
3. **`C:\tmp` is user data** (notes, scripts), not system temp. Only `%TEMP%` and `C:\Windows\Temp` are auto-cleanable.
4. **In WSL, `pnpm` resolves to the Windows binary** (`/mnt/c/Users/Administrator/AppData/Roaming/npm/pnpm`) unless `PNPM_HOME` is on PATH. Use `~/.local/share/pnpm/pnpm` explicitly in scripts.
5. **Edge update services are disabled on purpose** (edgeupdate, edgeupdatem, MicrosoftEdgeElevationService). Edge and the WebView2 runtime therefore go stale; update them with winget each checkup.
6. **Intel driver pushes re-enable Intel services** that were disabled (Intel Connectivity Network Service, IntelConnectService, IDBWM came back on 2026-10-09 holding ~2.6 GB). Re-check every checkup.
7. **Logitech Download Assistant leaks instances** (14 seen). Real exe name is versioned: `logi_download_assistant-2.0.1020-win64.exe`; match with a wildcard.
8. **Windows Sandbox** may be open during a snapshot (4 GB). Re-check before blaming it.
9. **PowerShell 5.1 quirks**: `$PSScriptRoot` is empty in param defaults when launched via `-File` from Git Bash; resolve paths in the body. Keep .ps1 files ASCII-only (an em-dash in a string literal broke a script in August).
10. **Claude Code tool sandbox**: the PowerShell tool can only write under `C:\WINDOWS\system32`; write files with the Write tool or via `powershell.exe -File` from Bash using absolute paths. The damage-control hook blocks `rm -rf`, any command containing `.env`, and `-E`-looking flags after `powershell.exe` (it reads them as -EncodedCommand).
11. **Elevation**: sessions are not elevated. Launch admin scripts with `Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','<abs path>'` as a background Bash task; the user clicks UAC.
12. **Telemetry task death**: v1 used a -Once trigger without RepetitionDuration and vanished; a re-registration on 2026-09-10 also left no task. v2 (`Perf-Telemetry-v2.ps1 -Status`) has a heartbeat; check it first.

## User preferences (from past sessions)
- Wants work done, not re-confirmed: once an action is authorized, do not ask again. But irreversible deletions go through a dry-run script the user runs.
- "What you leave is more important to know than what you wipe" - always list what is kept and why.
- Never touch: browser logins/cookies/history, Obsidian vault and settings, `.claude`, the WSL distro, `C:\0.defenderexclusions` (ignore entirely).
- Prefers pnpm/bun over npm, Rust-native tools, anything that saves RAM. Hates SSD-as-RAM thrash more than OOM kills.
- Agents run 24/7 in WSL (busiest around 01:00). Do not `wsl --shutdown`, reboot, or restart WezTerm/agents without explicit go-ahead.
- Grunt work goes to headless omp sessions on opencode-go/muse-spark-1.3-contributor.
- **Security posture is intentional (user, 2026-10-14).** No BitLocker, tamper protection off, UAC as set, Defender exclusions, keymakers/activators/cracked installers, MDM-bypass and credential files all stay exactly as they are. Do not recommend changes, do not isolate or move those files, and exclude them from every cleanup plan (`build_cleanup_plan.py` filters them with its SECURITY regex).
- Cleanup decisions go through `removal/Cleanup-Approvals.html` (approve/reject per item, by folder, exportable in parts) and `Remove-CheckupItems.ps1 -Approvals <export>`. The user wants Downloads organized by project, then by type for leftovers.

## Disk-space drain to watch
Shadow-copy storage on C: is UNBOUNDED (39.9 GB on 2026-10-13). While snapshots exist, every block WSL rewrites inside the ~373 GB ext4.vhdx is copied into shadow storage, so C: free can fall by GBs per day with no visible files growing. Check `vssadmin list shadowstorage` (admin) whenever C: free drops unexplained; the cap item in the cleanup plan addresses it.
