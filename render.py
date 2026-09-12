#!/usr/bin/env python3
"""Render a MoErgo Glove80 keymap.json as text, one grid per layer.

Usage: python3 render.py [keymap.json] [-o layers.txt] [--readme README.md]
Writes layers.txt (grids plus a sorted binding -> key table, so moves show
up in a diff) and rewrites the marked layout section of README.md in place.
"""
import json
import sys

# The 34 keys in use: 3x5 per hand plus the lower two thumb keys per hand (T4, T5).
# ZMK key indices, left hand then right hand, outer -> inner for both.
HAND_ROWS = [
    ([23, 24, 25, 26, 27], [28, 29, 30, 31, 32]),
    ([35, 36, 37, 38, 39], [40, 41, 42, 43, 44]),
    ([47, 48, 49, 50, 51], [58, 59, 60, 61, 62]),
]
THUMBS = ([69, 70], [73, 74])

KEYCODES = {
    "EXCL": "!", "AT": "@", "HASH": "#", "DLLR": "$", "PRCNT": "%", "CARET": "^",
    "AMPS": "&", "STAR": "*", "ASTRK": "*", "LPAR": "(", "RPAR": ")", "MINUS": "-",
    "UNDER": "_", "EQUAL": "=", "PLUS": "+", "LBKT": "[", "RBKT": "]", "LBRC": "{",
    "RBRC": "}", "BSLH": "\\", "PIPE": "|", "SEMI": ";", "COLON": ":", "SQT": "'",
    "DQT": '"', "COMMA": ",", "DOT": ".", "FSLH": "/", "QMARK": "?", "GRAVE": "`",
    "TILDE": "~", "LT": "<", "GT": ">",
    "SPACE": "Spc", "RET": "Ent", "ENTER": "Ent", "ESC": "Esc", "BSPC": "Bspc",
    "DEL": "Del", "TAB": "Tab", "CAPS": "Caps", "INS": "Ins", "PSCRN": "PrtSc",
    "LEFT": "←", "DOWN": "↓", "UP": "↑", "RIGHT": "→",
    "HOME": "Home", "END": "End", "PG_UP": "PgUp", "PG_DN": "PgDn",
    "C_PREV": "Prev", "C_PP": "Play", "C_NEXT": "Next", "C_MUTE": "Mute",
    "C_VOL_UP": "Vol+", "C_VOL_DN": "Vol-", "C_BRI_UP": "Bri+", "C_BRI_DN": "Bri-",
    "LSHFT": "Shft", "RSHFT": "Shft", "LCTRL": "Ctrl", "RCTRL": "Ctrl",
    "LALT": "Alt", "RALT": "Alt", "LGUI": "Gui", "RGUI": "Gui",
}


def label(key, layer_names):
    """Short text for one binding."""
    if key is None:
        return ""
    v = key.get("value", "")
    params = [p.get("value") for p in key.get("params", [])]
    deco = (key.get("decoration") or {}).get("label")
    if deco:
        return deco
    if v == "&none":
        return ""
    if v == "&trans":
        return "▽"
    if v == "&kp":
        k = str(params[0])
        if k in KEYCODES:
            return KEYCODES[k]
        if len(k) == 2 and k[0] == "N" and k[1].isdigit():
            return k[1]
        return k
    if v == "&sk":
        k = str(params[0])
        return "(" + KEYCODES.get(k, k) + ")"
    if v.endswith("_ns"):
        k = v[1:-3].upper()
        return KEYCODES.get(k, k)
    if v in ("&mo", "&to", "&tog", "&sl"):
        n = params[0]
        name = layer_names[n] if isinstance(n, int) and n < len(layer_names) else str(n)
        return f"{v[1:]}:{name}"
    if v == "&caps_word":
        return "CapsW"
    if v == "&magic":
        return "Magic"
    if v == "&bootloader":
        return "BOOT"
    if v == "&reset":
        return "RESET"
    if v.startswith("&bt_"):
        return "BT" + v[4:]
    if v == "&bt":
        return str(params[0]).replace("BT_CLR_ALL", "BT CLR*").replace("BT_", "BT ")
    if v == "&rgb_ug":
        return str(params[0]).replace("RGB_", "")
    if v == "&out":
        return str(params[0]).replace("OUT_", "")
    if params:
        return f"{v[1:]} {' '.join(map(str, params))}"
    return v.lstrip("&")


def box_rows(labels, width):
    """Return top / middle / bottom border lines and a content line for one group of cells."""
    seg = "\u2500" * width
    top = "\u250c" + "\u252c".join([seg] * len(labels)) + "\u2510"
    mid = "\u251c" + "\u253c".join([seg] * len(labels)) + "\u2524"
    bot = "\u2514" + "\u2534".join([seg] * len(labels)) + "\u2518"
    body = "\u2502" + "\u2502".join(l[:width].center(width) for l in labels) + "\u2502"
    return top, mid, bot, body


def render_layer(name, idx, keys, layer_names, width=6, gap=6):
    lab = lambda i: label(keys[i], layer_names)
    out = [f"== {idx}: {name} =="]
    sep = " " * gap
    for r, (left, right) in enumerate(HAND_ROWS):
        lt, lm, lb, lbody = box_rows([lab(i) for i in left], width)
        rt, rm, rb, rbody = box_rows([lab(i) for i in right], width)
        out.append((lt if r == 0 else lm) + sep + (rt if r == 0 else rm))
        out.append(lbody + sep + rbody)
    out.append(lb + sep + rb)
    lt, _, lb, lbody = box_rows([lab(i) for i in THUMBS[0]], width)
    rt, _, rb, rbody = box_rows([lab(i) for i in THUMBS[1]], width)
    hand_w = 5 * (width + 1) + 1
    indent = " " * (hand_w - len(lt))
    for line_l, line_r in ((lt, rt), (lbody, rbody), (lb, rb)):
        out.append(indent + line_l + sep + line_r)
    return "\n".join(out)


SKIP = ("&none", "&trans", "&mo", "&magic")


def _key_names():
    """MoErgo editor names: LH/RH, C1 = inner column .. C6 = outer, R1 = top row .. R6 = bottom, T1-T6 thumbs."""
    names = {}
    # (first index, row, left columns outer->inner, right columns inner->outer)
    main = [(0, 1, [5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            (10, 2, [6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]),
            (22, 3, [6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]),
            (34, 4, [6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]),
            (46, 5, [6, 5, 4, 3, 2, 1], None),
            (64, 6, [6, 5, 4, 3, 2], None)]
    for start, row, left, right in main:
        for j, c in enumerate(left):
            names[start + j] = f"LH C{c}R{row}"
        if right:
            for j, c in enumerate(right):
                names[start + len(left) + j] = f"RH C{c}R{row}"
    for j, c in enumerate([1, 2, 3, 4, 5, 6]):
        names[58 + j] = f"RH C{c}R5"
    for j, c in enumerate([2, 3, 4, 5, 6]):
        names[75 + j] = f"RH C{c}R6"
    for i, t in zip((52, 53, 54, 69, 70, 71), (1, 2, 3, 4, 5, 6)):
        names[i] = f"LH T{t}"
    for i, t in zip((57, 56, 55, 74, 73, 72), (1, 2, 3, 4, 5, 6)):
        names[i] = f"RH T{t}"
    return names


KEY_NAMES = _key_names()


def bindings_table(d):
    """One line per binding: label, MoErgo key name. Sorted, duplicates collapsed."""
    names = d["layer_names"]
    rows = []
    for n, l in zip(names, d["layers"]):
        if n == "Magic":
            continue
        for i, k in enumerate(l):
            if k["value"] in SKIP:
                continue
            rows.append((label(k, names), KEY_NAMES[i]))
    rows = sorted(set(rows))
    return "\n".join(f"{lab:<8} {key}" for lab, key in rows) + "\n"


START, END = "<!-- layout:start -->", "<!-- layout:end -->"


def render_all(d):
    names = d["layer_names"]
    grids = "\n\n".join(render_layer(n, i, l, names) for i, (n, l) in enumerate(zip(names, d["layers"])))
    return grids + "\n\n== Bindings ==\n" + bindings_table(d)


def readme_section(d):
    names = d["layer_names"]
    grids = "\n\n".join(render_layer(n, i, l, names) for i, (n, l) in enumerate(zip(names, d["layers"])))
    return f"{START}\n```text\n{grids}\n```\n{END}"


def update_readme(path, d):
    text = open(path).read()
    a, b = text.find(START), text.find(END)
    if a < 0 or b < 0:
        raise SystemExit(f"{path}: missing {START} / {END} markers")
    text = text[:a] + readme_section(d) + text[b + len(END):]
    open(path, "w").write(text)


def main(argv):
    """Usage: render.py [keymap.json] [-o layers.txt] [--readme README.md]

    Writes the plain-text render (grids + bindings table) to layers.txt and
    rewrites the marked layout section of README.md in place."""
    path, out_path, readme = "keymap.json", "layers.txt", "README.md"
    args = iter(argv)
    for a in args:
        if a == "-o":
            out_path = next(args)
        elif a == "--readme":
            readme = next(args)
        else:
            path = a
    with open(path) as f:
        d = json.load(f)
    with open(out_path, "w") as f:
        f.write(render_all(d))
    update_readme(readme, d)


if __name__ == "__main__":
    main(sys.argv[1:])
