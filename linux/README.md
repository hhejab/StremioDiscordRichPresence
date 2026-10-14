# Native Linux port

This implementation brings the original Windows card style to the GTK Stremio Linux shell. The Windows DLL and memory offsets are not used on Linux. Instead, a bundled source patch connects native MPV events, Stremio's loaded player metadata, and the existing `discord-rich-presence` crate.

## Install

Build dependencies: Rust/Cargo, Git, Node.js, pkg-config, gettext (`msgfmt`), GLib utilities, GTK4 >= 4.22, libadwaita >= 1.9, WebKitGTK 6.0 >= 2.52, libmpv, and libepoxy. Install these through your distribution first. The installer never installs system packages or uses sudo.

```sh
git clone https://github.com/hhejab/StremioDiscordRichPresence.git
git clone https://github.com/Stremio/stremio-linux-shell.git
git -C stremio-linux-shell checkout d7bb4e7795389f0d8cf96abe5f2574cee632698c
python3 StremioDiscordRichPresence/linux/install.py --source stremio-linux-shell --install-desktop
```

The separate **Stremio RPC Linux** launcher runs the patched shell and its included streaming server. Open Discord Desktop and launch Stremio through that shortcut. Artwork and episode information depend on the selected addon metadata. Movies without an IMDb identifier get the Stremio button only. Missing poster/thumbnail data falls back to the normal title/artwork or Stremio icon.

For an existing clean checkout at the supported revision:

```sh
python3 linux/install.py --source /path/to/stremio-linux-shell --check-only
python3 linux/install.py --source /path/to/stremio-linux-shell
```

The installer refuses incompatible revisions and unrelated local changes. An already-applied patch is detected and can be rebuilt. Add `--offline` when the locked Rust dependencies are already cached.

For a custom Discord application, set `STREMIO_DISCORD_CLIENT_ID` in the environment before launching Stremio. The default is the original project's public Discord application ID. The Linux connection starts automatically each launch; the frontend's explicit disconnect method disables it for the current session.

## Rollback

Before compiling, the installer copies an existing executable to `target/release/stremio-linux-shell.before-linux-rpc-<timestamp>`. Fully quit Stremio, then copy that saved executable back to `target/release/stremio-linux-shell` to restore it. The installer also preserves an existing generated desktop entry as `.desktop.previous`.

To remove source changes from a checkout where this exact patch was installed:

```sh
git -C /path/to/stremio-linux-shell apply --reverse --check /path/to/linux/stremio-linux-shell.patch
git -C /path/to/stremio-linux-shell apply --reverse /path/to/linux/stremio-linux-shell.patch
```

The reverse check must succeed before reversing the patch. Save any later edits first.

## Implementation

- `stremio-linux-shell.patch` includes the complete Rust Discord controller, IPC integration, JavaScript metadata bridge, and Rust regression tests.
- `metadata-bridge.js` is the reviewable bridge source mirrored in the patch. It calls the frontend's existing `window.core.getState('player')` method. It never calls `fetch`, dispatches a load action, or starts another metadata request.
- `install.py` checks compatibility, preserves the executable, applies the patch, runs tests, builds with the existing lockfile, and optionally adds a launcher.
- `tests/metadata.test.js` checks loaded metadata, stale episode/navigation results, core reload failures, and malformed messages.

Playback state and timing come from MPV. `media.status` is treated only as a pause flag. Redirects and `loadfile` replacement are handled without losing the new episode metadata. Repeated playback-clock ticks retain stable timestamps to avoid sending every MPV update to Discord. Timers are removed while paused; at non-default playback speed the remaining-time estimate is adjusted for the selected speed.

Discord socket operations run on a worker so a blocked handshake cannot freeze the player. Connection failures are retried after 15 seconds. Exit queues a clear/disconnect and process exit closes any remaining socket without waiting for a blocked handshake.

## Validation

```sh
node --test linux/tests/metadata.test.js
cargo test --manifest-path /path/to/stremio-linux-shell/Cargo.toml --release --locked
cargo build --manifest-path /path/to/stremio-linux-shell/Cargo.toml --release --locked
# Requires an active X11 display, ffmpeg and dbus-run-session; opens a test window.
python3 linux/tests/smoke.py --source /path/to/stremio-linux-shell
```

Validated on CachyOS:

- Eight Rust regression tests covering lifecycle, reconnection, artwork/buttons, Unicode limits, seeking/speed changes, pause, and invalid values.
- Five metadata-bridge tests, including a mocked network function that fails if called.
- A real GTK/WebKit/MPV playback test against an isolated simulated Discord socket: poster, episode thumbnail, both buttons, running timestamps, paused timer removal, episode replacement, seeking, stop cleanup, late messages, and exit.
- Patch compatibility against both an already-patched checkout and a fresh checkout of the pinned source.

The Discord payload was verified; the exact visual rendering of the card on a real Discord profile has not been manually verified.

## Attribution and license

The Windows implementation and card design originate from Loukious. The Linux integration extends the existing Stremio Linux shell's Discord module; the source patch identifies the modified upstream files and is based on the pinned source revision above. Both upstream projects use GPLv3; the original license is retained in `../LICENSE.txt`. This is a community fork, not an official Stremio or Discord release.
