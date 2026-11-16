#!/usr/bin/env python3
"""Enable autonomous trading config without touching secrets or trading state."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile


def configure(path, autonomous=True):
    path = Path(path)
    original = path.read_bytes() if path.exists() else None
    if original is None:
        template = Path(__file__).resolve().parent / 'trader-budget' / 'config.example.json'
        cfg = json.loads(template.read_text(encoding='utf-8'))
    else:
        cfg = json.loads(original.decode('utf-8'))
    if not isinstance(cfg, dict):
        raise ValueError('config must be a JSON object')
    cfg['autonomous'] = autonomous
    data = (json.dumps(cfg, indent=2) + '\n').encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if original is not None and cfg == json.loads(original.decode('utf-8')):
        return None
    if original is not None:
        fd, name = tempfile.mkstemp(prefix=path.name + '.backup-', dir=str(path.parent))
        backup = Path(name)
        with os.fdopen(fd, 'wb') as fh:
            fh.write(original)
    fd, name = tempfile.mkstemp(prefix=path.name + '.tmp-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(data)
        if original is not None:
            shutil.copymode(str(path), name)
        os.replace(name, str(path))
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='trader/config.json')
    parser.add_argument('--manual', action='store_true', help='explicitly select manual confirmation')
    args = parser.parse_args(argv)
    try:
        backup = configure(args.config, not args.manual)
    except (OSError, ValueError) as exc:
        # Parsing errors may contain sensitive config excerpts; do not echo them.
        print('Configuration failed (%s). Check the path and JSON locally.' % type(exc).__name__)
        return 1
    print('Manual confirmation selected.' if args.manual else 'Autonomous execution enabled.')
    print('Existing risk limits, broker and paper/live settings preserved; new configs default to paper.')
    if backup:
        print('Original config backed up beside the active config. Keep backups private.')
    print('Next: follow SETUP.md to configure broker tools and reload the agent host.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
