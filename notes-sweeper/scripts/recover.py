#!/usr/bin/env python3
"""Monthly notes snapshot + parse. Proven 2026-10-21: 78 NPP tabs + 120 Notepad bins -> 81 extracted.
Usage: python3 recover.py [--run-dir ~/agent-notes/recovery/<TS>Z]
Read-only on live apps; snapshots go read-only after hashing. Never touches dossiers/vault."""
import argparse, csv, hashlib, os, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

WIN_BASE = Path("/mnt/c/Users/Administrator")
NPP = WIN_BASE / "AppData/Roaming/Notepad++"
NP = WIN_BASE / "AppData/Local/Packages/Microsoft.WindowsNotepad_8wekyb3d8bbwe/LocalState"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", default=None)
    a = ap.parse_args()
    run = Path(a.run_dir) if a.run_dir else Path.home() / "agent-notes/recovery" / (datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ"))
    snap, ext, rep = run/"source-snapshots", run/"extracted-exact", run/"reports"
    for d in [snap/"windows-notepad", snap/"notepad-plus-plus", ext, rep]: d.mkdir(parents=True, exist_ok=True)
    # 1. snapshot (copy, never move)
    if (NP).exists():
        shutil.copytree(NP, snap/"windows-notepad/LocalState", dirs_exist_ok=True)
    for name in ["backup", "session.xml", "config.xml"]:
        src = NPP/name
        if src.is_dir(): shutil.copytree(src, snap/f"notepad-plus-plus/{name}", dirs_exist_ok=True)
        elif src.is_file(): shutil.copy2(src, snap/"notepad-plus-plus"/name)
    # 2. hash + read-only
    rows = []
    for root, _, files in os.walk(snap):
        for f in files:
            p = Path(root)/f
            rows.append([str(p.relative_to(run)), p.stat().st_size, sha(p)])
    with open(rep/"source-hashes.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["path","bytes","sha256"]); w.writerows(rows)
    os.system(f"chmod -R a-w {snap}")
    # 3. NPP parse: session.xml -> backup buffers
    n_npp = 0
    sess = snap/"notepad-plus-plus/session.xml"
    bak = snap/"notepad-plus-plus/backup"
    if sess.is_file() and bak.is_dir():
        bakmap = {}
        for f in os.listdir(bak):
            bakmap[f] = bak/f
            if "@" in f: bakmap.setdefault(f.split("@")[0], bak/f)
        for fe in ET.parse(sess).getroot().findall(".//File"):
            bp = (fe.get("backupFilePath") or "").replace("\\","/").split("/")[-1]
            hit = bakmap.get(bp) or bakmap.get(bp.split("@")[0])
            if hit and hit.is_file():
                fn = (fe.get("filename") or "untitled").replace("\\","/").split("/")[-1]
                shutil.copy2(hit, ext/(fn + ".recovered")); n_npp += 1
    # 4. Notepad parse: GUID .bin UTF-16
    n_np = 0
    ts = snap/"windows-notepad/LocalState/TabState"
    if ts.is_dir():
        for f in sorted(os.listdir(ts)):
            if f.endswith(".bak") or not f.endswith(".bin") or ".0.bin" in f or ".1.bin" in f: continue
            data = (ts/f).read_bytes()
            strs = re.findall(rb"(?:[\x20-\x7e]\x00){8,}", data)
            texts = [s.decode("utf-16-le") for s in strs if len(s.decode("utf-16-le").strip()) > 4]
            if not texts: continue
            longest = max(texts, key=len)
            paths = [t for t in texts if re.match(r"^[A-Z]:\\", t)]
            h = hashlib.sha256(longest.encode()).hexdigest()[:8]
            name = (paths[0].replace("\\","/").split("/")[-1] if paths else f.replace(".bin",""))[:40]
            safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")[:40] or "notepad-tab"
            (ext/f"{safe}-{h}.recovered.md").write_text(longest); n_npp += 1
    print(f"run: {run}\nsnapshots: {len(rows)}\nnpp recovered: {n_npp}\nnotepad recovered: {n_np}")

if __name__ == "__main__":
    raise SystemExit(main())
