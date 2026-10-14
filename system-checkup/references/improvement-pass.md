# Improvement pass (proposed 2026-10-13, awaiting the user's approval)

The auto-mode classifier refused to let Claude write this as a ready-to-run script, so it is recorded here as a specification. Each change is reversible; record the previous state before applying (`Revert-Improvements.ps1` reads `raw\elevated\revert-state.json` with keys `services[]`, `startupApproved[]`, `lassoIni`, `lassoIniBackup`). Get the user's explicit OK, then apply elevated.

1. **Telemetry v2**: `Perf-Telemetry-v2.ps1 -SetPhase checkup-YYYYMMDD; Perf-Telemetry-v2.ps1 -Register`, then `-Status` must say Healthy within 10 minutes.
2. **Intel Connectivity Performance Suite**: stop and set Disabled: `Intel Connectivity Network Service`, `IntelConnectService`, `IDBWM` (about 2.6 GB of private commit; optional bandwidth management, Wi-Fi does not need them).
3. **Logitech Download Assistant**: stop all `logi_download_assistant*` processes; disable the HKLM Run value `Logi Download Assistant` through `HKLM\...\Explorer\StartupApproved\Run` (binary `03 00 00 00` + FILETIME), the same mechanism Task Manager uses, so it can be re-enabled there.
4. **Process Lasso v3 rules** (procedure in lasso-v18-ini.md):
   - `DefaultAffinitiesEx` = existing 10 with `logi_download_assistant*.exe` fixed, plus `esrv_svc.exe`, `mdnsresponder.exe`, `schedul2.exe`, `googledrivefs.exe`, `crossdeviceservice.exe`, `intel_pie_service.exe` -> `8-15`.
   - `CPUSets` = discord, slack, beeper, joplin, phoneexperiencehost, msedgewebview2 -> `(0/8-15)`.
   - `EfficiencyMode` = wezterm-gui, openwhispr, sherpa-onnx-ws-win32-x64, claude, codex, code -> 0; logi_download_assistant*, googledrivefs, crossdeviceservice, searchindexer, mdnsresponder, schedul2, intel_pie_service -> 1.
   - `DefaultIOPriorities` = searchindexer 0, logi_download_assistant* 0, everything 1, googledrivefs 1, schedul2 1, crossdeviceservice 1.
   - `DefaultMemoryPriorities` = discord/slack/beeper/joplin/phoneexperiencehost 2; googledrivefs/crossdeviceservice/searchindexer/intel_pie_service 1; logi_download_assistant* 0.
   - `InstanceLimitedProcesses` = `logi_download_assistant*.exe;1`, `ApplyInstanceCountLimitsToAllUsers=true`.
   - `StartupBoostRules` = `wezterm-gui.exe;above normal;10;1,code.exe;above normal;15;1,obsidian.exe;above normal;10;1`.
   - `DefaultPriorities` += googledrivefs, crossdeviceservice, joplin, phoneexperiencehost -> below normal.
   - `OocExclusions` += `sherpa-onnx-ws-win32-x64.exe`.
5. **winget, non-disruptive set** (apps not running): Microsoft.EdgeWebView2Runtime, Microsoft.Edge, .NET 8/9/10 runtimes, Microsoft.PowerToys, Perplexity.Comet, Amazon.Kiro, UnslothAI.Unsloth. Defer Git (Git Bash in use), Tailscale (drops tailnet), Intel radio drivers, WSL packages, Docker, pnpm 12/Node/uv majors, and WezTerm to a maintenance window.
6. `Update-MpSignature`.
