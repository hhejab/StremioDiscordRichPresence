# Discord Rich Presence for Stremio on Linux

I forked [Loukious/StremioDiscordRichPresence](https://github.com/Loukious/StremioDiscordRichPresence) to make a Linux version for the GTK Stremio Linux shell.

**The original Windows project and its Discord presence design were created by [Loukious](https://github.com/Loukious).** This repository is my Linux adaptation of his work.

- **Original project:** [Loukious/StremioDiscordRichPresence](https://github.com/Loukious/StremioDiscordRichPresence)
- **Linux fork:** [hhejab/StremioDiscordRichPresence](https://github.com/hhejab/StremioDiscordRichPresence)

This version is tested on CachyOS with [Stremio/stremio-linux-shell](https://github.com/Stremio/stremio-linux-shell). It supports that GTK client, not the older Qt Stremio 4 Linux client or playback in an external player.

## Features

- Shows the movie or series you are watching on Discord.
- Shows the episode title, season, and episode number for series.
- Shows poster artwork and an episode thumbnail when available in Stremio's metadata.
- Shows a playback timer that updates after seeking, resuming, or changing playback speed.
- Shows when playback is paused and removes the running timer until playback resumes.
- Shows buttons to open IMDb and Stremio Web when the media identifiers are available.
- Connects automatically when Stremio opens and retries if Discord starts later.
- Clears your activity when playback stops, finishes, or fails.
- Disconnects when Stremio exits.

It uses the metadata Stremio has already loaded. No additional metadata API key or separate background app is required.

## Screenshots

These screenshots belong to **Loukious's original Windows project** and are included as a reference for its Discord card layout. They are not screenshots of the Linux port.

![Original Windows project: playing](https://i.imgur.com/q0u4BFn.png)
![Original Windows project: paused](https://i.imgur.com/AKG0Bi0.png)
![Original Windows project: episode thumbnail](https://i.imgur.com/WZ0A887.png)
![Original Windows project: movie or series artwork](https://i.imgur.com/CXIPc7R.png)

## Steps to install

1. Install the Linux build prerequisites listed below.
2. Clone this fork and the supported Stremio Linux shell:

   ```sh
   git clone https://github.com/hhejab/StremioDiscordRichPresence.git
   git clone https://github.com/Stremio/stremio-linux-shell.git
   git -C stremio-linux-shell checkout d7bb4e7795389f0d8cf96abe5f2574cee632698c
   ```

3. Apply the Linux patch, run the tests, build Stremio, and add a launcher:

   ```sh
   python3 StremioDiscordRichPresence/linux/install.py --source stremio-linux-shell --install-desktop
   ```

4. Open Discord Desktop and launch **Stremio RPC Linux** from your applications menu.
5. Play a movie or episode and check your Discord activity.

The installer preserves an existing executable before building. The Linux patch currently targets the exact Stremio revision shown above.

For an existing checkout, compatibility checks, and more installation details, see the [Linux guide](linux/README.md).

## Configuring the mod

Rich Presence starts automatically with Stremio using the default Discord application ID.

To use your own Discord application, set `STREMIO_DISCORD_CLIENT_ID` in Stremio's environment before launching it. See the [Linux configuration instructions](linux/README.md#install) for details.

The Windows `RPCconfig.ini` settings do not apply to this Linux implementation.

## Steps to uninstall

1. Fully quit Stremio.
2. Restore the executable saved as `target/release/stremio-linux-shell.before-linux-rpc-<timestamp>` to `target/release/stremio-linux-shell`.
3. Remove the separate `stremio-rpc-linux.desktop` launcher from `~/.local/share/applications/`, or your custom `XDG_DATA_HOME/applications/` directory. If an earlier launcher was backed up as `.desktop.previous`, restore it instead.

See [rollback instructions](linux/README.md#rollback) to remove the source patch as well.

## Support

For Linux installation, troubleshooting information, and tests, see the [Linux guide](linux/README.md).

To support **Loukious, the original author**, visit [his Buy Me a Coffee page](https://buymeacoffee.com/loukious).

For the original Windows version, visit [his repository](https://github.com/Loukious/StremioDiscordRichPresence).

## Build prerequisites

- Python 3, Git, Rust, and Cargo.
- Node.js and pkg-config.
- GTK4 >= 4.22, libadwaita >= 1.9, and WebKitGTK 6.0 >= 2.52.
- libmpv, libepoxy, gettext, and GLib build utilities.

Install these through your Linux distribution before running the installer. See the [Linux guide](linux/README.md#install) for the complete requirements.

## Credits and license

- **Loukious:** original Stremio Discord Rich Presence project and Windows implementation.
- **Stremio contributors:** the GTK Linux shell and its existing Discord integration.
- **hhejab:** this fork and the Linux adaptation.

The original [GPLv3 license](LICENSE.txt) is retained.
