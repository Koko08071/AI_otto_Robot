"""Start the relocated Windows runtime without contacting the robot."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true', help='Check HTTP startup then exit; no robot commands')
    args = parser.parse_args()
    config_path = ROOT / 'config.local.json'
    if not config_path.exists():
        config_path.write_bytes((ROOT / 'config.example.json').read_bytes())
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    preferred = int(config.get('OTTO_PORT', 8765))
    port = None
    for candidate in range(preferred, min(preferred + 30, 65536)):
        with socket.socket() as probe:
            try:
                probe.bind(('127.0.0.1', candidate))
                port = candidate
                break
            except OSError:
                continue
    if port is None:
        raise RuntimeError('No free localhost port; change OTTO_PORT in config.local.json')
    env = dict(os.environ)
    for key in list(env):
        if key.upper().startswith(('PYTHON', 'OTTO_')):
            env.pop(key)
    env.update(OTTO_PORT=str(port), PYTHONUTF8='1', NO_PROXY='*', no_proxy='*')
    url = f'http://127.0.0.1:{port}'
    print(f'Otto Studio: {url}', flush=True)
    print('Keep this window open. Stop robot motion in the webpage before closing.', flush=True)
    child = subprocess.Popen([sys.executable, '-E', '-s', '-X', 'utf8', str(ROOT / 'web/server.py')], cwd=ROOT, env=env)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if child.poll() is not None:
                raise RuntimeError(f'Server exited with code {child.returncode}')
            try:
                with opener.open(url + '/api/resources', timeout=2) as response:
                    assert response.status == 200
                    json.load(response)
                break
            except OSError:
                time.sleep(0.3)
        else:
            raise RuntimeError('Server startup timed out')
        if args.smoke:
            for path in ['/', '/composer.html', '/api/status']:
                with opener.open(url + path, timeout=5) as response:
                    assert response.status == 200
                    data = response.read()
                    if path == '/api/status':
                        assert not json.loads(data)['connected']
                    print(f'PASS {path}: {len(data)} bytes', flush=True)
            return 0
        webbrowser.open(url)
        return child.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        if child.poll() is None:
            child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


if __name__ == '__main__':
    raise SystemExit(main())
