"""Export/import local audio and behavior files without embedding them in Git."""
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ('web/library/audio/', 'web/behaviors/')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['export', 'import'])
    parser.add_argument('archive', type=Path)
    parser.add_argument('--source', type=Path, default=ROOT, help='Project root for export')
    args = parser.parse_args()
    if args.mode == 'export':
        with zipfile.ZipFile(args.archive, 'w', zipfile.ZIP_DEFLATED) as archive:
            for prefix in PREFIXES:
                for path in (args.source / prefix).rglob('*'):
                    if path.is_file():
                        archive.write(path, path.relative_to(args.source).as_posix())
    else:
        with zipfile.ZipFile(args.archive) as archive:
            members = archive.infolist()
            for item in members:
                target = (ROOT / item.filename).resolve()
                if not item.filename.startswith(PREFIXES) or not any(target.is_relative_to((ROOT / prefix).resolve()) for prefix in PREFIXES):
                    raise ValueError('Invalid resource archive path')
                if target.exists():
                    raise FileExistsError(f'Refusing to overwrite {target}')
            for item in members:
                archive.extract(item, ROOT)
    print('Resource archive complete')

if __name__ == '__main__':
    main()
