# Responsible Disclosure

> **Status:** reports to the parties below are **not recorded** in the evidence. Update this table
> as reports are filed. Do not include ticket numbers or contact details that identify the reporter.

| Party | Why | Channel (find through the party's official website) | Status |
|---|---|---|---|
| StreamYard | Brand impersonation | Official security or abuse contact on `streamyard.com` | Not recorded |
| Cloudflare | Reverse proxy and CDN for the site | Cloudflare abuse reporting form (phishing category) | Not recorded |
| Registrar / DNS host of `host12us[.]com` | Hosts the impersonating subdomain | Registrar abuse contact from RDAP/WHOIS | Not recorded |
| Email provider of `beaconlayer[.]cc` | Sends the lure | Registrar or mail-host abuse contact | Not recorded |
| Google Safe Browsing | Browser blocklisting | Safe Browsing "Report phishing" page | Not recorded |
| urlscan.io | Verdict was "not malicious" at scan time | Add a verdict or comment on the existing scan | Not recorded |
| Anti-phishing clearinghouses (e.g. APWG) | Sharing with defenders | `reportphishing@` addresses published by the organisation | Not recorded |

## Guidance

- Report from a clean system, and send **indicators only**. Do not send your browser databases or
  personal email content.
- Forward the lure email **as an attachment with full headers** to providers that request it.
- Do not interact further with the sender, and do not probe the `/api/*` or `/download/*`
  endpoints.
- If the hosting party disputes the report, refer them to the hashes and reconstructed logic in
  this repository.
