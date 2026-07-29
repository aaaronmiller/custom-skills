#!/usr/bin/env python3
"""Refresh Living Documents projections after Markdown changes without editing Markdown."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

CORPUS = Path.home() / "LIVING_DOCUMENTS"
LD = Path(__file__).with_name("ld")
POLL_SECONDS = float(os.environ.get("LIVING_DOCUMENTS_WATCH_POLL_SECONDS", "2"))
DEBOUNCE_SECONDS = float(os.environ.get("LIVING_DOCUMENTS_WATCH_DEBOUNCE_SECONDS", "1"))


def snapshot() -> str:
    """Hash source metadata only; generated runtime files are outside CORPUS."""
    digest = hashlib.sha256()
    for path in sorted(CORPUS.rglob("*.md")):
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        digest.update(str(path.relative_to(CORPUS)).encode("utf-8"))
        digest.update(f"{stat.st_mtime_ns}:{stat.st_size}".encode("ascii"))
    return digest.hexdigest()


def refresh() -> bool:
    result = subprocess.run(
        [str(LD), "sync", "--all", "--no-index-write"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        print("living-documents projection refresh complete", flush=True)
        return True
    print(f"living-documents projection refresh failed: {result.stderr.strip()}", file=sys.stderr, flush=True)
    return False


def main() -> int:
    if not CORPUS.is_dir() or not LD.is_file():
        print("living-documents projection watcher: required corpus or ld command is missing", file=sys.stderr)
        return 1
    observed = snapshot()
    pending_at: float | None = None
    while True:
        time.sleep(POLL_SECONDS)
        current = snapshot()
        if current != observed:
            observed = current
            pending_at = time.monotonic()
            continue
        if pending_at is not None and time.monotonic() - pending_at >= DEBOUNCE_SECONDS:
            if refresh():
                pending_at = None


if __name__ == "__main__":
    raise SystemExit(main())
