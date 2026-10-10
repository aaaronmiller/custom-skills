# Browser skill: install layout and troubleshooting

Verified on this machine 2026-10-09: all three anti-bot rungs ran, and rungs 2
and 3 returned real posts from `https://www.reddit.com/r/Polymarket/`.

## Install layout

| Engine | Version | Binary on PATH | Real location |
|---|---|---|---|
| Obscura (stealth build) | 0.2.4 | `/home/cheta/.local/bin/obscura` | `/home/cheta/.local/opt/obscura-0.2.4/` |
| Camoufox | 0.5.7 pip package | `/home/cheta/.local/bin/camoufox-fetch`, `/home/cheta/.local/bin/camoufox` | venv `/home/cheta/.venvs/camoufox`, browser in `/home/cheta/.cache/camoufox/` |
| Interceptor (browser-only) | 1.0.24 | `/home/cheta/.local/bin/interceptor` | `/home/cheta/.local/opt/interceptor` -> `interceptor-1.0.24/Interceptor-Browser-1.0.24-linux-x64` |
| Interceptor browser launcher | n/a | `/home/cheta/.local/bin/interceptor-browser` | Chrome for Testing 151 at `/home/cheta/.cache/ms-playwright/chromium-1234/` |
| agent-browser | 0.38.2 | `/home/cheta/.npm-global/bin/agent-browser` | npm global |

Camoufox is pinned to 0.5.7 because `/home/cheta/.config/uv/uv.toml` sets an
`exclude-newer` supply-chain cooldown; 0.5.8 becomes installable once it ages
past that window. Upgrade with:

```bash
uv pip install -p /home/cheta/.venvs/camoufox -U 'camoufox[geoip]' && /home/cheta/.venvs/camoufox/bin/camoufox fetch
```

An older Camoufox 0.4.11 also exists inside the litellm venv. It is shadowed
on PATH by `/home/cheta/.local/bin/camoufox` and is not used by this skill.

## Interceptor wiring

The stock `scripts/install.sh` on Linux only supports branded `google-chrome`
or Brave, neither of which is installed. The equivalent manual wiring:

- Profile: `/home/cheta/.local/share/interceptor/chrome-profile`
  (Developer Mode preset in `Default/Preferences`).
- Native messaging manifest:
  `/home/cheta/.local/share/interceptor/chrome-profile/NativeMessagingHosts/com.interceptor.host.json`,
  `path` set to the release's `daemon/interceptor-daemon`.
- Launcher flags: `--load-extension=<release>/extension/dist`,
  `--password-store=basic` (stops the GNOME keyring prompt on WSLg),
  `--disable-features=DisableLoadExtensionCommandLineSwitch`.
- Display: WSLg (`DISPLAY=:0`). No Xvfb and no proxy bridge are needed here;
  those were sandbox-VM workarounds in the 2026-09-18 setup report.
- Override the browser binary with `INTERCEPTOR_CHROME=/path/to/chrome`.

Upgrading Interceptor: download the new `Interceptor-Browser-<v>-linux-x64.tar.gz`
and `SHA256SUMS` from the GitHub releases of Hacker-Valley-Media/Interceptor,
verify, extract under `/home/cheta/.local/opt/`, repoint the
`/home/cheta/.local/opt/interceptor` symlink, regenerate the manifest `path`,
then `interceptor-browser stop && interceptor-browser start`.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `timeout: no response for 'get_a11y_tree'` | Browser not running, or extension not loaded | `interceptor-browser start`; check `/home/cheta/.local/state/interceptor-browser.log` |
| Keyring / password prompt on screen | Chrome asking GNOME keyring for a store | Launcher passes `--password-store=basic`; cancel any old prompt |
| `NotInstalledGeoIPExtra` from Camoufox | geoip extra missing | `uv pip install -p /home/cheta/.venvs/camoufox 'camoufox[geoip]'` |
| Obscura returns challenge HTML, no content | Real JS challenge; Obscura cannot solve it | Escalate to `camoufox-fetch` |
| agent-browser gets "blocked by network security" | Headless Chromium fingerprint | Escalate to `camoufox-fetch`; never retry agent-browser |

## Background

Engine ranking and forensics came from three reports in the Windows Documents
folder (2026-09-18): `Browser-Showdown-Report.md`,
`Browser-Forensics-VM-Strategy.md`, `Interceptor-Setup-Report.md`.
