# Process Lasso 18 - prolasso.ini cheat sheet (verified 2026-10-13)

Source: https://bitsum.com/apps/process-lasso/docs/reference/ini-config/ plus observed engine behaviour.

## Safe edit procedure
1. Live file: `HKLM\SOFTWARE\ProcessLasso\ConfigFolderEx` + `\prolasso.ini` (currently the Desktop `...[FTUApps]\Data\config`). UTF-16LE with BOM.
2. Back it up. **Close the GUI** (`ProcessLasso.exe`; leave the `ProcessGovernor` service running). An open GUI overwrites hand edits on its next save.
3. Edit. The governor notices the timestamp/size change and reloads automatically within about a second.
4. Verify: tail `processlasso.log` next to the config folder; read a target process's affinity from an **elevated** shell (unelevated reads return 0x0000 for SYSTEM processes); confirm the engine lowercased/re-sorted list keys (proof of a successful parse).
5. Restart the GUI unelevated (Start menu, or `Start-Process` from a non-admin shell).

There is no rule CLI in v18 (no plcmd). Installer supports `/importconfigfrom=`; runtime supports `/ConfigFolder=`, `/SetActiveProfile=`.

## Key formats
| Key | Format | Example |
|---|---|---|
| `DefaultAffinitiesEx` | `match,delay_ms,cpus,...` cpus `0-3;6;8-11` or `all` | `everything.exe,0,8-15` |
| `CPUSets` | `match,sets,...` sets = `(group/cpus)` items | `discord.exe,(0/8-15)` |
| `DefaultPriorities` | `match,priority,...` (`idle`, `below normal`, `normal`, `above normal`, `high`) | `slack.exe,below normal` |
| `EfficiencyMode` | `match,mode,...` 1 = on, 0 = off | `wezterm-gui.exe,0` |
| `DefaultIOPriorities` | `match,value,...` 0 very low .. 2 normal .. 4 critical | `searchindexer.exe,0` |
| `DefaultMemoryPriorities` (Pro) | `match,value,...` 0 lowest .. 5 normal | `discord.exe,2` |
| `InstanceLimitedProcesses` (Pro) | `match;max,...` | `logi_download_assistant*.exe;1` |
| `StartupBoostRules` | `match;priority;seconds;efficiency,...` | `code.exe;above normal;15;1` |
| `OocExclusions` (ProBalance) | comma list | `claude.exe,codex.exe,vmmemwsl,vmmemwsl.exe` |
| `WatchdogRules2` (Pro) | 12 `;` fields per rule | `leaky.exe;1;1;2048.00;30000;0;1;1;-;-;-;-` |
| `DefaultPowerSchemes` (Pro) | `match;plan name,...` | |
| `KeepRunningProcessesEx` (Pro) | `match;command_line;;elevate,...` | |

Flat namespace: section headers are cosmetic, and the **first** occurrence of a duplicated key wins. Flat exe lists use **commas** (a semicolon-separated OocExclusions was silently dropped in August). Wildcards match names (`MatchWildcardsToPathnames=true`).

## Hybrid-CPU guidance (Bitsum)
- Prefer CPU Sets (soft) over hard affinity for anything with a UI. Keep hard affinity for pure background daemons.
- Efficiency Mode off = keep a process out of EcoQoS/E-cores; on = push background work to E-cores.
- Never ProBalance-restrain `vmmemWSL`: throttling the VM throttles every agent at once.
- Leave SmartTrim trimming/standby-clear actions off on this box (they manufacture hard faults). Leave IdleSaver off (agents run while the user is idle).

## Rules live as of 2026-10-13
`DefaultAffinitiesEx`: notepad/notepad++ -> 0-7; everything, tailscaled, usbipd, abdownloadmanager, localsend_app, logi_download_assistant (DEAD: wrong name), searchindexer, esrv -> 8-15.
`DefaultPriorities`: discord, slack, beeper, msedgewebview2 -> below normal.
`OocExclusions`: claude, codex, openwhispr, vmmemwsl(.exe), wezterm-gui. `UseEfficiencyMode=true`.
Proposed v3 additions are listed in `references/improvement-pass.md`.
