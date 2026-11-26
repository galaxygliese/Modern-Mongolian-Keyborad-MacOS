#!/usr/bin/env python3
"""Check that the installed keyboards type exactly what scripts/layouts.py says.

Reads every key x modifier combination back through macOS (UCKeyTranslate), so it
also proves macOS accepted and compiled the .keylayout files. Install first:
    ./install.sh && python3 scripts/verify.py
"""

import json
import subprocess
import sys
from pathlib import Path

from build import LAYERS, key_tables, source_id
from layouts import LAYOUTS

DUMP = Path(__file__).with_name("dump_layout.swift")


def show(text: str) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in text) or "(nothing)"


def main() -> int:
    failures = 0
    for layout in LAYOUTS:
        states = [f"{name}={state}" for name, state in LAYERS.items()]
        dump = subprocess.run(["swift", str(DUMP), source_id(layout), *states],
                              capture_output=True, text=True)
        if dump.returncode != 0:
            print(dump.stderr.strip())
            return 1
        actual = json.loads(dump.stdout)
        expected = key_tables(layout)
        mismatches = [
            f"  {layer} key {code}: expected {show(want)}, got {show(actual[layer][str(code)])}"
            for layer, table in expected.items()
            for code, want in sorted(table.items())
            if actual[layer][str(code)] != want
        ]
        checked = sum(len(t) for t in expected.values())
        print(f"{layout['name']}: {checked - len(mismatches)}/{checked} key outputs match")
        if mismatches:
            print(*mismatches, sep="\n")
        failures += len(mismatches)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
