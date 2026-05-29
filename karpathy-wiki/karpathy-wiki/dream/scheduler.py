#!/usr/bin/env python3
"""
Dream Agent Scheduler v3 — Sleep-Time Compute Orchestrator.

Triggers the dream agent on:
  - systemd --user idle timer (primary, 30min check)
  - Wall-clock fallback if no idle detected for 4 hours
  - Manual invocation via CLI

Usage:
  python3 scheduler.py                  # Run one cycle (default idle=600s)
  python3 scheduler.py --cycle 3600     # One cycle with 1hr budget
  python3 scheduler.py --daemon         # Continuous daemon loop
  python3 scheduler.py --daemon --idle-check  # Check idle before running
"""
import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

DREAM_AGENT = Path(__file__).parent / "dream_agent.py"
STATE_FILE = Path(os.environ.get("AI_WIKI", Path.home() / "ai-wiki")) / ".meta" / "scheduler_state.json"

DAEMON_INTERVAL = int(os.environ.get("DAEMON_INTERVAL", "1800"))  # 30 min
WALL_CLOCK_FALLBACK = int(os.environ.get("WALL_CLOCK_FALLBACK", "14400"))  # 4 hours
DEFAULT_IDLE = int(os.environ.get("DEFAULT_IDLE", "600"))  # 10 min


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            pass
    return {"last_run": 0, "last_wall_clock_run": 0, "interaction_count": 0}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def check_idle() -> int:
    """Check OS-level idle time in seconds. Uses systemd's idle hint or uptime delta."""
    try:
        # Try last systemd user activity timestamp
        result = subprocess.run(
            ["loginctl", "show-user", os.environ.get("USER", "cheta"), "--property=IdleSinceHint"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "=" in result.stdout:
            val = result.stdout.strip().split("=", 1)[1]
            if val and val != "0":
                idle_since = int(val) / 1_000_000  # microseconds → seconds
                idle_seconds = int(time.time() - idle_since)
                return max(idle_seconds, 0)

        # Fallback: check /proc/uptime vs last command
        with open("/proc/uptime") as f:
            uptime_seconds = float(f.read().split()[0])
        # Rough proxy: if system has been up a while, assume some idle
        return DEFAULT_IDLE
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return DEFAULT_IDLE


def run_dream_cycle(idle_seconds: int = DEFAULT_IDLE, quiet: bool = False) -> dict:
    """Execute one dream agent cycle."""
    if not quiet:
        print(f"🌙 Running dream cycle at {datetime.now().strftime('%H:%M:%S')} "
              f"(idle_budget={idle_seconds}s)")

    cmd = [sys.executable, str(DREAM_AGENT), "--idle", str(idle_seconds)]
    if quiet:
        cmd.append("--quiet")

    result = subprocess.run(cmd, capture_output=False, text=True, timeout=7200)

    if result.returncode == 0:
        if not quiet:
            print(f"✅ Dream cycle complete (returncode=0)")
        return {"status": "ok", "idle_seconds": idle_seconds}
    else:
        if not quiet:
            print(f"⚠️  Dream cycle error (returncode={result.returncode})")
        return {"status": "error", "returncode": result.returncode,
                "stderr": result.stderr[:500] if result.stderr else ""}


def daemon_loop(interval: int = DAEMON_INTERVAL, idle_check: bool = False):
    """Continuous daemon loop for environments without systemd idle timer."""
    state = load_state()
    print(f"🌙 Dream daemon started (interval={interval}s, idle_check={idle_check})")
    print(f"   Press Ctrl+C to stop")

    try:
        while True:
            now = time.time()
            should_run = False

            # Interval trigger
            if now - state.get("last_run", 0) > interval:
                should_run = True

            # Wall-clock fallback (if idle_check enabled but never idle enough)
            if (idle_check and
                now - state.get("last_wall_clock_run", 0) > WALL_CLOCK_FALLBACK):
                should_run = True

            if should_run:
                idle_seconds = check_idle() if idle_check else DEFAULT_IDLE
                result = run_dream_cycle(idle_seconds=idle_seconds, quiet=True)
                state["last_run"] = now
                if idle_check:
                    state["last_wall_clock_run"] = now
                state["last_result"] = result.get("status", "unknown")
                save_state(state)

            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🌙 Daemon stopped")


def install_systemd_units():
    """Print instructions for setting up systemd idle timer (primary trigger mechanism)."""
    user = os.environ.get("USER", "cheta")
    dream_path = DREAM_AGENT.resolve()
    print("=" * 60)
    print("Systemd Idle Timer Setup Instructions")
    print("=" * 60)
    print(f"""
# 1. Create service unit: ~/.config/systemd/user/dream-agent.service
cat > ~/.config/systemd/user/dream-agent.service << 'SERVICE'
[Unit]
Description=Karpathy Wiki Dream Agent (Sleep-Time Compute)
Documentation=https://github.com/karpathy-wiki

[Service]
Type=oneshot
ExecStart={sys.executable} {dream_path} --idle 600
Environment=AI_WIKI={os.environ.get('AI_WIKI', str(Path.home() / 'ai-wiki'))}
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
SERVICE

# 2. Create idle timer: ~/.config/systemd/user/dream-agent.timer
cat > ~/.config/systemd/user/dream-agent.timer << 'TIMER'
[Unit]
Description=Dream agent idle timer (30min check)
Requires=dream-agent.service

[Timer]
OnActiveSec=5min
# Run when system has been idle for 5+ minutes
OnType=idle
IdleWaitSec=5min
OnUnitActiveSec=30min

[Install]
WantedBy=timers.target
TIMER

# 3. Enable and start
systemctl --user daemon-reload
systemctl --user enable --now dream-agent.timer
systemctl --user start dream-agent.timer

# 4. Verify
systemctl --user list-timers --all | grep dream-agent

# 5. To run manually:
systemctl --user start dream-agent.service
""")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dream Agent Scheduler v3")
    parser.add_argument("--cycle", type=int, default=0,
                        help="Run one cycle with N seconds idle budget. Overrides --idle.")
    parser.add_argument("--idle", type=int, default=DEFAULT_IDLE,
                        help="Idle seconds for budget calc (default: 600)")
    parser.add_argument("--daemon", action="store_true",
                        help="Run continuous daemon loop")
    parser.add_argument("--idle-check", action="store_true",
                        help="Check OS idle time before running (with --daemon)")
    parser.add_argument("--install", action="store_true",
                        help="Print systemd unit setup instructions")
    args = parser.parse_args()

    if args.install:
        install_systemd_units()
        sys.exit(0)

    if args.daemon:
        daemon_loop(interval=DAEMON_INTERVAL, idle_check=args.idle_check)
    else:
        idle_seconds = args.cycle if args.cycle > 0 else args.idle
        run_dream_cycle(idle_seconds=idle_seconds, quiet=False)
