import json, os, pathlib, socket, struct, subprocess, threading, time, tempfile

import argparse
parser=argparse.ArgumentParser(description='Isolated GTK/WebKit/MPV → Discord integration test; opens a temporary window.')
parser.add_argument('--source',type=pathlib.Path,required=True)
args=parser.parse_args()
source=args.source.expanduser().resolve()
fixture=pathlib.Path(__file__).resolve().parent/'smoke.html'
base=pathlib.Path(tempfile.mkdtemp(prefix='stremio-rpc-smoke-'))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','color=c=black:s=320x180:r=10','-t','20','-c:v','mpeg4',str(base/'media.mp4')],check=True)
(base/'discord-smoke.html').write_text(fixture.read_text().replace('TEST_MEDIA',str(base/'media.mp4')))
runtime = pathlib.Path(tempfile.mkdtemp(prefix='stremio-rpc-test-'))
runtime.mkdir(mode=0o700, exist_ok=True)
pipe = runtime / 'discord-ipc-0'
if pipe.exists(): pipe.unlink()
server = socket.socket(socket.AF_UNIX)
server.bind(str(pipe)); server.listen(); server.settimeout(25)
packets = []
errors = []

def read_exact(conn, count):
    result = b''
    while len(result) < count:
        data = conn.recv(count-len(result))
        if not data: raise EOFError
        result += data
    return result

def listen():
    try:
        conn, _ = server.accept()
        with conn:
            conn.settimeout(20)
            while True:
                op, length = struct.unpack('<II', read_exact(conn,8))
                data = json.loads(read_exact(conn,length))
                packets.append({'op':op,'data':data})
                if op == 0:
                    reply = json.dumps({'cmd':'DISPATCH','evt':'READY','data':{}}).encode()
                    conn.sendall(struct.pack('<II',1,len(reply))+reply)
                if op == 2: break
    except EOFError:
        packets.append({'closed':True})
    except Exception as exc: errors.append(repr(exc))

worker=threading.Thread(target=listen,daemon=True);worker.start()
(base/'idle-server.js').write_text('setInterval(() => {}, 1000);\n')
env=os.environ.copy()
env.update({
 'XDG_RUNTIME_DIR': str(runtime), 'TMPDIR':str(runtime), 'TMP':str(runtime), 'TEMP':str(runtime),
 'XDG_CONFIG_HOME':str(runtime/'config'), 'XDG_CACHE_HOME':str(runtime/'cache'),
 'XDG_DATA_HOME':str(runtime/'data'), 'GSETTINGS_BACKEND':'memory',
 'GSETTINGS_SCHEMA_DIR':str(pathlib.Path(os.environ.get('XDG_DATA_HOME',str(pathlib.Path.home()/'.local/share')))/'glib-2.0/schemas'),
 'SERVER_PATH':str(base/'idle-server.js'), 'GDK_BACKEND':'x11',
})
with (base/'smoke-app.log').open('w') as log:
    process=subprocess.Popen(['dbus-run-session','--',str(source/'target/release/stremio-linux-shell'),'--url',(base/'discord-smoke.html').as_uri()],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try: code=process.wait(timeout=25)
    except subprocess.TimeoutExpired:
        import signal
        os.killpg(process.pid,signal.SIGTERM)
        process.wait(timeout=5)
        raise AssertionError(f'Stremio did not exit automatically; see {base}/smoke-app.log')
worker.join(timeout=3)
server.close()
(base/'smoke-packets.json').write_text(json.dumps(packets,indent=2))
assert code==0, f'Stremio exited {code}: see {base}/smoke-app.log'
assert not errors, errors
activities=[p['data']['args']['activity'] for p in packets if p.get('data',{}).get('cmd')=='SET_ACTIVITY']
assert any(a and a['details']=='Presence Test Series' and 'Pilot' in a['state'] for a in activities), activities
assert any(a and a['state'].startswith('Paused') for a in activities), activities
assert any(a and 'Second episode' in a['state'] for a in activities), activities
assert all(a is None or a['details']!='STALE' for a in activities), activities
assert activities[-1] is None, activities
assert any(a and a.get('timestamps',{}).get('end') for a in activities), 'Missing playback timestamps'
assert all(not a.get('timestamps') for a in activities if a and a['state'].startswith('Paused')), 'Paused timer is still running'
assert any(a and a.get('assets',{}).get('small_image')=='https://example.com/episode1.jpg' for a in activities)
assert any(a and len(a.get('buttons',[]))==2 for a in activities), 'Missing IMDb/Stremio buttons'
assert any(p.get('op')==2 or p.get('closed') for p in packets), 'Socket did not close'
assert all(a is None or a['assets']['large_image']=='https://example.com/poster.jpg' for a in activities)
print('PASS: actual GTK/WebKit → IPC → MPV → Discord socket: episode/artwork, pause/resume, stream replacement, stop, late messages and application exit.')
print('Activity sequence:', [(a['details'],a['state']) if a else None for a in activities])

print("Test logs and captured packets:",base)
