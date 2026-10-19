# Publication Checklist

Status of the privacy and safety review done **before** the first publication. Items marked ☐
need a human decision.

## Content minimisation

- [x] No local usernames, home paths, or machine names (automated + manual grep)
- [x] No investigator email address, real name, location, or project names; the public handle is used only for the author credit
- [x] No browser databases, WAL files, sessions, cookies, Local Storage, IndexedDB, or `Preferences`
- [x] No full browsing history; only the incident visits are summarised, without row IDs
- [x] Email-redirector tracking parameters removed; the redirector provider is not named
- [x] Meeting ID and download token redacted (`<redacted-meeting-id>`, `<redacted-token>`)
- [x] Download GUID and history row IDs other than the download ID omitted
- [x] No wallet addresses, seeds, keys, signatures, tokens, or API keys
- [x] No screenshots
- [x] No raw attacker JavaScript, archives, payloads, or binaries; hashes and short decoded excerpts only
- [x] Attacker infrastructure defanged everywhere, and no clickable attacker links
- [x] Researcher credited by public handle (0xOucan) at their request. Personal email, location, and projects still omitted.
- [x] The persona name is kept in `indicators/iocs.md` with an explicit "impersonator or fictitious; unknown" caveat.

## Accuracy

- [x] Every significant claim tagged Confirmed / Observed / Inferred / Unknown
- [x] JS decoding counts (14 / 204 / 89) reproduced byte-identically
- [x] Download record fields checked against the `History` copy
- [x] DIPS counts checked on a scratch copy; originals unchanged
- [x] "Domain registered 2026-10-13" corrected (TLS issue date; the apex is ~10.6 years old per urlscan)
- [x] No claims of infection, sandbox escape, wallet compromise, exfiltration, or "total safety"

## Automated checks

| Check | Tool | Result |
|---|---|---|
| Privacy / live indicators / file types / Markdown links and anchors | `tools/check_publication.py` with a private deny-list kept outside the repo | 0 findings |
| Independent grep for personal terms, paths, tracking params, EVM addresses | `grep -rnIiE` | Matches only inside the checker's own regex patterns |
| Mermaid syntax | Structural lint (header, bracket balance, quoting) | Passed. **Not** rendered with the official Mermaid parser. Preview on GitHub before announcing. |
| Hash file format | `sha256sum -c` against the local samples | 2/2 OK |
| Tools run against the evidence | All three analysis tools | Expected output; hash gate refuses unknown input |

## Git hygiene (when publishing)

- [x] Git initialised **inside `github-public-report/` only**, never in the evidence folder
- [x] Staged with an explicit allowlist (no `git add .` or `git add -A`)
- [x] `git diff --cached` reviewed before committing
- [x] Commit authored with the GitHub noreply address, so no personal email appears in the history
