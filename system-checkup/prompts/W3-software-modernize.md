# Worker W3 — Software currency + modernization research (Rust ports, RE-era forks, faster replacements)

Research worker. Use `web_search` heavily (GitHub repos, release pages, Hacker News, lobste.rs, reputable blogs). Today is {{DATE}} — prefer sources from 2026. Read the local inventory files listed; write ONLY the output file. Do not install, update or uninstall anything.

## Machine & owner profile
SPECTRE-16: HP Spectre x360 16 (i7-1360P 4P+8E, **16 GB soldered RAM — memory is the binding constraint**, Arc A370M 4 GB + Iris Xe, 1 TB NVMe). Windows 11 Insider 27965 (being upgraded to 28120 Experimental 26H1). Owner is a power user running 4-7 coding-agent CLIs at once inside WSL2 Ubuntu 24.04 (claude, codex, omp/oh-my-pi, muse, opencode, hermes, jcode, kilocode, gemini-cli), WezTerm, Chrome with 30-60 tabs, VS Code + Antigravity + Kiro, Obsidian, Discord/Slack/Beeper, OpenWhispr (voice dictation), Process Lasso Pro, Everything, Tailscale, LocalSend, Acronis. Prefers pnpm/bun over npm, Rust-native tools, and anything that cuts RAM.

## Inputs (read these)
- Windows programs: `/mnt/c/performance-diagnostics/{{CHECKUP}}/raw/programs-compact.txt` (name | version | publisher)
- Store/Appx: `/mnt/c/performance-diagnostics/{{CHECKUP}}/raw/appx.csv`
- winget view: `/mnt/c/performance-diagnostics/{{CHECKUP}}/raw/winget-list.txt` and `winget-upgrade.txt` (same dir)
- Startup items: `/mnt/c/performance-diagnostics/{{CHECKUP}}/raw/startup.csv`; running processes: `processes.csv` (same dir)
- WSL side: `/mnt/c/performance-diagnostics/{{CHECKUP}}/workers/W1-wsl-audit.md` (globals, cargo tools, uv tools, versions)
- Also list WSL user-installed CLIs yourself: `ls ~/.cargo/bin ~/.local/bin ~/.bun/bin ~/.npm-global/bin /home/linuxbrew/.linuxbrew/bin 2>/dev/null`

## Tasks
1. **Outdated / EOL / abandoned**: from the inventories, flag software that is (a) clearly out of date vs. the latest release (check the top ~40 most important apps: browsers, editors, terminals, runtimes, drivers suites, Acronis, VMware, PowerToys, 7-Zip, Git, Node, Python, .NET, WSL, Docker, Obsidian, Discord, etc.), (b) end-of-life or abandoned upstream (e.g. Classic Sticky Notes, iTunes/Bonjour leftovers, 3uTools, old SDK bits), (c) duplicated (multiple tools doing the same job — e.g. several download managers, several AI IDEs, several terminals, multiple Node/Python installs, clipboard managers). Give latest version + source URL for each flagged item.
2. **Modernization candidates** — for each category the owner actually uses, propose the best 2026 replacement or complement, emphasizing **Rust/Zig/Go rewrites, lower RAM, and projects born from the 2026 reverse-engineering/"port it to Rust" wave** (e.g. Rust ports/forks of coding-agent harnesses, Rust terminal emulators, Rust file managers, Rust replacements for Electron apps, Rust coreutils/sudo-rs, fish 4, nushell, uv/ruff/ty, oxc/biome/rolldown, bun/deno/pnpm 12, Zed, Ghostty/Rio/WezTerm alternatives on Windows, Czkawka/dua/gdu/dust for disk, Kondo for build artifacts, ripgrep-all, yazi, zellij, atuin, bottom/btop, mise, Tauri-based replacements for Electron chat apps, local Whisper/Parakeet in Rust/C++ for OpenWhispr). Only recommend projects you verify exist via web_search with a repo/release URL and an activity date in 2026. For each: what it replaces, why (RAM/CPU/startup numbers if published), maturity on **Windows** vs WSL, install command (winget/scoop/cargo/uv/bun), and risk.
3. **Coding-agent harness landscape (Oct 2026)**: which Rust/Go-native or lighter-weight agent CLIs/forks are credible right now (memory per session matters: Node-based harnesses cost ~300-800 MB each). Include anything relevant to omp/oh-my-pi, opencode, codex (Rust), claw-code/ClawCode, ante, goose, aider, etc. — verify each with a URL.
4. **Package-manager hygiene**: concrete recommendations for npm→pnpm/bun migration on this box (Windows has npm-only globals `pnpm@10.28.2`; pnpm 12 exists; bun not installed on Windows), corepack status in Node 26, and whether to install scoop apps vs winget.

## Output
Write `/mnt/c/performance-diagnostics/{{CHECKUP}}/workers/W3-software-modernize.md` with sections:
`## TL;DR` (8 bullets max) · `## Outdated / EOL / duplicates` (table: app | installed | latest | status | action | source) · `## Modernization picks` (table: category | current | recommended | why (numbers) | Windows maturity | install | risk | source) · `## Agent-harness landscape` (table) · `## Package managers` · `## Quick wins (ordered list of exact commands)` · `## Sources`.
Mark anything unverified as UNVERIFIED. Never invent version numbers or projects.
