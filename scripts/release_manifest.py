#!/usr/bin/env python3
"""Shared strict manifest reader for packaging and publication (no network)."""
from __future__ import annotations
import hashlib
from pathlib import Path, PurePosixPath
import re


def read_manifest(root: Path) -> list[str]:
    root = root.resolve()
    entries: list[str] = []
    for line in (root/'manifest.sha256').read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        parts = line.split('  ', 1)
        if len(parts) != 2 or not re.fullmatch(r'[a-f0-9]{64}', parts[0]):
            raise ValueError('Malformed manifest line')
        expected, relative = parts
        rel = PurePosixPath(relative)
        if rel.is_absolute() or '..' in rel.parts or '\\' in relative or ':' in relative:
            raise ValueError(f'Unsafe manifest path: {relative}')
        if any(part in {'.git', '__pycache__', '.env'} for part in rel.parts):
            raise ValueError(f'Private/runtime path in manifest: {relative}')
        if relative in entries or relative == 'manifest.sha256':
            raise ValueError(f'Duplicate or self-referencing manifest path: {relative}')
        path = root / relative
        # Reject symlinks in any path component, even if they resolve inside root.
        if any((root/Path(*rel.parts[:i])).is_symlink() for i in range(1, len(rel.parts)+1)):
            raise ValueError(f'Symlink is not publishable: {relative}')
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError(f'Missing/escaping manifest target: {relative}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Hash mismatch: {relative}')
        entries.append(relative)
    if not entries: raise ValueError('Manifest is empty')
    if 'SKILL.md' not in entries or 'README.md' not in entries:
        raise ValueError('Manifest lacks SKILL.md or README.md')
    return entries
