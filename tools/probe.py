#!/usr/bin/env python3
"""Probe Worms W.M.D. bundles and report their XOM section structure.

    python tools/probe.py <file-or-dir> [...]
    python tools/probe.py "$WMD_INSTALL/DataPC/Bundles"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wmdmod.xom import scan  # noqa: E402

READ_LIMIT = 2 << 20  # 2 MiB header window is plenty to see the structure


def targets(args: list[str]) -> list[Path]:
    if not args:
        install = os.environ.get("WMD_INSTALL")
        if not install:
            sys.exit("give a path, or set WMD_INSTALL")
        args = [str(Path(install) / "DataPC" / "Bundles")]

    found: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            found += sorted(
                q for q in p.iterdir() if q.suffix.lower() in {".bdl", ".xom"}
            )
        elif p.is_file():
            found.append(p)
        else:
            print(f"skip (not found): {p}", file=sys.stderr)
    return found


def main() -> int:
    files = targets(sys.argv[1:])
    if not files:
        print("nothing to probe", file=sys.stderr)
        return 1

    print(f"{'file':<24}{'size':>13}  magic  sections")
    print("-" * 78)
    all_types: dict[str, int] = {}

    for f in files:
        x = scan(f, read_limit=READ_LIMIT)
        tags = ", ".join(f"{k}={v}" for k, v in sorted(x.tag_counts.items()))
        magic = "MOIK" if x.has_magic else "----"
        print(f"{f.name:<24}{x.size:>13,}  {magic}   {tags or '(none)'}")
        for t in x.type_names:
            all_types[t] = all_types.get(t, 0) + 1

    if all_types:
        print(f"\nXOM classes seen (in first {READ_LIMIT >> 20} MiB of each):")
        for name, n in sorted(all_types.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {n:>3}x  {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
