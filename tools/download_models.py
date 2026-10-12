"""Install the tested models from this repository's GitHub Release."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def install_models(archive, destination, kind, digest):
    with archive.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
            raise ValueError('Model archive SHA256 mismatch; download it again')
    allowed = ('models/', 'voice-model/') if kind == 'all' else (('models/',) if kind == 'gesture' else ('voice-model/',))
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as package:
        members = []
        for info in package.infolist():
            if not info.filename.startswith(allowed) or info.is_dir():
                continue
            target = (destination / info.filename).resolve()
            if not any(target.is_relative_to(destination / prefix) for prefix in allowed):
                raise ValueError('Invalid model archive path')
            members.append((info, target))
        if not members:
            raise ValueError('Requested model is missing from the archive')
        for info, target in members:
            target.parent.mkdir(parents=True, exist_ok=True)
            with package.open(info) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=['gesture', 'voice', 'all'], default='all')
    parser.add_argument('--archive', type=Path, help='Use an already downloaded release ZIP')
    args = parser.parse_args()
    asset = json.loads((ROOT / 'release-assets.json').read_text(encoding='utf-8'))['models']
    archive = args.archive or ROOT / '.downloads' / asset['name']
    if not archive.exists():
        if args.archive:
            raise FileNotFoundError(archive)
        archive.parent.mkdir(parents=True, exist_ok=True)
        partial = archive.with_suffix('.download')
        print('Downloading the tested gesture and voice models from GitHub...', flush=True)
        try:
            with urllib.request.urlopen(asset['url'], timeout=120) as source, partial.open('wb') as target:
                shutil.copyfileobj(source, target)
            partial.replace(archive)
        finally:
            partial.unlink(missing_ok=True)
    install_models(archive, ROOT, args.kind, asset['sha256'])
    print('Model installation complete:', args.kind)


if __name__ == '__main__':
    main()
