#!/usr/bin/env python3
"""Print Chromium/Brave download records for one host from a *copy* of the History database.

Opens the database with mode=ro&immutable=1 so SQLite never writes to it. Only rows whose
tab URL, referrer, or URL chain contains --host are printed. By default, path segments after
/download/ and query strings are redacted.

Usage:
    cp ~/.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser/Default/History /tmp/History.copy
    python3 -I chromium_download_record.py /tmp/History.copy --host example.invalid
"""
import argparse
import datetime
import re
import sqlite3
from pathlib import Path

STATES = {0: 'IN_PROGRESS', 1: 'COMPLETE', 2: 'CANCELLED', 4: 'INTERRUPTED'}
# Subset of Chromium's download_interrupt_reason_values.h
INTERRUPT_REASONS = {0: 'NONE', 40: 'USER_CANCELED', 41: 'USER_SHUTDOWN', 50: 'CRASH'}
FIELDS = ['id', 'start_time', 'end_time', 'state', 'interrupt_reason', 'danger_type', 'received_bytes',
          'total_bytes', 'opened', 'target_path', 'mime_type', 'tab_url', 'referrer']


def webkit_to_utc(us):
    if not us:
        return None
    return (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=us)).isoformat() + 'Z'


def redact(url, enabled):
    if not enabled or not url:
        return url
    url = re.sub(r'(/download/)[^/?#]+', r'\1<redacted>', url)
    return re.sub(r'\?.*$', '?<redacted>', url)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('history', type=Path, help='path to a COPY of the History database')
    parser.add_argument('--host', required=True, help='substring to match, e.g. a hostname')
    parser.add_argument('--no-redact', action='store_true', help='print full URLs')
    args = parser.parse_args()

    db = sqlite3.connect(f'file:{args.history.resolve()}?mode=ro&immutable=1', uri=True)
    like = f'%{args.host}%'
    ids = [r[0] for r in db.execute(
        'SELECT DISTINCT d.id FROM downloads d LEFT JOIN downloads_url_chains c ON c.id = d.id '
        'WHERE d.tab_url LIKE ? OR d.referrer LIKE ? OR c.url LIKE ?', (like, like, like))]
    for download_id in ids:
        row = dict(zip(FIELDS, db.execute(f'SELECT {", ".join(FIELDS)} FROM downloads WHERE id = ?',
                                          (download_id,)).fetchone()))
        row['start_time'], row['end_time'] = webkit_to_utc(row['start_time']), webkit_to_utc(row['end_time'])
        row['state'] = f"{row['state']} ({STATES.get(row['state'], '?')})"
        row['interrupt_reason'] = f"{row['interrupt_reason']} ({INTERRUPT_REASONS.get(row['interrupt_reason'], 'see Chromium source')})"
        for key in ('tab_url', 'referrer'):
            row[key] = redact(row[key], not args.no_redact)
        print('---')
        for key, value in row.items():
            print(f'{key:17} {value}')
        for index, url in db.execute('SELECT chain_index, url FROM downloads_url_chains WHERE id = ? '
                                     'ORDER BY chain_index', (download_id,)):
            print(f'chain[{index}]         {redact(url, not args.no_redact)}')
    if not ids:
        print('No matching download records.')


if __name__ == '__main__':
    main()
