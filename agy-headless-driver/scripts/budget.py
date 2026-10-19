#!/usr/bin/env python3
"""budget.py: size files for an agy context pack or read list, in KB and estimated tokens.

Usage:
  python3 budget.py FILE_OR_GLOB [...] [--pack-limit 40000] [--window 200000]

Estimates use 4.0 bytes per token for prose and Markdown and 3.3 for source code,
which is accurate enough for planning (within about 15 percent for English text).
Reports each file, the total, and a verdict against the pack limit and the
recommended Claude peak residency (60 percent of the window).

Exit codes: 0 within the pack limit; 3 over the pack limit; 4 a path is missing or nothing matched.
This makes it usable as a driver verify command for pack-building units.
"""
import argparse
import glob
import os
import sys

CODE_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".c", ".h", ".cpp",
    ".svelte", ".sh", ".rb", ".php", ".cs", ".kt", ".swift", ".sql", ".json", ".yaml", ".yml", ".toml",
}


def est_tokens(path: str, size: int) -> int:
    ratio = 3.3 if os.path.splitext(path)[1].lower() in CODE_EXT else 4.0
    return int(size / ratio)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--pack-limit", type=int, default=40000, help="token limit for a context pack")
    ap.add_argument("--window", type=int, default=200000, help="model context window in tokens")
    args = ap.parse_args()

    files = []
    missing = False
    for p in args.paths:
        matches = glob.glob(p, recursive=True) or [p]
        for m in matches:
            if os.path.isdir(m):
                for root, _, names in os.walk(m):
                    files.extend(os.path.join(root, n) for n in names)
            elif os.path.isfile(m):
                files.append(m)
            else:
                print(f"missing: {m}", file=sys.stderr)
                missing = True

    total_b = total_t = 0
    rows = []
    for f in sorted(set(files)):
        b = os.path.getsize(f)
        t = est_tokens(f, b)
        total_b += b
        total_t += t
        rows.append((t, b, f))

    rows.sort(reverse=True)
    print(f"{'tokens':>9} {'KB':>8}  file")
    for t, b, f in rows:
        flag = "  <- read by range only" if b > 40 * 1024 else ""
        print(f"{t:>9,} {b / 1024:>8.1f}  {f}{flag}")
    resident_target = int(args.window * 0.6)
    print("-" * 60)
    print(f"{total_t:>9,} {total_b / 1024:>8.1f}  TOTAL ({len(rows)} files)")
    print(f"pack limit {args.pack_limit:,} tokens: {'OK' if total_t <= args.pack_limit else 'OVER by ' + format(total_t - args.pack_limit, ',')}")
    print(f"peak residency target {resident_target:,} tokens ({resident_target * 4 // 1024} KB prose): "
          f"{'OK as a whole-read set' if total_t <= resident_target else 'too large to load whole; build a pack'}")
    if missing or not rows:
        print("FAIL: missing paths or no files matched", file=sys.stderr)
        return 4
    return 0 if total_t <= args.pack_limit else 3


if __name__ == "__main__":
    sys.exit(main())
