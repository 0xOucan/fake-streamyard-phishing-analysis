# Contributing

Corrections, extra indicators from **other** sightings of this campaign, and detection ideas are
welcome.

## Ground rules

1. **Evidence first.** Tag every new claim **Confirmed**, **Observed**, **Inferred**, or
   **Unknown**, and name its source. See
   [docs/evidence-and-limitations.md](docs/evidence-and-limitations.md#confidence-model).
2. **No live interaction.** Do not submit findings obtained by requesting `/api/*`, `/download/*`,
   or other attacker endpoints from a non-isolated system.
3. **Defang** every attacker URL, domain, and email address.
4. **No sensitive data.** No browser databases, cookies, session files, screenshots of private
   data, wallet addresses, tokens, or personal identifiers, including your own.
5. **No payloads.** Do not commit raw attacker JavaScript, binaries, or archives. Hashes and short
   excerpts are fine.
6. **Static tools only.** New tools must not execute attacker code and should be hash-gated.

## Before opening a pull request

```bash
# Privacy, live-indicator, file-type, and Markdown link checks.
# Keep your own deny-list (usernames, handles, real names) OUTSIDE the repository.
python3 -I tools/check_publication.py . --deny-file ~/private-terms.txt
```

Stage files explicitly (`git add path/to/file`). Never use `git add .` or `git add -A`.
