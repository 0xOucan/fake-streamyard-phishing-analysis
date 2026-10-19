#!/usr/bin/env python3
"""Static, offline string recovery for the archived fake-StreamYard main bundle.

Solves the string-array rotation arithmetically, substitutes decoder calls with their literals,
and prints the context around selected keywords. Never executes JavaScript and never makes
network requests.

Usage:
    python3 -I main_bundle_strings.py index-DTuBtXUO.js [--keyword TEXT ...] [--out decoded.txt]
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_SHA256 = 'b59b2faca845ae3a3035cf4f80733b9edaefe3f592c99864edba417b994e1513'
OFFSET = 0x1c8
CHECKSUM = 0xee547
DEFAULT_KEYWORDS = ['You are invited', 'use our application', 'join-button', 'createRoot']


def js_parseint(s):
    match = re.match(r'\s*([+-]?\d+)', s)
    return int(match.group(1)) if match else float('nan')


def solve_rotation(values):
    for rotation in range(len(values)):
        t = values[rotation:] + values[:rotation]
        v = lambda n: js_parseint(t[n - OFFSET])
        # Mirrors the checksum expression in the bundle's rotation IIFE.
        x = (v(0x60d) / 1 + -v(0xe23) / 2 * (v(0x763) / 3) + v(0x490) / 4 + v(0xae9) / 5
             + -v(0x28c) / 6 + -v(0xd69) / 7 + v(0x572) / 8 * (v(0xd80) / 9))
        if x == CHECKSUM:
            return rotation, t
    raise SystemExit('Rotation not solved: unexpected sample.')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('js', type=Path, help='archived index-DTuBtXUO.js (decompressed)')
    parser.add_argument('--keyword', action='append', help='keyword to show in context')
    parser.add_argument('--out', type=Path, help='write the substituted text here')
    args = parser.parse_args()

    raw = args.js.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f'SHA-256 mismatch ({digest}); refusing to analyse.')
    source = raw.decode('utf-8')

    start = source.index('function a0_0x523a(){var _0xeeedc1=[')
    values = re.findall(r"'((?:\\.|[^'\\])*)'", source[start:source.index('];', start)])
    rotation, table = solve_rotation(values)
    lookup = {OFFSET + i: s for i, s in enumerate(table)}

    def sub(m):
        n = int(m.group(1), 16)
        if n not in lookup:
            return m.group(0)
        # Entries are JS single-quoted literal bodies; only \xNN escapes occur in practice.
        text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda e: chr(int(e.group(1), 16)), lookup[n])
        return json.dumps(text, ensure_ascii=False)

    decoded = re.sub(r'\b(?:_0x[0-9a-f]+|a0_0x[0-9a-f]+)\((0x[0-9a-f]+)\)', sub, source)
    print(f'SHA-256: {digest}\nString-array entries: {len(values)}\nRotation: {rotation}')
    if args.out:
        args.out.write_text(decoded)
    for key in args.keyword or DEFAULT_KEYWORDS:
        for m in list(re.finditer(re.escape(key), decoded))[-1:]:
            print(f'\n== {key} @ {m.start()}\n{decoded[max(0, m.start() - 300):m.end() + 300]}')


if __name__ == '__main__':
    main()
