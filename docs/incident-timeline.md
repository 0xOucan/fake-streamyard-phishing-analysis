# Incident Timeline

All times are **local time, UTC-05:00**, on 2026-10-19 unless stated otherwise. Browser times were
converted from Chromium's WebKit epoch (microseconds since 1601-01-01 UTC).

**Source tags**

- **Email:** times shown by the researcher's mail client in a copied transcript. Raw message headers
  were not available, so the sender and transport were not authenticated.
- **History:** Brave `History` SQLite copy (`visits`, `downloads`, `downloads_url_chains`).
- **urlscan:** public urlscan.io scan metadata (`result.json`).
- **FS:** modification times of files in the local evidence folder.
- **Reported:** statements by the researcher with no preserved artifact.

| Time | Event | Source | Confidence |
|------|-------|--------|------------|
| 2026-10-13 07:21:04 **UTC** | TLS certificate for `host12us[.]com` becomes valid (urlscan reports `tlsAgeDays: 6`). | urlscan | Confirmed |
| 04:56 | First email from a purported podcast producer (`info@beaconlayer[.]cc`), with a detailed episode outline built from the researcher's public posts and a request for a high-resolution portrait. | Email | Observed |
| 07:22–07:28 | The researcher accepts and the sender asks again for a photo. | Email | Observed |
| 08:21 | The researcher sends images and logos to the sender. | Email | Observed |
| 08:53 | The sender provides "Recording Details": platform *StreamYard*, **10:00 AM ET** (= 09:00 local), and the join link on `streamyard.host12us[.]com`. | Email | Observed |
| 09:00:09 | Brave visits the meeting URL through an email link-redirector (`LINK` transition, server redirect). Page title: `StreamYard Webinar`. Visit lasts ~89 s. | History | Confirmed |
| **09:01:07** | **Download record 1115 is created** from the meeting tab: `/download/<token>`, `application/octet-stream`, `total_bytes=857`. It ends **cancelled** (`state=2`, `interrupt_reason=40`) with `received_bytes=0`, `opened=0`, and an empty target path. | History | Confirmed |
| 09:01:55 | Second visit to the meeting URL through the same email link (~17 s). | History | Confirmed |
| 09:02 | The sender writes "coming? Waiting for you." The message includes attachments, which were **not opened or analysed**. | Email | Observed |
| 09:06 | The researcher replies that they only use another meeting platform. | Email | Observed |
| 09:07:42 | Public urlscan.io scan of the meeting URL. The scanner did not click **Join**, so no `/api/*` request was captured. urlscan verdict at scan time: not malicious, score 0. | urlscan | Confirmed |
| 09:08 | The sender replies "Canceled our meeting". | Email | Observed |
| 09:22:19 | Third visit to the meeting URL from a newer email link (~28 s). The artifacts do not record why. No further download records exist. | History | Confirmed |
| 09:25 | Brave `History` copied for analysis. | FS | Confirmed |
| 09:43–10:07 | urlscan artifacts retrieved and the JavaScript statically decoded. | FS | Confirmed |
| before 10:12 | Brave history and cache cleared by the researcher. | Reported | Observed |
| 10:12 | Brave `DIPS` and `DIPS-wal` copied. | FS | Confirmed |
| — | Linux processes, network, services, timers, cron, and autostart reviewed. | Reported | Observed |

## Notes

- The researcher recalled the interaction as roughly 08:55–09:03. The browser records place the
  page visits at 09:00–09:02, which is consistent with that recollection.
- The "10:00 AM ET" invitation time is 09:00 in UTC-05:00 (US Eastern observes daylight saving
  time, UTC-04:00, in mid-October). It matches the first visit to within seconds.
- The ~60 s gap between the cancelled download (09:01:07) and the "coming?" message (09:02) fits
  the operator watching `/api/hit` telemetry, but it is **not proof**. Email minute-level times
  are not precise enough.
- The urlscan scan time comes from urlscan's own task record. The scan was run *after* the visits,
  so it shows how the site looked at 09:07, not necessarily at 09:00.
