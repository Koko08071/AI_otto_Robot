"""Build a Windows x64 handoff with a relocatable CPython and local assets."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    parser.add_argument('--device-url', default='http://otto.local')
    parser.add_argument('--zip-only', action='store_true')
    parser.add_argument('--stage-only', action='store_true')
    args = parser.parse_args()
    target = args.destination.resolve()
    if target == ROOT or target.is_relative_to(ROOT):
        raise ValueError('Choose a destination outside the repository')
    if not args.zip_only:
        target.mkdir(parents=True, exist_ok=False)
        print('Copying project source...', flush=True)
        files = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode().split('\0')
        for name in filter(None, files):
            source = ROOT / name
            if not source.is_file():
                continue
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        ignore = shutil.ignore_patterns('__pycache__', '*.pyc', '.cache')
        for name in ['models', 'voice-model', 'web/library/audio', 'web/behaviors']:
            source = ROOT / name
            if source.is_dir():
                print(f'Copying {name}...', flush=True)
                shutil.copytree(source, target / name, dirs_exist_ok=True, ignore=ignore)
        config = json.loads((ROOT / 'config.example.json').read_text(encoding='utf-8'))
        config['OTTO_DEVICE_URL'] = args.device_url
        (target / 'config.local.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
        runtime = target / 'runtime'
        runtime.mkdir()
        base = Path(sys.base_prefix)
        print('Copying standalone CPython...', flush=True)
        for source in base.iterdir():
            if source.is_file() and (source.suffix.lower() in {'.exe', '.dll'} or source.name == 'LICENSE.txt'):
                shutil.copy2(source, runtime / source.name)
        shutil.copytree(base / 'DLLs', runtime / 'DLLs', ignore=ignore)
        shutil.copytree(base / 'Lib', runtime / 'Lib', ignore=shutil.ignore_patterns('site-packages', '__pycache__', '*.pyc'))
        print('Copying installed dependencies (may take several minutes)...', flush=True)
        shutil.copytree(Path(sys.prefix) / 'Lib/site-packages', runtime / 'Lib/site-packages', ignore=ignore)
        # Native inference wheels need matching MSVC libraries beside python.exe.
        system32 = Path(os.environ['SystemRoot']) / 'System32'
        for name in ['msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll',
                     'msvcp140_atomic_wait.dll', 'msvcp140_codecvt_ids.dll',
                     'vcruntime140.dll', 'vcruntime140_1.dll', 'concrt140.dll']:
            source = system32 / name
            if source.is_file():
                shutil.copy2(source, runtime / name)
    if args.stage_only:
        print(f'Staged for verification: {target}', flush=True)
        return
    archive = target.parent / (target.name + '.zip')
    if archive.exists():
        raise FileExistsError(archive)
    print('Compressing handoff...', flush=True)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=3) as output:
        for path in target.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                output.write(path, path.relative_to(target.parent))
    print(f'Package ready: {archive} ({archive.stat().st_size / 1024**2:.1f} MiB)', flush=True)


if __name__ == '__main__':
    main()
