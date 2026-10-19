# Linux Persistence and Execution Review

> **Scope warning.** This was a **live triage**, not a full-disk image, memory forensics, or an
> exhaustive malware scan. The results below were **reported by the researcher**. Raw command
> output was not preserved in the evidence set. Every item is therefore **Observed**, not
> **Confirmed**.

## Environment

- Linux Mint (desktop), with Brave installed as a **Flatpak**.
- Development tooling on the host, including a JVM and Gradle.

## What was reviewed, and the results

| Area | Result reported | Confidence |
|---|---|---|
| Active connections and listening ports | Reviewed; no confirmed malicious finding | Observed |
| Processes | One Java process matched a **legitimate Gradle daemon**. Other **historical** Java processes were **not conclusively attributed**: neither linked to the incident nor ruled out. | Observed |
| Previous-boot journal | Reviewed; no confirmed malicious finding | Observed |
| `~/Downloads` and selected filesystem locations | Reviewed; no confirmed malicious finding | Observed |
| User systemd services and timers | Known legitimate entries identified, including PipeWire `filter-chain` and the Launchpadlib cache-cleanup timer; no confirmed malicious finding | Observed |
| Cron | Reviewed; no confirmed malicious finding | Observed |
| XDG autostart | Reviewed; no confirmed malicious finding | Observed |
| Selected system-wide persistence locations | Reviewed; no confirmed malicious finding | Observed |
| Filesystem timeline | **Not available** (output file is empty) | Unknown |

**Conclusion:** no confirmed malicious persistence or payload execution was identified **in the
reviewed evidence**. This does not prove that no malware exists anywhere on the system.

## How to repeat this triage

All commands are read-only. Run them as your normal user unless `sudo` is shown. Save the output
**before** cleaning anything up.

```bash
# Evidence folder for this triage (keep it outside any git repository)
OUT=~/ir-$(date +%Y%m%dT%H%M%S); mkdir -p "$OUT"

# Network and processes
ss -tupan                       > "$OUT/ss.txt"
ps -eo pid,ppid,user,lstart,etime,cmd --sort=lstart > "$OUT/ps.txt"
ps -eo pid,cmd | grep -iE 'java|gradle' | grep -v grep >> "$OUT/java.txt"

# Boot journal (previous boot) and user journal
journalctl -b -1 --no-pager     > "$OUT/journal-prev-boot.txt"
journalctl --user -b --no-pager > "$OUT/journal-user.txt"

# systemd units and timers (user and system)
systemctl --user list-unit-files --state=enabled > "$OUT/user-units.txt"
systemctl --user list-timers --all               > "$OUT/user-timers.txt"
systemctl list-timers --all                      > "$OUT/system-timers.txt"
ls -la ~/.config/systemd/user/ 2>/dev/null       > "$OUT/user-unit-dir.txt"

# Cron
crontab -l 2>&1                                  > "$OUT/crontab-user.txt"
ls -la /etc/cron.* /etc/crontab /var/spool/cron 2>/dev/null > "$OUT/cron-system.txt"

# Autostart and desktop entries
ls -la ~/.config/autostart /etc/xdg/autostart ~/.local/share/applications 2>/dev/null > "$OUT/autostart.txt"

# Shell start-up files changed recently (review by hand)
ls -la --time-style=full-iso ~/.bashrc ~/.profile ~/.bash_profile ~/.zshrc 2>/dev/null > "$OUT/shell-rc.txt"

# Files created or changed in the incident window (adjust the times)
find ~ -xdev -newermt '2026-10-19 08:50' ! -newermt '2026-10-19 10:00' \
     -not -path '*/.cache/*' -printf '%TY-%Tm-%Td %TT %m %s %p\n' 2>/dev/null | sort > "$OUT/fs-window.txt"

# Flatpak sandbox permissions for Brave
flatpak info --show-permissions com.brave.Browser > "$OUT/brave-flatpak-perms.txt"

sha256sum "$OUT"/* > "$OUT/SHA256SUMS"
```

**Privacy note:** this output contains usernames, paths, and process command lines that may
include secrets. Do **not** commit it to a public repository.

## Interpreting results

- **Java/Gradle:** a `GradleDaemon` command line under `~/.gradle` that started when you ran a
  build is expected. A Java process with an unknown JAR in `/tmp`, `~/Downloads`, or a hidden
  directory, or with a network listener you did not create, needs investigation.
- **Timers and services:** compare each entry with the package that owns it
  (`dpkg -S <path>` for system files). User units under `~/.config/systemd/user` belong to no
  package, so review them manually.
- **`.desktop` files:** look at the `Exec=` line. A launcher in `~/.local/share/applications` or
  `~/.config/autostart` that runs `bash -c`, `curl | sh`, or a binary from a hidden directory is a
  red flag.
