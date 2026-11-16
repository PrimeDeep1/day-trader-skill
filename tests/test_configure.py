import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from _load import ROOT

spec = importlib.util.spec_from_file_location('configure', str(Path(ROOT) / 'configure.py'))
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class Configuration(unittest.TestCase):
    def test_new_setup_defaults_to_autonomous_paper(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'trader' / 'config.json'
            setup.configure(path)
            cfg = json.loads(path.read_text())
            self.assertIs(cfg['autonomous'], True)
            self.assertIs(cfg['paper'], True)
            self.assertEqual(cfg['broker'], 'alpaca')

    def test_existing_config_and_private_state_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'config.json'
            original = b'{"paper":false,"budget":123,"custom":{"nested":42},"autonomous":false}'
            path.write_bytes(original)
            secret = root / '.env'
            state = root / 'broker.json'
            secret.write_bytes(b'PRIVATE_PLACEHOLDER')
            state.write_bytes(b'{"orders":[{"status":"placed"}]}')
            backup = setup.configure(path)
            self.assertEqual(backup.read_bytes(), original)
            expected = json.loads(original)
            expected['autonomous'] = True
            self.assertEqual(json.loads(path.read_bytes()), expected)
            self.assertEqual(secret.read_bytes(), b'PRIVATE_PLACEHOLDER')
            self.assertEqual(state.read_bytes(), b'{"orders":[{"status":"placed"}]}')
            before = path.read_bytes()
            self.assertIsNone(setup.configure(path))
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(len(list(root.glob('*.backup-*'))), 1)
            setup.configure(path, False)
            self.assertIs(json.loads(path.read_bytes())['autonomous'], False)

    def test_invalid_config_is_left_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.json'
            for original in (b'not json', b'[]'):
                path.write_bytes(original)
                with self.assertRaises(ValueError):
                    setup.configure(path)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(list(path.parent.glob('*.backup-*')), [])
