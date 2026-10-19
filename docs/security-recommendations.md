# Security Recommendations

Written for both non-technical and technical readers. Items marked 🔧 are more technical.

## Spot the lure

- **Unsolicited invitations that flatter you** (podcasts, interviews, conferences, grants, jobs)
  and then move quickly to "join this meeting" are a known pattern. Verify the host independently,
  for example through a contact you already trust or an official site you find yourself.
- **Check the registrable domain**, not the first word of the hostname.
  `streamyard.host12us[.]com` belongs to `host12us[.]com`, not to StreamYard. Read the hostname
  **right to left** up to the first dot after the TLD.
- **"Install our app to join"** for a meeting you expected to join in the browser is a red flag.
  Legitimate platforms offer a browser option or link to their official download page on their own
  domain.
- **Last-minute links and "are you coming?" pressure** are designed to make you hurry. Slow down.
- **Be careful about sending personal photos and media** to unverified contacts. They can be reused
  for impersonation.
- Insisting on a platform you trust (as the researcher did) is a good defence. A real host can
  usually adapt.

## Browser security

- Keep Brave or your browser **up to date**, and restart it after updates.
- Turn on **"Ask where to save each file before downloading"**, so every download needs a
  decision from you.
- **Never** enable "open automatically" for any file type.
- Review site permissions regularly (*Settings → Privacy and security → Site and Shields
  settings*): pop-ups and redirects, notifications, clipboard, camera, microphone, USB, HID, serial,
  and automatic downloads. Remove anything you do not recognise.
- Use **separate browser profiles**, or separate browsers, for
  (1) meetings and general browsing, (2) Web3 and wallets, and (3) development and admin consoles.
- 🔧 **Flatpak sandboxing** limits what a *compromised browser process* can reach. It does
  **not** protect you from a file you save and run yourself, and the downloads folder is usually
  shared with the host. Check with
  `flatpak info --show-permissions com.brave.Browser`, and tighten it with
  `flatpak override --user` (or Flatseal) if appropriate.
- 🔧 Browser isolation and disposable VMs are the strongest option for opening untrusted meeting
  links, at some cost in convenience.

## Wallet and Web3 security

- Set wallet extensions to **"On click"** or **"On specific sites"** site access instead of
  "On all sites". Grant access only to sites you approved.
- Review **connected sites** in each wallet regularly and revoke what you do not use. Revoke
  token **approvals** too, using a trusted revocation interface.
- **Never sign unexpected messages or transactions.** A meeting site, "verification" page, or
  support agent has no reason to ask for a signature.
- **Verify transaction details on the hardware device's own screen**, not only in the browser.
- Keep **high-value funds and signing devices** away from your everyday browsing profile and
  machine. Consider a dedicated device or profile used only for signing.
- Understand the limits: restricting extension site access **reduces** what a malicious page can
  see and request. It is **not a complete anti-fingerprinting guarantee**, because some extensions
  can still be detected through side channels. See
  [threat-model.md](threat-model.md#wallet-extensions-five-separate-boundaries).

## Linux security

- **Do not run installers or scripts you did not seek out.** If you do need software, get it from
  your distribution's repositories, Flathub, or the vendor's official domain.
- **Verify provenance:** compare published checksums (`sha256sum file`) and verify signatures
  (`gpg --verify`) against keys obtained independently.
- **Never pipe network content into a shell** (`curl ... | sh`, `wget -O- ... | bash`).
- 🔧 **Inspect without executing:**
  ```bash
  file suspicious.bin            # what type is it really?
  sha256sum suspicious.bin       # hash for lookups and IoCs
  head -c 2000 suspicious.bin | less   # small text files: read them
  strings -n 6 suspicious.bin | less   # binaries: readable strings
  # .desktop files: look at Exec= ; scripts: read every line
  ```
  Do this as an unprivileged user, ideally in a disposable VM, and never `chmod +x` the file.
- Review persistence points periodically: `~/.config/autostart`,
  `~/.local/share/applications`, `~/.config/systemd/user`, `crontab -l`, and shell start-up files.
  See [linux-persistence-review.md](linux-persistence-review.md).
- Install security updates promptly (`sudo apt update && sudo apt upgrade`, or Update Manager).
- Keep **offline, versioned backups**.
- Use **least privilege**: work as a non-admin user, and do not type your `sudo` password in
  response to anything you did not start.

## Incident response

1. **Disconnect from the lure, not from your evidence.** Close the tab. Do not revisit the site.
2. **Preserve before cleaning.** Copy the browser's `History`, `DIPS`, and their `-wal`/`-journal`
   files (with the browser closed) **before** clearing history or cache. Save the original email
   **with full headers** (`.eml`, "Show original").
3. **Record time and timezone** for every observation.
4. **Hash** everything you preserve (`sha256sum`) and work only on copies.
5. Open SQLite copies **read-only** (`sqlite3 'file:History?mode=ro&immutable=1'`), and remember
   that opening a WAL database normally can change it.
6. **Do not open attachments** from the suspicious sender. Preserve them as evidence.
7. Separate **confirmed facts**, **observations**, and **hypotheses** in your notes.
8. **Escalate to professional incident response, and rotate credentials from a known-clean
   device**, if any of these apply:
   - you saved **and** opened or ran the file, or entered a password or seed anywhere;
   - you approved a wallet connection or signature on the site;
   - you find unknown autostart entries, services, cron jobs, listeners, or processes;
   - accounts show sign-ins, sessions, or API keys you do not recognise.

   If a seed phrase or private key may have been exposed, move funds to a **new** wallet created
   on a clean device. Rotating passwords does not fix a leaked seed.
9. **Report** the infrastructure. See [responsible-disclosure.md](responsible-disclosure.md).
