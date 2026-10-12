import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release_models', ROOT / 'tools/download_models.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseModelTests(unittest.TestCase):
    def make_archive(self, root, files):
        path = root / 'models.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_requested_model_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, digest = self.make_archive(root, {'models/a.bin': 'gesture', 'voice-model/base/model.bin': 'voice'})
            module.install_models(archive, root / 'output', 'gesture', digest)
            self.assertEqual((root / 'output/models/a.bin').read_text(), 'gesture')
            self.assertFalse((root / 'output/voice-model').exists())

    def test_bad_checksum_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, _ = self.make_archive(root, {'models/a.bin': 'gesture'})
            with self.assertRaises(ValueError):
                module.install_models(archive, root / 'output', 'all', '0' * 64)
            self.assertFalse((root / 'output').exists())

    def test_cannot_escape_model_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, digest = self.make_archive(root, {'models/a.bin': 'gesture', 'models/../web/server.py': 'bad'})
            with self.assertRaises(ValueError):
                module.install_models(archive, root / 'output', 'all', digest)
            self.assertFalse((root / 'output').exists())


if __name__ == '__main__':
    unittest.main()
