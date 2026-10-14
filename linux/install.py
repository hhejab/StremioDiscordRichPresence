#!/usr/bin/env python3
"""Build the native Linux implementation against a supported Stremio checkout."""
import argparse
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

PIN = 'd7bb4e7795389f0d8cf96abe5f2574cee632698c'
PACKAGE = Path(__file__).resolve().parent

def run(args, cwd=None, capture=False, check=True):
    return subprocess.run(args, cwd=cwd, check=check, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None)

def desktop_argument(value):
    if '\n' in value or '\r' in value:
        raise ValueError('Desktop paths cannot contain newlines')
    value = value.replace('%', '%%').replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
    return '"' + value + '"'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Existing stremio-linux-shell checkout')
    parser.add_argument('--check-only', action='store_true', help='Check compatibility without changing any files')
    parser.add_argument('--offline', action='store_true', help='Use only cached Rust dependencies')
    parser.add_argument('--install-desktop', action='store_true', help='Add a separate Stremio RPC Linux launcher')
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    patch = PACKAGE / 'stremio-linux-shell.patch'
    if not (source / 'Cargo.toml').is_file() or not patch.is_file():
        parser.error('Expected a Stremio source checkout and the bundled patch')
    head = run(['git', 'rev-parse', 'HEAD'], source, capture=True).stdout.strip()
    applied = run(['git', 'apply', '--reverse', '--check', str(patch)], source, capture=True, check=False).returncode == 0
    if not applied:
        if head != PIN:
            parser.error(f'Unsupported source revision {head}; use {PIN}. Existing source was not modified.')
        if run(['git', 'status', '--porcelain'], source, capture=True).stdout.strip():
            parser.error('Source has local changes. Commit or save them before applying this port.')
        run(['git', 'apply', '--check', str(patch)], source)
    if args.check_only:
        print('Compatible: Linux port already applied.' if applied else 'Compatible: patch can be applied safely.')
        return
    for command in ['git', 'cargo', 'rustc', 'node', 'pkg-config', 'msgfmt', 'glib-compile-schemas']:
        if not shutil.which(command):
            parser.error(f'Missing build dependency: {command}')
    for package, version in [('gtk4','4.22'),('libadwaita-1','1.9'),('webkitgtk-6.0','2.52')]:
        run(['pkg-config', '--atleast-version='+version, package])
    for package in ['mpv', 'epoxy']:
        run(['pkg-config', '--exists', package])
    if not applied:
        run(['git', 'apply', str(patch)], source)
    binary = source / 'target/release/stremio-linux-shell'
    if binary.exists():
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup = binary.with_name(binary.name + '.before-linux-rpc-' + stamp)
        shutil.copy2(binary, backup)
        print('Working executable preserved:', backup)
    options = ['--release', '--locked'] + (['--offline'] if args.offline else [])
    run(['node', '--test', str(PACKAGE/'tests/metadata.test.js')])
    run(['cargo', 'test', *options], source)
    run(['cargo', 'build', *options], source)
    if args.install_desktop:
        data = Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))
        applications = data / 'applications'
        applications.mkdir(parents=True, exist_ok=True)
        entry = applications / 'stremio-rpc-linux.desktop'
        if entry.exists():
            shutil.copy2(entry, entry.with_suffix('.desktop.previous'))
        server = source / 'data/server.js'
        icon = source / 'data/icons/com.stremio.Stremio.svg'
        text = ('[Desktop Entry]\nName=Stremio RPC Linux\nComment=Stremio with Discord Rich Presence\n'
                'Exec=env '+desktop_argument('SERVER_PATH='+str(server))+' '+desktop_argument(str(binary))+'\n'
                'Icon='+str(icon)+'\nType=Application\nTerminal=false\nCategories=AudioVideo;Video;Player;\n')
        temporary = entry.with_suffix('.desktop.tmp')
        temporary.write_text(text)
        temporary.replace(entry)
        print('Launcher installed:', entry)
    print('Build ready:', binary)
    print('Launch with SERVER_PATH pointing to', source/'data/server.js')

if __name__ == '__main__':
    try:
        main()
    except (subprocess.CalledProcessError, ValueError) as error:
        print('Build stopped:', error, file=sys.stderr)
        sys.exit(1)
