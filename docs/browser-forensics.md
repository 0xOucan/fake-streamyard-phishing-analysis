# Browser Forensics (Brave on Linux, Flatpak)

## Handling

- Brave's profile files were **copied** before analysis. The copies were hashed, and all queries
  ran against **second-level scratch copies**, never the first copy.
- `History` was opened with `file:...?mode=ro&immutable=1` so SQLite could not write to it.
- **Caution with WAL databases:** opening a copy of `DIPS` together with its `DIPS-wal` in normal
  mode **checkpoints and removes the WAL**, which changes the files. This happened on a scratch copy
  during this analysis, and that copy was thrown away. The preserved WAL was examined only with
  read-only byte-level tools. Always work on throw-away copies.
- Only incident-related rows were extracted. No other browsing history is published.

| File (copy) | SHA-256 |
|---|---|
| `History` | `9a7024a933f376cc1562095991b5a507cbbf69820c1a53222db33ac10520d2fc` |
| `DIPS` | `c2ae36a474c6d4b0ddf83f302fc99de94c35349f77b5a203a82b8be9b762308d` |
| `DIPS-wal` | `38d02df4dfcec71c398a88a650f7a2f86ab262068cb596b7737cf7fe57d759ba` |

These hashes identify the researcher's private copies. The files themselves are **not** published.

## `History`: the download record

| Column | Value | Meaning |
|---|---|---|
| `id` | 1115 | Row ID |
| `start_time` | 2026-10-19 14:01:07.573 UTC (09:01:07 local) | Download initiated |
| `end_time` | *(none)* | Never completed |
| `state` | **2** | `CANCELLED` (history encoding: 0 in progress, 1 complete, 2 cancelled, 4 interrupted) |
| `interrupt_reason` | **40** | Chromium `DOWNLOAD_INTERRUPT_REASON_USER_CANCELED` |
| `danger_type` | 0 | `NOT_DANGEROUS`: no Safe Browsing or file-type danger flag was set. This is **not** a verdict that the file was safe. |
| `received_bytes` | **0** | No content stored |
| `total_bytes` | 857 | Size the server announced (normally `Content-Length`) |
| `opened` | **0** | Never opened from the browser |
| `target_path`, `current_path` | *(empty)* | No save location was committed; cancelled at the save prompt |
| `hash` | *(empty)* | No content hash, consistent with 0 bytes |
| `mime_type` / `original_mime_type` | `application/octet-stream` | Generic binary type |
| `tab_url`, `referrer` | meeting page | Started from the fake meeting tab |
| `downloads_url_chains[0]` | `hxxps://streamyard[.]host12us[.]com/download/<redacted-token>` | Single URL, no redirect chain |

The enum meanings come from Chromium's `download_interrupt_reason_values.h` (`USER_CANCELED = 40`)
and the history `DownloadState` storage values. Reviewers should check them against the source of
the exact Brave/Chromium version they use.

The download token (43 URL-safe characters, which looks like a per-request secret) is redacted. It
could identify the target to the operator.

## `History`: visits

Three visit chains reached the meeting URL. Each came through an email link-redirector
(`PAGE_TRANSITION_LINK`, with `CHAIN_START` on the redirector and
`SERVER_REDIRECT | CHAIN_END` on the destination):

| Local time | Duration | Notes |
|---|---|---|
| 09:00:09 | 89.2 s | Download initiated during this visit (09:01:07) |
| 09:01:55 | 16.6 s | Same email link |
| 09:22:19 | 27.9 s | Newer email link; after the incident |

No other URL on `host12us[.]com` (for example `/denied.html` or a redirect target) is present in
the copied history. That **does not** rule out requests that were not recorded as visits, such as
`fetch()` calls, which Chromium history does not record.

## DIPS (Bounce Tracking Mitigations database)

The researcher cleared browsing history and cache **before** copying `DIPS` (Reported).

| Check | Result |
|---|---|
| `bounces` rows matching `host12us` | **0** (of 163 rows, after WAL replay on a scratch copy) |
| `popups` rows matching `host12us` | **0** (table empty) |
| Main `DIPS` file, byte search | 0 occurrences |
| `DIPS-wal`, byte search | **150** occurrences of `host12us[.]com` in 150 of 262 WAL frames (4096-byte pages 7 and 11) |

**Interpretation**
- DIPS records **sites** (registrable domains) and interaction or bounce timestamps. It does not
  record URLs, paths, request bodies, or responses. Only the bare string `host12us[.]com` appears.
- The 150 WAL frames are successive **historical versions of two B-tree pages**. They show the
  site was in the DIPS state at some point and was later removed (consistent with clearing the
  history). (Inferred)
- 150 occurrences **≠ 150 network requests**. The count reflects how often SQLite rewrote those
  pages.
- The DIPS WAL **does not** contain the `/api/join` HTTP response, and this report does not claim
  it does.

## Site permissions

The researcher reviewed Brave's site permissions for the domain (Reported). The per-permission
results were not preserved as an artifact, so this report makes no claim about them. `Preferences`
was not exported, to protect privacy.

## Flatpak context

Brave ran as a Flatpak. The browser processes were confined by the Flatpak sandbox, and in a
typical configuration the downloads directory is shared with the host. A file saved there and then
**executed by the user** runs on the host outside the sandbox. Flatpak lowers the impact of a
browser compromise, but it does not stop a user from running a malicious download. (Platform
behaviour)
