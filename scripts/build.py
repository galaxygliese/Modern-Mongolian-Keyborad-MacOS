#!/usr/bin/env python3
"""Generate ModernMongolian.bundle and the layout charts from scripts/layouts.py.

    python3 scripts/build.py          # regenerate everything
    python3 scripts/build.py --check  # fail if committed output is stale
"""

import html
import plistlib
import sys
from pathlib import Path

from layouts import INVISIBLE_LABELS, LAYOUTS

VERSION = "1.0.0"
BUNDLE_ID = "com.galaxygliese.keyboardlayout.modernmongolian"
COPYRIGHT = "Copyright © 2026 Sodoo. Built for Mongolian Mac users."
ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "ModernMongolian.bundle"
DOCS = ROOT / "docs"

# US-QWERTY label -> (virtual key code, US base, US shift).
US_KEYS = {
    "a": (0, "a", "A"), "s": (1, "s", "S"), "d": (2, "d", "D"), "f": (3, "f", "F"),
    "h": (4, "h", "H"), "g": (5, "g", "G"), "z": (6, "z", "Z"), "x": (7, "x", "X"),
    "c": (8, "c", "C"), "v": (9, "v", "V"), "§": (10, "§", "±"), "b": (11, "b", "B"),
    "q": (12, "q", "Q"), "w": (13, "w", "W"), "e": (14, "e", "E"), "r": (15, "r", "R"),
    "y": (16, "y", "Y"), "t": (17, "t", "T"), "1": (18, "1", "!"), "2": (19, "2", "@"),
    "3": (20, "3", "#"), "4": (21, "4", "$"), "6": (22, "6", "^"), "5": (23, "5", "%"),
    "=": (24, "=", "+"), "9": (25, "9", "("), "7": (26, "7", "&"), "-": (27, "-", "_"),
    "8": (28, "8", "*"), "0": (29, "0", ")"), "]": (30, "]", "}"), "o": (31, "o", "O"),
    "u": (32, "u", "U"), "[": (33, "[", "{"), "i": (34, "i", "I"), "p": (35, "p", "P"),
    "l": (37, "l", "L"), "j": (38, "j", "J"), "'": (39, "'", '"'), "k": (40, "k", "K"),
    ";": (41, ";", ":"), "\\": (42, "\\", "|"), ",": (43, ",", "<"), "/": (44, "/", "?"),
    "n": (45, "n", "N"), "m": (46, "m", "M"), ".": (47, ".", ">"), "`": (50, "`", "~"),
    "space": (49, " ", " "),
}
DIGITS = "1234567890"

# Keys whose output never depends on the layout: code -> (unshifted, shifted).
_F = "\x10"  # function keys
SPECIAL = {
    36: ("\r", "\r"), 48: ("\t", "\t"), 51: ("\b", "\b"), 52: ("\x03", "\x03"),
    53: ("\x1b", "\x1b"), 65: (".", "."), 66: ("\x1d", "*"), 67: ("*", "*"),
    69: ("+", "+"), 70: ("\x1c", "+"), 71: ("\x1b", "\x1b"), 72: ("\x1f", "="),
    75: ("/", "/"), 76: ("\x03", "\x03"), 77: ("\x1e", "/"), 78: ("-", "-"),
    81: ("=", "="), 82: ("0", "0"), 83: ("1", "1"), 84: ("2", "2"), 85: ("3", "3"),
    86: ("4", "4"), 87: ("5", "5"), 88: ("6", "6"), 89: ("7", "7"), 91: ("8", "8"),
    92: ("9", "9"), 114: ("\x05", "\x05"), 115: ("\x01", "\x01"), 116: ("\x0b", "\x0b"),
    117: ("\x7f", "\x7f"), 119: ("\x04", "\x04"), 121: ("\x0c", "\x0c"),
    123: ("\x1c", "\x1c"), 124: ("\x1d", "\x1d"), 125: ("\x1f", "\x1f"),
    126: ("\x1e", "\x1e"),
    **{code: (_F, _F) for code in (*range(96, 114), 118, 120, 122)},
}

# Modifier layers in keyMap index order, with the UCKeyTranslate modifier state
# (EventRecord modifiers >> 8) used by verify.py to read each layer back.
LAYERS = {
    "base": 0, "shift": 2, "caps": 4, "option": 8, "shift_option": 10,
    "command": 1, "shift_command": 3, "control": 16,
}
MODIFIER_MAP = [  # first match wins
    "",
    "anyShift caps?",
    "caps",
    "anyOption caps?",
    "anyShift anyOption caps?",
    "command caps? anyOption?",
    "command anyShift caps? anyOption?",
    "anyControl anyShift? caps? anyOption? command?",
]


def us_control(label: str, base: str) -> str:
    if len(base) == 1 and base.isalpha() and base.isascii():
        return chr(ord(base) & 0x1F)
    return {"[": "\x1b", "\\": "\x1c", "]": "\x1d", "-": "\x1f", "§": "0"}.get(label, base)


def key_tables(layout: dict) -> dict[str, dict[int, str]]:
    """Output of every key code in every modifier layer."""
    tables: dict[str, dict[int, str]] = {name: {} for name in LAYERS}
    for label, (code, us_base, us_shift) in US_KEYS.items():
        base, shift = layout["keys"][label]
        caps = shift if layout["caps_uppercases"] and base.upper() == shift != base else base
        if label in DIGITS:
            option, shift_option = us_shift, layout["shift_option_digits"][label]
        elif label == "space":
            option = shift_option = "\u00a0"
        else:
            option, shift_option = us_base, us_shift
        row = {
            "base": base, "shift": shift, "caps": caps,
            "option": option, "shift_option": shift_option,
            "command": us_base, "shift_command": us_shift,
            "control": us_control(label, us_base),
        }
        for name, out in row.items():
            tables[name][code] = out
    for code, (plain, shifted) in SPECIAL.items():
        for name in LAYERS:
            tables[name][code] = shifted if "shift" in name else plain
    return tables


def xml_attr(text: str) -> str:
    """Escape for an XML attribute; invisible characters become numeric refs."""
    out = []
    for ch in text:
        cp = ord(ch)
        if ch in "&<>\"'" or cp < 0x20 or cp == 0x7F or ch in INVISIBLE_LABELS and ch != " ":
            out.append(f"&#x{cp:04X};")
        else:
            out.append(ch)
    return "".join(out)


def keylayout_xml(layout: dict) -> str:
    tables = key_tables(layout)
    maxout = max(len(s) for t in tables.values() for s in t.values())
    lines = [
        '<?xml version="1.1" encoding="UTF-8"?>',
        '<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">',
        "<!-- Generated by scripts/build.py from scripts/layouts.py. Do not edit. -->",
        # group 126 = Unicode; with a negative id it cannot clash with Apple's layouts.
        f'<keyboard group="126" id="{layout["id"]}" name="{layout["name"]}" maxout="{maxout}">',
        "  <layouts>",
        '    <layout first="0" last="255" modifiers="Modifiers" mapSet="ANSI"/>',
        "  </layouts>",
        '  <modifierMap id="Modifiers" defaultIndex="0">',
    ]
    for index, keys in enumerate(MODIFIER_MAP):
        lines.append(f'    <keyMapSelect mapIndex="{index}"><modifier keys="{keys}"/></keyMapSelect>')
    lines += ["  </modifierMap>", '  <keyMapSet id="ANSI">']
    for index, name in enumerate(LAYERS):
        lines.append(f'    <keyMap index="{index}"><!-- {name} -->')
        for code, out in sorted(tables[name].items()):
            lines.append(f'      <key code="{code}" output="{xml_attr(out)}"/>')
        lines.append("    </keyMap>")
    lines += ["  </keyMapSet>", "</keyboard>", ""]
    return "\n".join(lines)


def source_id(layout: dict) -> str:
    # macOS derives the id from the bundle id and layout name; this matches it.
    return f"{BUNDLE_ID}.keylayout.{layout['name'].replace(' ', '')}"


def info_plist() -> bytes:
    plist = {
        "CFBundleIdentifier": BUNDLE_ID,
        "CFBundleName": "Modern Mongolian",
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "CFBundleDevelopmentRegion": "en",
        "NSHumanReadableCopyright": COPYRIGHT,
    }
    for layout in LAYOUTS:
        plist[f"KLInfo_{layout['name']}"] = {
            "TISInputSourceID": source_id(layout),
            "TISIntendedLanguage": layout["language"],
            "TISIconIsTemplate": True,
        }
    return plistlib.dumps(plist, sort_keys=True)


def infoplist_strings(lang: str) -> str:
    return "".join(f'"{l["name"]}" = "{l["localized"][lang]}";\n' for l in LAYOUTS)


# ---------------------------------------------------------------- charts

UNIT, GAP = 58, 6
ROWS = [
    [("`", 1), *[(d, 1) for d in DIGITS], ("-", 1), ("=", 1), ("delete", 2)],
    [("tab", 1.5), *[(k, 1) for k in "qwertyuiop[]"], ("\\", 1.5)],
    [("caps", 1.75), *[(k, 1) for k in "asdfghjkl;'"], ("return", 2.25)],
    [("shift", 2.25), *[(k, 1) for k in "zxcvbnm,./"], ("shift", 2.75)],
    [("fn", 1.25), ("control", 1.25), ("option", 1.25), ("command", 1.5), ("space", 5.5),
     ("command", 1.5), ("option", 1.25), ("", 1.5)],
]
FONT_SIZE = {"base": 22, "shift": 15, "extra": 13, "us": 10}


def is_vertical_script(ch: str) -> bool:
    """Mongolian letters and punctuation lie sideways in horizontal text; digits do not."""
    return 0x1800 <= ord(ch) <= 0x18AF and not 0x1810 <= ord(ch) <= 0x1819


def svg_text(x: float, y: float, text: str, cls: str) -> str:
    """Draw `text` starting at (x, baseline y); invisible characters are drawn as tags."""
    tags = [INVISIBLE_LABELS[ch] for ch in text if INVISIBLE_LABELS.get(ch)]
    visible = "".join(ch for ch in text if ch not in INVISIBLE_LABELS)
    parts = []
    if tags:
        tag = "+".join(tags) + ("+" if visible else "")
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="tag {cls}">{tag}</text>')
        x += 6.5 * len(tag)
    if visible and any(map(is_vertical_script, visible)):
        # Rotate clockwise so the glyph stands upright, hanging down from the label top.
        size = FONT_SIZE[cls]
        ax, ay = x + size * 0.45, y - size * 0.95
        parts.append(f'<text x="{ax:.1f}" y="{ay:.1f}" class="{cls} mong" '
                     f'transform="rotate(90 {ax:.1f} {ay:.1f})">{html.escape(visible)}</text>')
    elif visible:
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}">{html.escape(visible)}</text>')
    return "".join(parts)


def chart_svg(layout: dict) -> str:
    width = 15 * UNIT
    parts = []
    y = 0.0
    for row in ROWS:
        x = 0.0
        for label, size in row:
            w = size * UNIT - GAP
            h = UNIT - GAP
            mapped = label in layout["keys"]
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" '
                         f'class="{"key" if mapped else "mod"}"/>')
            if mapped:
                base, shift = layout["keys"][label]
                parts.append(svg_text(x + 7, y + h - 9, base, "base"))
                if shift != base and shift != base.upper():
                    parts.append(svg_text(x + 7, y + 17, shift, "shift"))
                if label in DIGITS:
                    parts.append(svg_text(x + w - 6, y + 17, layout["shift_option_digits"][label],
                                          "extra"))
                if label != "space":
                    parts.append(svg_text(x + w - 6, y + h - 7, label, "us"))
            elif label:
                parts.append(f'<text x="{x + 7:.1f}" y="{y + h - 9:.1f}" class="modlabel">'
                             f"{label}</text>")
            x += size * UNIT
        y += UNIT
    height = y - GAP
    style = """
  .key { fill: #f6f8fa; stroke: #8c959f; }
  .mod { fill: #eaeef2; stroke: #d0d7de; }
  text { font-family: -apple-system, "Helvetica Neue", Arial, "Noto Sans Mongolian", sans-serif; fill: #1f2328; }
  .base { font-size: 22px; }
  .shift { font-size: 15px; fill: #57606a; }
  .extra { font-size: 13px; fill: #0969da; text-anchor: end; }
  .us { font-size: 10px; fill: #8c959f; text-anchor: end; }
  .tag.base, .tag.shift { font-size: 10px; font-weight: 600; }
  .modlabel { font-size: 11px; fill: #57606a; }
  .mong { font-family: "Noto Sans Mongolian", "Mongolian Baiti", sans-serif; }
  @media (prefers-color-scheme: dark) {
    .key { fill: #262c36; stroke: #6e7681; }
    .mod { fill: #161b22; stroke: #30363d; }
    text { fill: #e6edf3; }
    .shift, .modlabel { fill: #9198a1; }
    .extra { fill: #4493f8; }
    .us { fill: #6e7681; }
  }"""
    body = "\n".join(p for p in parts if p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {width + 2:.0f} {height + 4:.0f}" '
            f'width="{width + 2:.0f}" height="{height + 4:.0f}">\n'
            f"<!-- Generated by scripts/build.py. -->\n<style>{style}\n</style>\n{body}\n</svg>\n")


# ---------------------------------------------------------------- main

def outputs() -> dict[Path, bytes]:
    files: dict[Path, bytes] = {
        BUNDLE / "Contents/Info.plist": info_plist(),
        BUNDLE / "Contents/version.plist": plistlib.dumps(
            {"BuildVersion": VERSION, "ProjectName": "ModernMongolian", "SourceVersion": VERSION}),
    }
    for lang in ("en", "mn"):
        files[BUNDLE / f"Contents/Resources/{lang}.lproj/InfoPlist.strings"] = \
            infoplist_strings(lang).encode()
    for layout in LAYOUTS:
        files[BUNDLE / f"Contents/Resources/{layout['name']}.keylayout"] = \
            keylayout_xml(layout).encode()
        files[DOCS / f"{layout['short']}.svg"] = chart_svg(layout).encode()
    return files


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale = []
    for path, data in outputs().items():
        if path.exists() and path.read_bytes() == data:
            continue
        if check:
            stale.append(path.relative_to(ROOT))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        print("stale generated files (run scripts/build.py):", *stale, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
