# Tools

Small Python 3 standard-library scripts used to produce the results in this repository.

**Safety properties (verified by review):**
- no JavaScript is executed: no `eval`, Node.js, browser, or `js2py`;
- no network access;
- the JavaScript analysers **refuse to run** unless the input's SHA-256 matches the archived
  sample;
- `ast.literal_eval` is used only on matched string literals;
- the SQLite tool opens databases with `mode=ro&immutable=1`.

Run them with `python3 -I` (isolated mode), from a directory that does **not** contain the
samples, so that no stray module next to the evidence can be imported.

| Script | Input | Output |
|---|---|---|
| `tracker_static_decode.py` | `tracker.js` (SHA-256 `9610644d…0846`) | `decoded_table.json`, `tracker_STATIC_ONLY.txt`, `report.txt` |
| `main_bundle_strings.py` | `index-DTuBtXUO.js` (SHA-256 `b59b2fac…1513`) | Rotation, string count, keyword context; optional substituted text |
| `chromium_download_record.py` | A **copy** of a Chromium/Brave `History` database | Download rows for one host, with tokens redacted by default |
| `check_publication.py` | This repository | Privacy, live-indicator, file-type, and Markdown-link findings |

## Obtaining the samples

The samples are **not** included in this repository. They are public response bodies in the
urlscan.io scan `01a1547c-f423-727d-a1dc-91732fef77cc` and can be retrieved by SHA-256 from
urlscan (account or API key may be required). This fetches from urlscan, **not** from the attacker.
urlscan serves them gzip-compressed:

```bash
mkdir -p ~/samples && cd ~/samples        # a dedicated, empty directory
# ...download the two bodies from urlscan by hash, then:
gunzip -c <tracker-body-file> > tracker.js
gunzip -c <main-body-file>    > index-DTuBtXUO.js
sha256sum -c /path/to/repo/indicators/hashes.sha256
```

## Expected results

```
$ python3 -I tools/tracker_static_decode.py ~/samples/tracker.js --out /tmp/tracker-out
String-table entries: 148
Rotation: 116
Aliases (14): [...]
Decoder calls replaced: 204
String joins folded: 89

$ python3 -I tools/main_bundle_strings.py ~/samples/index-DTuBtXUO.js
String-array entries: 3298
Rotation: 250
```

Treat the output files as **attacker-derived content**. Do not serve them from a web server, and
do not commit them.

## Not included

The original working scripts (earlier, Spanish-language iterations) were reviewed and replaced by
these consolidated versions. The earlier versions contained a hard-coded report text that went
beyond what the code itself established, and a less complete alias search (5 aliases / 35 folds
instead of 14 / 89).
