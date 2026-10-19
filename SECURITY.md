# Security Policy

## Reporting a problem with this repository

Please report **privately**, using GitHub's *Security → Report a vulnerability* (private
vulnerability reporting) on this repository, if you find:

- personal data that should have been redacted (usernames, paths, emails, tokens, IDs);
- a live, clickable, or non-defanged attacker URL;
- attacker code or a payload that should not be here;
- a factual error that overstates or understates the incident.

Do **not** open a public issue for these.

## Scope

This repository contains documentation and static-analysis tools. It does not run a service.
Vulnerabilities in Brave, Chromium, StreamYard, Cloudflare, or other third parties should be
reported to those vendors directly.

## Handling of indicators

- All attacker URLs are defanged (`hxxps`, `[.]`). Pull requests that add clickable attacker links
  will be rejected.
- Raw attacker JavaScript, payloads, and browser databases are never accepted.
