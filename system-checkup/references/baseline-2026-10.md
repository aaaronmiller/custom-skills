# Baseline from the 2026-10-13 checkup (compare the next run against these)

Report: https://claude.ai/code/artifact/a23682f2-5cd6-47c3-ab76-a81af24c1eaf (local: `C:\performance-diagnostics\checkup-20261013\report\SPECTRE-16-checkup.html`)

| Measure | 2026-10-13 | Better next time if |
|---|---|---|
| OS build | 27965.1 (expired Canary) | 28120.x or newer, WU succeeding |
| WU failed downloads (event 31) | 337 since mid-July, ~26/week | 0 |
| SFC | 187 unrepairable, all UserExperience-FileExp icons | clean |
| C: free / D: free | 120.4 GB / 309.6 GB | C: > 150 GB after the removal default set |
| WSL ext4.vhdx / used inside | 371.8 GB / 307 GB | shrinking (`wsl --manage Ubuntu --set-sparse true` needs a shutdown) |
| RAM median / p95 (Aug 15-Sep 10, v1 telemetry) | 92.5% / 97.0% | below 88% median |
| Samples >= 90% RAM | 67% | below 40% |
| Hard faults p95 | 2,020/s | below 500/s |
| Resource-exhaustion events (2004) | 0 since 2026-08-20 | still 0 |
| Commit at snapshot | 35.0 / 45.6 GB | |
| Top private commit | vmmemWSL 7.9 GB, Chrome 5.8 GB, Windows Sandbox 4.0 GB (session open), Intel ICPS 2.6 GB | Intel ICPS gone |
| Unclean shutdowns since July | 6 (bugchecks 0xD1 2026-09-02, 0x3B 2026-07-21) | none; keep the next minidump |
| BT disconnects (Kernel-PnP 1010) | kbd peak 26/day (Sep), mouse peak 27/day (Oct 3) | single digits after the driver update |
| Telemetry | v1 dead since 2026-09-10; v2 written, not yet registered | `-Status` Healthy |
| Lasso | 14 of 15 rule targets effective; Pro features unused | v3 rules live, logi pinned and capped |
| Removal default set | ~42.6 GB (Windows caches 22.0, WSL 18.7, temp 1.9); duplicates all opt-in (421 copies, 13.5 GB) | |
| Removal with opt-ins | ~125 GB | |
| node_modules (WSL) | 155 trees, 34 GB, 68 npm projects | fewer npm, fewer stale |
| Security | BitLocker off, tamper protection off, no full scan ever, Edge/WebView2 at 145 | all fixed |
