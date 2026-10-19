#!/usr/bin/env python3
"""Pre-publication checks for this repository: privacy leaks, live indicators, links, file types.

Usage:
    python3 -I tools/check_publication.py . [--deny-file ~/private-terms.txt]

--deny-file lists private terms (usernames, handles, real names, emails), one per line. Keep that
file OUTSIDE the repository. Exit status is 1 if any finding is reported.
"""
import argparse
import re
import sys
from pathlib import Path

ALLOWED_SUFFIXES = {'.md', '.mmd', '.py', '.sha256', ''}
ALLOWED_NAMES = {'LICENSE', '.gitignore'}
# Hashes deliberately published in this repository.
KNOWN_HEX = re.compile(r'\b[0-9a-f]{64}\b')
CHECKS = {
    'live attacker domain': re.compile(r'host12us\.com|beaconlayer\.cc', re.I),
    'clickable http(s) URL to attacker': re.compile(r'https?://[^\s)]*(host12us|beaconlayer)', re.I),
    'home directory path': re.compile(r'/home/(?!<redacted-user>)[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+'),
    'email address': re.compile(r'\b[A-Za-z0-9._%+-]+@(?!beaconlayer\[\.\])[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'IPv4 address (not defanged)': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    'EVM address': re.compile(r'\b0x[0-9a-fA-F]{40}\b'),
    'Bitcoin bech32 address': re.compile(r'\bbc1[02-9ac-hj-np-z]{25,87}\b'),
    'private key block': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    'API-key-like secret': re.compile(r'\b(?:AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]+)\b'),
    'webmail redirector / tracking token': re.compile(r'usg=AOv|google\.com/url\?q='),
}


def check_links(path, text):
    for target in re.findall(r'\]\(([^)\s]+)\)', text):
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue
        file_part, _, anchor = target.partition('#')
        dest = (path.parent / file_part).resolve() if file_part else path
        if not dest.exists():
            yield f'broken link -> {target}'
        elif anchor and dest.suffix == '.md':
            slugs = {re.sub(r'[^\w\- ]', '', h.strip().lower()).replace(' ', '-')
                     for h in re.findall(r'^#+\s+(.*)$', dest.read_text(), re.M)}
            if anchor not in slugs:
                yield f'missing anchor -> {target}'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('root', type=Path)
    parser.add_argument('--deny-file', type=Path)
    args = parser.parse_args()
    deny = []
    if args.deny_file:
        deny = [t.strip() for t in args.deny_file.read_text().splitlines() if t.strip()]
    findings = 0
    for path in sorted(p for p in args.root.rglob('*') if p.is_file() and '.git' not in p.parts):
        rel = path.relative_to(args.root)
        if path.suffix not in ALLOWED_SUFFIXES and path.name not in ALLOWED_NAMES:
            print(f'{rel}: unexpected file type'); findings += 1
            continue
        text = path.read_text(errors='replace')
        for n, line in enumerate(text.splitlines(), 1):
            scrubbed = KNOWN_HEX.sub('', line)
            for name, pattern in CHECKS.items():
                if pattern.search(scrubbed) and not (name == 'IPv4 address (not defanged)' and '[.]' in line):
                    if path.name == 'check_publication.py':
                        continue
                    print(f'{rel}:{n}: {name}: {line.strip()[:120]}'); findings += 1
            for term in deny:
                if term.lower() in line.lower():
                    print(f'{rel}:{n}: deny-listed term'); findings += 1
        if path.suffix == '.md':
            for problem in check_links(path, text):
                print(f'{rel}: {problem}'); findings += 1
    print(f'{findings} finding(s)')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
