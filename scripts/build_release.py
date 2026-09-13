#!/usr/bin/env python3
"""Build a ZIP from the reviewed manifest. Does not discover files or refresh hashes.

The manifest is an explicit release allowlist. Updating a release requires a human
review of the intended files and regeneration of their hashes, not blind inclusion
of everything in a research workspace.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import zipfile
from release_manifest import read_manifest

ROOT = Path(__file__).resolve().parents[1]


def build(root: Path, output: Path) -> int:
    files = read_manifest(root) + ['manifest.sha256']
    output = output.resolve()
    if output.is_relative_to(root.resolve()):
        raise ValueError('Place the release archive outside the skill directory.')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects an existing release.
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in sorted(files):
            info = zipfile.ZipInfo('visio-academic-diagrams/' + rel, date_time=(2026,9,12,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root/rel).read_bytes())
    return len(files)


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    a=p.parse_args()
    try: count=build(ROOT,a.output)
    except (OSError,ValueError,zipfile.BadZipFile) as exc: p.error(str(exc))
    print(f'Created {a.output} with {count} allowlisted files. No remote upload performed.')
    return 0
if __name__ == '__main__': raise SystemExit(main())
