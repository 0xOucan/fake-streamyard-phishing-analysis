# Technical Analysis

This document answers the core questions about the incident in order. Each claim carries a
confidence tag (see [evidence-and-limitations.md](evidence-and-limitations.md#confidence-model)).

## 1. Why the site looked like a legitimate meeting invitation

- **Pretext before the link (Observed).** The link arrived at the end of a multi-hour email
  exchange about a podcast appearance. The outline quoted the target's own public posts, projects,
  and opinions in detail, and the sender asked for a portrait for "cover art". When the meeting
  link arrived, the target had already invested in the conversation.
- **Time pressure (Observed).** The join link was sent about 7 minutes before the stated start.
  When the target had not joined two minutes after the start, the sender wrote "coming? Waiting
  for you".
- **Brand cues (Confirmed).** The HTML title was `StreamYard Webinar`, the hostname begins
  `streamyard.`, and the page served a logo, a camera icon, and Averta font files. The UI was a
  plain "You are invited to webinar" waiting room with a **Join** button.
- **A plausible ask (Confirmed).** The page text says *"For enhanced security and access to all
  services, use our application."* Asking guests to install a desktop app is normal for some
  meeting platforms, so the request does not seem out of place.

## 2. Legitimate StreamYard versus the impersonating host

| | Legitimate | Observed |
|---|---|---|
| Registrable domain | `streamyard.com` | `host12us[.]com` |
| Hostname | `streamyard.com` and its subdomains | `streamyard.host12us[.]com` |
| Meeting path | StreamYard's own URL scheme | `/meeting/<6 alphanumerics>` |

The browser treats the **registrable domain** (`host12us[.]com`) as the site. The `streamyard.`
label is only a subdomain chosen by whoever controls `host12us[.]com`, so it proves nothing about
the brand. (Confirmed)

**Domain age (correction).** An earlier note said the domain was "registered on 2026-10-13".
The available urlscan data does **not** support that:
- the **TLS certificate** for `host12us[.]com` became valid on 2026-10-13 07:21 UTC (`tlsAgeDays: 6`);
- urlscan reports the **apex** domain's age as **3,879 days** (about 10.6 years).

The date was probably a recent certificate or subdomain setup, not a new registration. How the
apex owner relates to the operator (for example an attacker-owned domain, a compromised domain,
or a hosting platform) is **Unknown**. WHOIS was not queried.

The site sat behind Cloudflare (AS13335). Its IPs are shared CDN addresses and are poor
indicators on their own.

## 3. How the meeting identifier is parsed

`tracker.js` runs `location.pathname.match(/^\/meeting\/([A-Za-z0-9]+)\/?$/)` and keeps the first
capture group as `code`. If there is no match, it calls `location.replace("/denied.html")`. The
code is sent to both `/api/hit` and `/api/join`, which suggests per-target or per-campaign tracking.
(Code: Confirmed. Purpose: Inferred.)

## 4. How the obfuscation hid the important strings

Strings such as `/api/join?code=`, `download`, `redirect`, and `iframe` never appear as plain text
in `tracker.js`. They are split into fragments (`"/api/"`, `"join?"`, `"code="`) stored as
custom-alphabet Base64 in a rotated array and read through 14 aliased decoder functions. A simple
`grep` for `/api/` or `download` on the original file returns nothing. Details:
[javascript-deobfuscation.md](javascript-deobfuscation.md). (Confirmed)

## 5. How static decoding recovered the API paths

1. Extract the string array. Try each rotation and evaluate the checksum arithmetic **in Python**,
   with a JavaScript-compatible `parseInt` emulation, until it equals `0xde483` (rotation 116).
2. Decode each entry: translate the custom alphabet to standard Base64, then decode as UTF-8.
3. Find decoder aliases iteratively (`x = a0_0xf230`, `y = x`, ...): 14 names.
4. Replace every `alias(0xNN)` with its literal: 204 replacements.
5. Fold `"lit" + "lit"` repeatedly with `ast.literal_eval`: 89 folds.

The result contains `"/api/hit?code="`, `"&event="`, `"&button="`, `"&t="`, `"/api/join?code="`,
`"redirect"`, `"download"`, `"iframe"`, `"/denied.html"`, and
`"Download is unavailable"`. (Reproduced byte-for-byte)

## 6. How click interception works

```js
document.addEventListener("click", handler, /* useCapture */ true);
```

The handler runs during the capture phase at `document`, before any element-level handler. For
join-like targets it calls `preventDefault()` and `stopPropagation()`. That cancels default
navigation and keeps the event away from the page's React handlers, so the tracker fully controls
what happens next. (Confirmed)

## 7. How event telemetry is built

```
/api/hit?code=<meeting code>&event=click&button=join&t=<Date.now()>
```

The URL is sent **twice**: once by `new Image().src = url` and once by
`fetch(url, {method:"GET", keepalive:true, cache:"no-store"})`. Using two channels with `keepalive`
makes delivery likely even if the page is about to navigate away. Errors are ignored.
(Confirmed) The operator would see which code clicked Join, and when. (Inferred)

## 8. How the frontend requests join instructions

```js
fetch("/api/join?code=" + encodeURIComponent(code), { cache: "no-store" })
  .then(r => { if (!r.ok) throw new Error("Download is unavailable"); return r.json(); })
```

`cache: "no-store"` makes the server decide fresh on every click. The server could therefore vary
its answer by code, time, IP, User-Agent (sent automatically with the request), or campaign state.
The client code does no platform detection itself. (Code: Confirmed. Server-side logic: Unknown.)

## 9. How `redirect` and `download` are processed

| JSON response | Client behaviour |
|---|---|
| `{ "action": "redirect", "url": U }` | `window.location.assign(U)`: full navigation to U |
| `{ "action": "download", "url": U }` | Creates a hidden iframe with `src = U` |
| anything else, or a non-2xx response | Throws `"Download is unavailable"`, which is caught silently, and resets `busy` |

(Confirmed) Which branch ran during the incident is not directly recorded. The Brave download
record (section 12) fits the `download` branch. (Inferred)

## 10. How a hidden iframe can start a download

An iframe is a full browsing context. When its `src` returns a response the browser will not
render, such as `Content-Type: application/octet-stream` or a `Content-Disposition: attachment`
header, Chromium-based browsers turn the navigation into a **download**. The iframe is styled
`position:absolute;width:0;height:0;border:0;visibility:hidden`, so the user sees only the
browser's download UI, which looks as if the "Join" button produced it. Here the download URL was
**same-origin** (`/download/<token>`) and followed a real user click, so the browser's stricter
rules for sandboxed or cross-origin frame downloads did not apply. (Mechanism: Confirmed from code
and the browser record. Exact response headers: Unknown.)

## 11. Why a download attempt is not malware execution

On Linux, getting from "browser received a file" to "attacker code runs" normally takes **further
steps**:

1. the file must be **saved** (here it was not: 0 bytes received, empty target path);
2. it must be **opened or executed**, for example by marking it executable, running an AppImage,
   installing a `.deb`, opening a `.desktop` file, or running a script (here `opened=0`);
3. for a sandboxed Flatpak browser, the file must be run **outside** the browser sandbox, usually
   by the user from a file manager or terminal.

The alternative is a browser or OS **vulnerability** that executes content without these steps.
No evidence of that exists here, and none is claimed. (Inferred from platform behaviour plus
Confirmed record values)

The server announced **857 bytes**. That is far too small for a native meeting application. It is
consistent with a script, a `.desktop` launcher, a small archive, or a first-stage downloader, but
the content is **Unknown** and should not be guessed.

## 12. What the Brave SQLite record proves, and what it does not

**Proves (Confirmed):**
- A download from `streamyard.host12us[.]com/download/<token>` was initiated in the meeting tab
  (`tab_url` and `referrer` = the meeting page) at 09:01:07 local.
- The server's announced size was 857 bytes, and the MIME type was `application/octet-stream`.
- The download ended **cancelled**: `state=2`, Chromium `interrupt_reason=40`
  (`USER_CANCELED`), `received_bytes=0`, `opened=0`, empty `target_path`/`current_path`, no
  `end_time`, and no content hash.
- It is the **only** download record associated with this host.

**Does not prove:**
- what the file was, or what `/api/join` returned;
- that nothing else was fetched, such as a second-stage file through `redirect` or another tab
  (only recorded downloads appear here, and the history was later cleared);
- anything about the operating system outside the browser.

## 13. What was investigated on Linux Mint

The researcher reviewed active connections and listening ports, running processes (including Java
and Gradle), the previous boot's journal, `~/Downloads` and selected locations, user systemd
services and timers, cron, XDG autostart, selected system-wide persistence locations, and Brave
site permissions. One Java process was matched to a legitimate Gradle daemon. Other historical
Java processes were **not** conclusively attributed. Known legitimate items included PipeWire's
`filter-chain` service and the Launchpadlib cache-cleanup timer. No confirmed malicious
persistence or execution was found. (Observed and researcher-reported. Raw outputs were not
preserved.) See [linux-persistence-review.md](linux-persistence-review.md).

## 14. What evidence is still unavailable

- the `/api/join` JSON response, and the actual payload behind `/download/<token>`;
- raw email headers (sender authentication, origin IPs) and the 09:02 message attachments;
- a filesystem timeline (the file `files-timeline.txt` exists but is empty);
- memory images, a full-disk image, preserved terminal output from the host review, and
  Brave's network or disk cache from the incident time.

See [evidence-and-limitations.md](evidence-and-limitations.md#findings-that-could-not-be-independently-verified).

## 15. Defences that would reduce the impact of similar attacks

In short: verify the meeting domain against the vendor's real domain; treat "install our app to
join" as a red flag; keep the browser's "ask where to save" prompt on; never execute unexpected
downloads; and keep wallets and signing away from general browsing. The full guide is in
[security-recommendations.md](security-recommendations.md).
