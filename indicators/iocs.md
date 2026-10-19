# Indicators of Compromise (IoCs)

> ⚠️ **Untrusted attacker infrastructure.** Every value is defanged. Do not visit, resolve, or
> "check" these indicators from a production machine. Status as of 2026-10-19.

## Network

| Type | Indicator | Notes |
|---|---|---|
| Hostname | `streamyard.host12us[.]com` | Impersonating host |
| Apex domain | `host12us[.]com` | The apex owner's relationship to the operator is **unknown**. urlscan reports an apex age of ~3,879 days. Block the subdomain first. |
| URL pattern | `hxxps://streamyard[.]host12us[.]com/meeting/<6 alnum>` | Lure page; the code is validated by `^/meeting/[A-Za-z0-9]+/?$` |
| URL path | `/api/hit?code=…&event=…&button=…&t=…` | Click telemetry |
| URL path | `/api/join?code=…` | Returns JSON `{action, url}` |
| URL pattern | `hxxps://streamyard[.]host12us[.]com/download/<43-char token>` | Download endpoint seen in the browser record |
| URL path | `/denied.html` | Shown when the path has no valid meeting code |
| URL path | `/assets/tracker.js?v=8`, `/assets/index-DTuBtXUO.js` | Scripts |
| IPv4 | `104.21.72[.]142` | Cloudflare (AS13335). **Shared CDN address: do not block on its own.** |
| TLS | Certificate for `host12us[.]com`, issuer `YE1`, valid from 2026-10-13 07:21:04 UTC | Per urlscan |

## Email

| Type | Indicator | Notes |
|---|---|---|
| Sender address | `info@beaconlayer[.]cc` | Claimed to be a crypto-security podcast ("BeaconLayer") |
| Sender domain | `beaconlayer[.]cc` | Headers were not available, so the domain is not authenticated |
| Display name | "Kenzi Morikawa" | Persona used by the sender. **We do not know at this point whether this is an impersonator misusing a real person's name or an entirely fictitious persona.** It does not identify the person behind the campaign, and anyone with this name should not be presumed to be involved. |
| Subject theme | Podcast episode about hardware wallets; meeting set for "10:00 AM ET" on "StreamYard" | |
| Behaviour | Repeated requests for a high-resolution portrait; join link sent ~7 min before start; "coming?" follow-up; meeting "cancelled" when the target asked to use a different platform | |

## Host / file

| Type | Value | Notes |
|---|---|---|
| Download size (announced) | 857 bytes | `application/octet-stream`. The content was **not obtained**. |
| Download hash | — | Unknown (0 bytes received) |

## Resource hashes

These two hashes were verified locally (also in [`hashes.sha256`](hashes.sha256)):

| SHA-256 | Resource |
|---|---|
| `b59b2faca845ae3a3035cf4f80733b9edaefe3f592c99864edba417b994e1513` | `/assets/index-DTuBtXUO.js` |
| `9610644d8653ab2ca10cd45346b43c9825769517bca83cbd2118ae3fb0af0846` | `/assets/tracker.js?v=8` |

These hashes are **reported by urlscan only**. The bodies were not retrieved or verified locally:

| SHA-256 | Resource |
|---|---|
| `0f4fd4d9f426a42e1ea30e68a40d1f92de7049730723c137f968b39f2208a436` | `/meeting/<id>` HTML (1,094 B) |
| `f3c7b6d207bff43a0c37f398cacf5c93b57e6a7c49c83f9c52d5ff3b7aa7fdee` | `/assets/index-CG25rUGw.css` |
| `a830b908971314d70c80d11887fd5163c326c4882cd42872c90f2b48dec1b429` | `/assets/logo.svg` |
| `0ea0904c31f3568646ed59c176f90c30e017b67dc6672d77bd581a333966faa1` | `/assets/camera.svg` |
| `c13359aaf6945b7c203915e5e38b0d213acbb053c68cbf735b4e99de63a9c13b` | `/assets/arrow.svg` |
| `27c7c6820cd15bb81940efc7c14eff9311585df09b49d50c19b589b8994e6eb8` | `/assets/averta-semibold.ttf` |
| `7a4c1e25032fc21ba4382c5fccd28781f35da8172d340834111b6457f7a0a413` | `/assets/averta-regular.ttf` |

The page also loaded Cloudflare's standard Web Analytics beacon. That is generic CDN tooling and
is not an indicator.

## Detection ideas

- Proxy/DNS: any request to `*.host12us[.]com/api/join` or `/download/` after a `/meeting/` page.
- Browser history hunting: `downloads` rows where `tab_url LIKE '%/meeting/%'` and the URL chain
  contains `/download/` on the same host.
- Content hunting (static file scanning, not live pages): the strings `"/api/join?code="` and
  `"Download is unavailable"` appear only **after** deobfuscation. On the raw tracker, use the
  SHA-256 hashes in [`hashes.sha256`](hashes.sha256).
