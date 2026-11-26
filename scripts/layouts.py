"""Key assignments for the Modern Mongolian keyboards.

Every layout is keyed by the US-QWERTY label of the physical key, so the
tables read like the keyboard itself. Each entry is (base, shift).

Layers shared by both layouts (filled in by build.py):
  Option          -> US English (letters, punctuation); digits give ! @ # $ % ^ & * ( )
  Shift+Option    -> US English uppercase / shifted punctuation; digits give the
                     layout's SHIFT_OPTION_DIGITS extras
  Command         -> US QWERTY, so ⌘C / ⌘V / ⌘Z work without switching layouts
  Control         -> US control codes (Emacs-style text navigation keeps working)
"""

# Invisible Mongolian formatting characters.
FVS1 = "\u180B"  # free variation selector one
FVS2 = "\u180C"
FVS3 = "\u180D"
FVS4 = "\u180F"
MVS = "\u180E"  # vowel separator: final a/e detached from the stem
NNBSP = "\u202F"  # narrow no-break space: joins case suffixes
ZWJ = "\u200D"
ZWNJ = "\u200C"
NBSP = "\u00A0"

# Short names drawn on the layout charts for characters that have no glyph.
INVISIBLE_LABELS = {
    FVS1: "FVS1",
    FVS2: "FVS2",
    FVS3: "FVS3",
    FVS4: "FVS4",
    MVS: "MVS",
    NNBSP: "NNBSP",
    ZWJ: "ZWJ",
    ZWNJ: "ZWNJ",
    NBSP: "NBSP",
    " ": "",
}

CYRILLIC = {
    "name": "Mongolian Modern Cyrillic",
    "localized": {"en": "Mongolian – Modern Cyrillic", "mn": "Монгол – Кирилл"},
    "short": "cyrillic",
    "id": -21470,
    "language": "mn-Cyrl",
    "caps_uppercases": True,
    "keys": {
        # Number row: digits without Shift; Shift gives the standard symbols in
        # the exact positions of the national (MNS) layout.
        "`": ("=", "+"),
        "1": ("1", "№"),
        "2": ("2", "-"),
        "3": ("3", '"'),
        "4": ("4", "₮"),
        "5": ("5", ":"),
        "6": ("6", "."),
        "7": ("7", "_"),
        "8": ("8", ","),
        "9": ("9", "%"),
        "0": ("0", "?"),
        "-": ("е", "Е"),
        "=": ("щ", "Щ"),
        # Letters: identical to the national (MNS) layout.
        "q": ("ф", "Ф"),
        "w": ("ц", "Ц"),
        "e": ("у", "У"),
        "r": ("ж", "Ж"),
        "t": ("э", "Э"),
        "y": ("н", "Н"),
        "u": ("г", "Г"),
        "i": ("ш", "Ш"),
        "o": ("ү", "Ү"),
        "p": ("з", "З"),
        "[": ("к", "К"),
        "]": ("ъ", "Ъ"),
        "\\": (".", ","),  # one-key period and comma for prose
        "a": ("й", "Й"),
        "s": ("ы", "Ы"),
        "d": ("б", "Б"),
        "f": ("ө", "Ө"),
        "g": ("а", "А"),
        "h": ("х", "Х"),
        "j": ("р", "Р"),
        "k": ("о", "О"),
        "l": ("л", "Л"),
        ";": ("д", "Д"),
        "'": ("п", "П"),
        "z": ("я", "Я"),
        "x": ("ч", "Ч"),
        "c": ("ё", "Ё"),
        "v": ("с", "С"),
        "b": ("м", "М"),
        "n": ("и", "И"),
        "m": ("т", "Т"),
        ",": ("ь", "Ь"),
        ".": ("в", "В"),
        "/": ("ю", "Ю"),
        "§": ("[", "]"),  # ISO keyboards only
        "space": (" ", " "),
    },
    "shift_option_digits": {
        "1": "«",
        "2": "»",
        "3": "„",
        "4": "“",
        "5": "”",
        "6": "…",
        "7": "–",
        "8": "—",
        "9": "€",
        "0": "°",
    },
}

# Traditional script, aligned with the Cyrillic layout: every key types the
# script letter its Cyrillic letter is normally spelled with (з, ж -> ᠵ;
# ц, ч -> ᠴ; й, и -> ᠢ). Shift gives the foreign/Galik variant of that sound.
# Keys whose Cyrillic letter has no script counterpart (ы ё ь ъ ю щ) carry the
# invisible formatting characters and brackets.
SCRIPT = {
    "name": "Mongolian Traditional Script",
    "localized": {"en": "Mongolian – Traditional Script", "mn": "Монгол бичиг"},
    "short": "script",
    "id": -21471,
    "language": "mn-Mong",
    "caps_uppercases": False,
    "keys": {
        "`": ("᠁", "᠅"),
        "1": ("1", "᠀"),
        "2": ("2", "-"),
        "3": ("3", '"'),
        "4": ("4", "₮"),
        "5": ("5", "᠄"),
        "6": ("6", "᠃"),
        "7": ("7", "᠊"),
        "8": ("8", "᠂"),
        "9": ("9", "%"),
        "0": ("0", "?"),
        "-": ("ᠧ", "ᠧ"),  # е
        "=": ("《", "》"),  # щ
        "q": ("ᠹ", "ᠹ"),  # ф
        "w": ("ᠴ", "ᠼ"),  # ц
        "e": ("ᠤ", "ᠤ"),  # у
        "r": ("ᠵ", "ᡁ"),  # ж
        "t": ("ᠡ", MVS + "ᠡ"),  # э; Shift = detached final e
        "y": ("ᠨ", "ᠩ"),  # н; Shift = ng
        "u": ("ᠭ", "ᠭ"),  # г
        "i": ("ᠱ", "ᠱ"),  # ш
        "o": ("ᠦ", "ᠦ"),  # ү
        "p": ("ᠵ", "ᠽ"),  # з
        "[": ("ᠺ", "ᠻ"),  # к
        "]": (ZWJ, ZWNJ),  # ъ
        "\\": ("᠃", "᠂"),
        "a": ("ᠢ", "ᠢ"),  # й
        "s": (FVS1, FVS2),  # ы
        "d": ("ᠪ", "ᠪ"),  # б
        "f": ("ᠥ", "ᠥ"),  # ө
        "g": ("ᠠ", MVS + "ᠠ"),  # а; Shift = detached final a
        "h": ("ᠬ", "ᠾ"),  # х
        "j": ("ᠷ", "ᠿ"),  # р
        "k": ("ᠣ", "ᠣ"),  # о
        "l": ("ᠯ", "ᡀ"),  # л
        ";": ("ᠳ", "ᠳ"),  # д
        "'": ("ᠫ", "ᠫ"),  # п
        "z": ("ᠶ", "ᠶ"),  # я
        "x": ("ᠴ", "ᡂ"),  # ч
        "c": (FVS3, FVS4),  # ё
        "v": ("ᠰ", "ᠰ"),  # с
        "b": ("ᠮ", "ᠮ"),  # м
        "n": ("ᠢ", "ᠢ"),  # и
        "m": ("ᠲ", "ᠲ"),  # т
        ",": (NNBSP, MVS),  # ь
        ".": ("ᠸ", "ᠸ"),  # в
        "/": ("〈", "〉"),  # ю
        "§": ("[", "]"),
        "space": (" ", NNBSP),
    },
    "shift_option_digits": {
        "1": "᠑",
        "2": "᠒",
        "3": "᠓",
        "4": "᠔",
        "5": "᠕",
        "6": "᠖",
        "7": "᠗",
        "8": "᠘",
        "9": "᠙",
        "0": "᠐",
    },
}

LAYOUTS = [CYRILLIC, SCRIPT]
