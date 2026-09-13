#!/usr/bin/env python3
"""Publish only this reviewed release as a NEW public GitHub repository.

Dry run is the default. --execute performs network writes using the user's locally
authenticated GitHub CLI. Never reads tokens itself, force-pushes, deletes a repo,
or adds files from the user's existing working tree. Live publishing is untested.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from release_manifest import read_manifest
from validate_package import check

ROOT = Path(__file__).resolve().parents[1]


def run(argv: list[str], cwd: Path | None = None) -> str:
    # argv list, no shell; credentials remain within gh/git credential handling.
    p=subprocess.run(argv, cwd=cwd, text=True, encoding='utf-8', errors='replace',
                     capture_output=True, check=False)
    if p.returncode:
        raise RuntimeError(f'{argv[0]} command failed: {p.stderr.strip() or p.stdout.strip()}')
    return p.stdout.strip()


def valid_names(owner: str, repo: str) -> None:
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', owner):
        raise ValueError('Invalid owner login')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', repo):
        raise ValueError('Invalid repository name')


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner',required=True)
    p.add_argument('--repo',default='visio-academic-diagrams')
    p.add_argument('--public',action='store_true',help='Required acknowledgment of public visibility')
    p.add_argument('--execute',action='store_true',help='Actually create and push (default: dry run)')
    a=p.parse_args()
    try:
        valid_names(a.owner,a.repo)
        files=read_manifest(ROOT)
        report=check(ROOT)
        if not report['ok']: raise ValueError('Package validation failed: '+ '; '.join(report['errors']))
        print(f'Reviewed release: {len(files)+1} files; target {a.owner}/{a.repo}; public.')
        print('Only the manifest-listed release files will be copied; other workspace files are excluded.')
        if not a.execute:
            print('DRY RUN: no network calls, account changes, repository creation or upload.')
            print('Review the files, authenticate gh locally, then rerun with --public --execute.')
            return 0
        if not a.public: raise ValueError('Explicit --public is required before publishing.')
        for tool in ('gh','git'):
            if not shutil.which(tool): raise ValueError(f'{tool} is not installed on this machine.')
        profile=json.loads(run(['gh','api','user','--jq','{login: .login, id: .id}']))
        login=profile.get('login','');uid=profile.get('id')
        if login.casefold()!=a.owner.casefold():
            raise ValueError(f'Authenticated account is {login}, not requested owner {a.owner}; no changes made.')
        if not isinstance(uid,int): raise ValueError('Could not verify authenticated GitHub user ID.')
        # A fresh isolated worktree prevents accidental publication of private research.
        with tempfile.TemporaryDirectory(prefix='visio-skill-public-') as td:
            staging=Path(td)
            for rel in files+['manifest.sha256']:
                dest=staging/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/rel,dest)
            run(['git','init','-b','main'],staging)
            run(['git','config','user.name',login],staging)
            run(['git','config','user.email',f'{uid}+{login}@users.noreply.github.com'],staging)
            run(['git','add','--all'],staging)  # isolated, allowlisted temp directory only
            run(['git','commit','-m','Release Visio Academic Diagrams v0.2.0'],staging)
            expected=run(['git','rev-parse','HEAD'],staging)
            target=f'{a.owner}/{a.repo}'
            # Atomic create: an existing repository causes gh to fail; it is never reused.
            try:
                run(['gh','repo','create',target,'--public','--source',str(staging),
                     '--remote','origin','--push','--description',
                     'Evidence-linked paper understanding and Microsoft Visio research-diagram skills'],staging)
            except RuntimeError as exc:
                raise RuntimeError(str(exc)+'\nA partial repository may have been created. Inspect GitHub; this script will not delete or overwrite it.')
            metadata=json.loads(run(['gh','repo','view',target,'--json','nameWithOwner,url,isPrivate']))
            actual=run(['gh','api',f'repos/{target}/commits/main','--jq','.sha'])
            if metadata.get('isPrivate') is not False or actual!=expected:
                raise RuntimeError('Post-upload visibility/commit verification failed. Inspect the remote repository.')
            print('PUBLISHED AND VERIFIED: '+ metadata['url'])
            print('Commit: '+actual)
        return 0
    except (OSError,ValueError,RuntimeError) as exc:
        print(f'Publication not confirmed: {exc}')
        return 1

if __name__=='__main__': raise SystemExit(main())
