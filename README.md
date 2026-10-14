# Stremio Discord Rich Presence — Windows + Linux

A fork of [Loukious/StremioDiscordRichPresence](https://github.com/Loukious/StremioDiscordRichPresence), adding a native Linux implementation for the GTK Stremio Linux shell.

## Linux

The Linux port runs inside Stremio and uses its actual MPV playback events. It connects automatically when Stremio opens, retries if Discord starts later, clears activity on stop/end/error, and disconnects when Stremio exits.

Its Discord card includes:

- Separate movie/show title and episode title with season/episode numbers.
- Poster artwork and an episode thumbnail when present in Stremio's loaded metadata.
- A pause indicator that stops the running timer.
- Playback timing that updates after seeking, resuming, and changing playback speed.
- IMDb and Stremio Web buttons when the corresponding media identifiers are available.

It reads metadata that Stremio has already loaded. It does not request another metadata service, need an API key, or run a second background app.

**Compatibility:** This version targets [Stremio/stremio-linux-shell](https://github.com/Stremio/stremio-linux-shell) revision `d7bb4e7795389f0d8cf96abe5f2574cee632698c`, tested on CachyOS. It does not support the older Qt Stremio 4 Linux client or playback handed to an external player. Windows builds retain the original implementation below.

See [Linux installation and development](linux/README.md) for setup, requirements, tests, rollback, and the source patch.

---

# Original Windows implementation
This is a simple mod that adds Discord Rich Presence support to Stremio 4. It shows the movie or series you are watching on Discord.
For Stremio 5, please check out my other project [here](https://github.com/Loukious/stremio-shell-ng)

## Features
- Shows the movie or series you are watching on Discord.
- Shows the current time of the movie or series.
- Shows the episode number and season of the series you are watching (in case of a series).
- Shows when you are paused (Optional).
- Shows when you are in the main menu (Optional).
- Shows thumbnail of the movie or series you are watching.
- Shows a smaller thumbnail of the episode you are watching (in case of a series).
- Shows a button to see the movie or series on IMDb (Optional).
- Shows a button to see the movie or series on Stremio Web (Optional).
- Configurable settings.

## Screenshots
![General view playing](https://i.imgur.com/q0u4BFn.png)
![General view paused](https://i.imgur.com/AKG0Bi0.png)
![Small icon shows episode name](https://i.imgur.com/WZ0A887.png)
![Big icon shows movie/series name](https://i.imgur.com/CXIPc7R.png)


## Steps to install
1. Locate the Stremio installation folder.
> By default, for Stremio 4 it is `%localappdata%\Programs\LNV\Stremio-4`.

2. Download the zip file for [Stremio 4](https://github.com/Loukious/StremioDiscordRichPresence/releases/latest) and extract it in your Stremio folder.
3. Verify that your Discord Rich Presence is working.

## Configuring the mod
1. Open the `RPCconfig.ini` file in the Stremio folder.
2. Change the settings as you like.
3. Save the file.

## Steps to uninstall
1. Delete the `DWrite.dll` file from the Stremio folder.

> ⚠️ **Warning:** Please note that after updating Stremio, the DWrite.dll file might break and will cause Stremio to crash. Make sure to check for updates or reapply the necessary changes to ensure compatibility.
# Support
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/loukious)

## Build rerequisites
- Visual Studio 2019 or later
