# Daily Ingest Setup — Automated Pipeline

## Overview

The daily ingest pipeline runs automatically to capture new conversations from all
configured sources. It is idempotent and incremental — only new or changed data
is processed.

## Configuration

All configuration lives in `~/.prompt-mine/config.yaml`:

```yaml
# Prompt Mine Configuration

database:
  path: ~/.prompt-mine/prompt_mine.db

sources:
  claude_code:
    enabled: true
    projects_dir: ~/projects              # Scan for .claude/ directories
    include_checkpoints: true
    last_ingested: null                    # Auto-updated after each run

  roo_kilo:
    enabled: true
    storage_path: ~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline
    include_kilo: true
    kilo_path: ~/.config/Code/User/globalStorage/kilocode.kilo-code

  openai:
    enabled: false
    export_dir: null                       # Set to unzipped export path

  gemini:
    enabled: false
    export_dir: null                       # Set to Takeout path

  anthropic:
    enabled: false
    export_file: null                      # Set to export JSON path

embedding:
  model: "all-MiniLM-L6-v2"
  dimensions: 768
  device: "cpu"
  batch_size: 64

summarization:
  method: "extractive"                    # "extractive" or "abstractive"
  max_summary_length: 200
  response_truncation_lines: 50           # Last N lines for truncated display
  full_response_threshold: 20000          # Store full text below this; truncate above

capture_api:
  enabled: false
  port: 8420

tagging:
  auto_tag: true
  confidence_threshold: 0.3

clustering:
  enabled: true
  recluster_threshold: 500                # Re-cluster after N new conversations
  last_clustered: null
```

## Scheduling Options

### Option 1: Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * /usr/bin/python3 ~/.prompt-mine/scripts/daily_ingest.py --all >> ~/.prompt-mine/ingest.log 2>&1

# Run every 6 hours for more frequent updates
0 */6 * * * /usr/bin/python3 ~/.prompt-mine/scripts/daily_ingest.py --incremental >> ~/.prompt-mine/ingest.log 2>&1
```

### Option 2: systemd Timer (Linux)

Create `~/.config/systemd/user/prompt-mine-ingest.service`:

```ini
[Unit]
Description=Prompt Mine Daily Ingest
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/.prompt-mine/scripts/daily_ingest.py --all
StandardOutput=journal
StandardError=journal
```

Create `~/.config/systemd/user/prompt-mine-ingest.timer`:

```ini
[Unit]
Description=Run Prompt Mine Ingest Daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
systemctl --user daemon-reload
systemctl --user enable prompt-mine-ingest.timer
systemctl --user start prompt-mine-ingest.timer
```

### Option 3: launchd (macOS)

Create `~/Library/LaunchAgents/com.prompt-mine.ingest.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.prompt-mine.ingest</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOU/.prompt-mine/scripts/daily_ingest.py</string>
        <string>--all</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/YOU/.prompt-mine/ingest.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOU/.prompt-mine/ingest-error.log</string>
</dict>
</plist>
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/com.prompt-mine.ingest.plist
```

## Incremental Extraction

The `--incremental` flag (default behavior) only processes new data:

1. **Check `ingest_log`** for the last successful run timestamp per provider
2. **Scan source directories** for files newer than the last ingest
3. **Compare source hashes** to skip already-processed files
4. **For partially-processed files** (e.g., a JSONL file with new lines appended),
   only extract new turns

The `--all` flag forces a full re-scan but still uses deduplication to avoid
inserting duplicate records.

## Monitoring

Check ingest status:
```bash
python scripts/daily_ingest.py --status
```

Output:
```
Prompt Mine Ingest Status
=========================
Database: ~/.prompt-mine/prompt_mine.db
Size: 847.3 MB

Last Ingest:
  claude_code: 2025-01-15T14:30:00Z (312 conversations, 8456 turns)
  roo_kilo:    2025-01-15T14:30:12Z (125 conversations, 2755 turns)
  openai:      2025-01-14T02:00:05Z (423 conversations, 8934 turns)
  gemini:      never configured
  anthropic:   2025-01-14T02:00:08Z (312 conversations, 7456 turns)

Totals:
  Conversations: 1,247
  Total turns:   28,456
  User turns:    9,832
  Tags applied:  3,891
  Embeddings:    28,456

Next scheduled: 2025-01-16T02:00:00Z
```
