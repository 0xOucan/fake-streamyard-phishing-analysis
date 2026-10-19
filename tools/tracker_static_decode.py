#!/usr/bin/env python3
"""Static, offline string recovery for the archived fake-StreamYard tracker.js.

Never executes JavaScript and never makes network requests. Python standard library only.
`ast.literal_eval` is applied to string literals only.

Usage:
    python3 -I tracker_static_decode.py tracker.js --out out/
"""
import argparse
import ast
import base64
import hashlib
import json
import re
from pathlib import Path

EXPECTED_SHA256 = '9610644d8653ab2ca10cd45346b43c9825769517bca83cbd2118ae3fb0af0846'
CUSTOM_B64 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
STANDARD_B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
OFFSET = 0xb0
CHECKSUM = 0xde483
# Indices used by the rotation IIFE's parseInt() checksum, in source order.
CHECK_INDICES = [0xd5, 0x128, 0xc9, 0x142, 0xf6, 0x126, 0x137, 0xb0, 0xb5]
STRING_LITERAL = r'(?:"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'


def decode_entry(value):
    """Custom-alphabet Base64 -> UTF-8, as the tracker's decoder does."""
    try:
        b64 = value.translate(str.maketrans(CUSTOM_B64, STANDARD_B64))
        return base64.b64decode(b64 + '=' * (-len(b64) % 4)).decode('utf-8')
    except (ValueError, UnicodeError):
        return ''


def js_parseint(s):
    match = re.match(r'\s*([+-]?\d+)', s)
    return int(match.group(1)) if match else float('nan')


def solve_rotation(values):
    for rotation in range(len(values)):
        trial = values[rotation:] + values[:rotation]
        a, b, c, d, e, f, g, h, i = (js_parseint(decode_entry(trial[n - OFFSET])) for n in CHECK_INDICES)
        if a * b / 2 - c / 3 + d / 4 + e / 5 + f / 6 * (-g / 7) + h / 8 + i / 9 == CHECKSUM:
            return rotation, trial
    raise SystemExit('Rotation not solved: unexpected sample.')


def find_aliases(source):
    aliases = {'a0_0xf230'}
    while True:
        before = len(aliases)
        for left, right in re.findall(r'\b([A-Za-z_$][\w$]*)\s*=\s*([A-Za-z_$][\w$]*)\s*[,;]', source):
            if right in aliases:
                aliases.add(left)
        if len(aliases) == before:
            return aliases


def replace_calls(source, aliases, table):
    count = 0

    def sub(m):
        nonlocal count
        value = table.get(f'0x{int(m.group(1), 16):x}')
        if value is None:
            return m.group(0)
        count += 1
        return json.dumps(value, ensure_ascii=False)

    for alias in sorted(aliases, key=len, reverse=True):
        source = re.sub(r'\b' + re.escape(alias) + r'\(\s*(0x[0-9a-fA-F]+)\s*\)', sub, source)
    return source, count


def fold_literals(source):
    pattern = re.compile('(' + STRING_LITERAL + r')\s*\+\s*(' + STRING_LITERAL + ')')
    folds = 0
    while True:
        changed = 0

        def combine(m):
            nonlocal changed, folds
            try:
                left, right = ast.literal_eval(m.group(1)), ast.literal_eval(m.group(2))
            except (SyntaxError, ValueError):
                return m.group(0)
            if not isinstance(left, str) or not isinstance(right, str):
                return m.group(0)
            changed += 1
            folds += 1
            return json.dumps(left + right, ensure_ascii=False)

        source = pattern.sub(combine, source)
        if not changed:
            return source, folds


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('js', type=Path, help='archived tracker.js (decompressed)')
    parser.add_argument('--out', type=Path, default=Path('tracker-report'))
    args = parser.parse_args()

    raw = args.js.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f'SHA-256 mismatch ({digest}); refusing to analyse.')
    source = raw.decode('utf-8')

    body = source[source.index('function a0_0x4fd7()'):]
    array_src = body[body.index('var _0xac28af='):body.index(';a0_0x4fd7=function')]
    rotation, rotated = solve_rotation(re.findall(r"'([^']*)'", array_src))
    table = {f'0x{n + OFFSET:x}': decode_entry(v) for n, v in enumerate(rotated)}

    aliases = find_aliases(source)
    decoded, replaced = replace_calls(source, aliases, table)
    decoded, folds = fold_literals(decoded)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'decoded_table.json').write_text(json.dumps(table, ensure_ascii=False, indent=2))
    (args.out / 'tracker_STATIC_ONLY.txt').write_text(decoded)

    lines = [
        f'SHA-256: {digest}',
        f'String-table entries: {len(table)}',
        f'Rotation: {rotation}',
        f'Aliases ({len(aliases)}): {sorted(aliases)}',
        f'Decoder calls replaced: {replaced}',
        f'String joins folded: {folds}',
    ]
    for key in ['/api/', 'redirect', 'download', 'iframe', 'addEventListener', 'preventDefault',
                'stopPropagation', 'location', 'Image', 'fetch']:
        hits = [m.start() for m in re.finditer(re.escape(key), decoded)]
        lines.append(f'{key}: {len(hits)} hit(s)')
    report = '\n'.join(lines) + '\n'
    (args.out / 'report.txt').write_text(report)
    print(report, end='')


if __name__ == '__main__':
    main()
