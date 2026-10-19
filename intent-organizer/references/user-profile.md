# Owner profile (Aaron, SPECTRE-16) - concepts that help infer intent

Keep this current. Workers receive the "Who" and "Projects" sections verbatim.

## Who
Power user on an HP Spectre x360 16 (i7-1360P, Intel Arc A370M, 16 GB soldered RAM), Windows 11 Insider, with 4-7 AI coding agents running in WSL2 Ubuntu (Claude Code, Codex, omp/oh-my-pi, opencode, hermes, muse, kilocode, gemini). Second Windows laptop (i7-13800H, 32 GB). Downloads a lot and keeps almost everything deliberately; uses Downloads and the Desktop as storage. Names folders bluntly ("mac shit", "Shit to SELL", "GAY" = an old dump). Periodically sweeps loose files into dated dump folders such as `Desktop\txt md ps1 zip 7-11-26` (= July 11, 2026).

## Projects and interests (strong intent signals)
- AI agent harnesses, skills, prompts, PRDs, model rankings (ARDF dashboards, model value analysis), Claude Code status lines and settings, MCP servers.
- Local AI on the Arc GPU: llama.cpp SYCL/Vulkan builds, OpenVINO, Intel AI Playground, Unsloth, LM Studio, Ollama, GGUF/safetensors models (`D:\modelsx`).
- Voice: OpenWhispr dictation and transcripts, Parakeet ASR, VoiceStudio/OmniVoice TTS, notification sounds.
- Hardware tinkering: ESP32, M5Stack Cardputer / ESP-BOX, M5Burner, NodeMCU, CH341 drivers, Arduino, Raspberry Pi, ClockworkPi, Flipper (qFlipper), USB tools; firmware dumps (`0891E` = this HP laptop's BIOS/ME).
- Other machines: Surface laptop and Chromebook running Linux, the second Windows laptop ("new box"/"other laptop" setup notes), MacBook (migration, eBay sale), iPhone/iPad tooling.
- Windows tuning: Process Lasso, power plans, admin/remediation scripts, PowerToys, Tron, system audits.
- Music production: Ableton Live, FL Studio (Image-Line), Tracktion.
- Writing: the "Cocktailmanship" article. Legal: a workplace grievance (T. Flack). Selling on eBay. Job searching.
- Notes: Obsidian (vault `Documents\chetaz`, mirror `D:\chetaz`), Joplin, Zettlr, Apple Notes exports.

## Never touch (protected)
`Documents\chetaz` and `D:\chetaz` (Obsidian vault + mirror) · `Desktop\Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]` (live Process Lasso config) · `C:\0.defenderexclusions`, `D:\0.defenderexclusions` · `D:\SPECTRE-16-UGLYBETTY.tibx` (Acronis backup) · `D:\casr-mirror` (rotated by a cron job) · `C:\performance-diagnostics` · any living-document folder (`*.livingdoc`) · `.claude`, `.ssh`, `.config` in the home folder.

## Security stance
Keymakers, activators, cracked installers (FileCR), MDM-bypass tools, password/credential files and the owner's security settings are intentional. Exclude them from every plan; do not read, move, isolate or comment on them.

## App-owned folders (leave in place)
Folders an app created where it expects them: `Documents\Image-Line` (FL Studio), `Documents\Virtual Machines` (VMware), `Documents\WindowsPowerShell` / `PowerShell`, `Documents\Zoom`, `Documents\PowerToys`, `Documents\Tracktion*`, `Documents\Ableton`, `Documents\My Games`, `Documents\Visual Studio*`, `Documents\Arduino`, plus any dot-folder (`.claude` on the Desktop holds Claude Code settings for sessions started there).

Found in the 2026-10 run (all stay put): `Documents\MAXON`, `AI-Playground`, `R-TT`, `VTune`, `Advisor` (Intel Advisor project), `bytepad`, `Codex` (PowerShell profile points at it), `Septabee`, `OBDistGit` (live git repo), `Zettlr Tutorial` (open Zettlr workspace), `mouse mapping` (X-Mouse Button Control settings); `Downloads\ABDM` (AB Download Manager's download folder), `Downloads\Telegram Desktop` (Telegram save folder); `Desktop\mouse cursors` (active cursor scheme), `Desktop\0.NEWBOX` (Startup shortcut runs DesktopInfo from it), `Desktop\Last30Days` and `Desktop\hermes` (agent output folders); `Music\evil-laugh.wav` (live notification sound), `Music\YTdownloads` (the owner's yt-dlp script output); home `wsl-kernel` (kernel build target), `JoplinBackup`, `Glaido`, `Hermes`, `ExplorerConfig-Rollback`, `agent_trash` (agents' trash bin, purged weekly), `scoop`, `Postman`, `CrossDevice`, `vscode-remote-wsl`; everything in `D:\modelsx` (the model library). `Pictures\Phhhoooooooottttoooos` (93 GB photo archive) and `Pictures\Shit to SELL` are topic folders that stay.

## How to run workers on this machine
Headless omp from Windows Git Bash, one background task per worker:
`MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash -l <skill>/scripts/run_worker.sh <brief-name> 55m high`
(login shell = provider keys; background task, not nohup; no --auto-approve.)

## Intent recovery source
`cass` (coding-agent session search) indexes the owner's agent sessions. For `unsure` items, search it for the file name - many downloads were fetched during an agent session that explains why.

## Preferences
Group-level decisions with sensible defaults ON; one short Unsure pile; full undo; no nagging about security; spaces, not hyphens, in folder names.
