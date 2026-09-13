#!/usr/bin/env python3
"""Local integrity checks only; no network and no changes to package files."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote
from release_manifest import read_manifest


def check(root: Path) -> dict:
    root=root.resolve();errors=[]
    required=['README.md','README.en.md','LICENSE','SECURITY.md','CONTRIBUTING.md',
              'assets/paper-model.schema.json','assets/figure-plan.schema.json','assets/feature-families.json',
              'scripts/validate_research.py','scripts/validate_bundle.py','tests/test_research.py',
              'SKILL.md','README.zh-CN.md','references/INDEX.md','references/environment.md',
              'references/source-register.md','assets/sources.json','assets/capabilities.json',
              'assets/diagram-spec.schema.json','examples/iterative-optimization/diagram-spec.json',
              'scripts/validate_spec.py','tests/test_validate.py']
    for relative in required:
        p=root/relative
        if not p.is_file() or p.stat().st_size==0:
            errors.append(f'Missing/empty required file: {relative}')
    if errors:
        return {'ok':False,'errors':errors}
    text=(root/'SKILL.md').read_text(encoding='utf-8')
    match=re.match(r'^---\n(.*?)\n---\n',text,re.S)
    if not match:
        errors.append('SKILL.md lacks YAML frontmatter.')
    else:
        fields={m.group(1):m.group(2).strip('"\'') for m in re.finditer(r'^(name|description):\s*(.+)$',match.group(1),re.M)}
        name=fields.get('name','')
        if name!=root.name or len(name)>64 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name):
            errors.append('Skill name is invalid or does not match folder.')
        if not 1<=len(fields.get('description',''))<=1024:
            errors.append('Skill description length invalid.')
    if len(text.splitlines())>500:
        errors.append('SKILL.md exceeds the package 500-line limit.')
    for p in root.rglob('*.json'):
        if '.git' in p.parts or '__pycache__' in p.parts: continue
        try:
            json.loads(p.read_text(encoding='utf-8'))
        except (ValueError,UnicodeError) as exc:
            errors.append(f'Invalid JSON {p.relative_to(root)}: {exc}')
    if errors:
        return {'ok':False,'errors':errors}
    sources=json.loads((root/'assets/sources.json').read_text())['sources']
    ids=[s['id'] for s in sources]
    if len(ids)!=len(set(ids)):
        errors.append('Duplicate source ids.')
    for s in sources:
        if not s['url'].startswith('https://'):
            errors.append(f"Source URL not https: {s['id']}")
        if s.get('gui_tested') is not False:
            errors.append(f"Unsubstantiated GUI-test flag: {s['id']}")
    caps=json.loads((root/'assets/capabilities.json').read_text())['capabilities']
    if len({c['id'] for c in caps})!=len(caps):
        errors.append('Duplicate capability ids.')
    families=json.loads((root/'assets/feature-families.json').read_text(encoding='utf-8'))['families']
    family_ids=[f['id'] for f in families]
    if len(family_ids)!=len(set(family_ids)): errors.append('Duplicate feature-family IDs.')
    for f in families:
        for sid in f['source_ids']:
            if sid not in ids: errors.append(f'Unknown family source: {sid}')
    for c in caps:
        if c.get('family') not in family_ids: errors.append(f"Unknown capability family: {c['id']}")
        if c.get('runtime_tested') is not False: errors.append(f"Unsubstantiated runtime-test flag: {c['id']}")
        if c.get('status') not in {'document-backed','index-only'}: errors.append(f"Unknown capability status: {c['id']}")
        path=root/c['module']
        if not path.is_file():
            errors.append(f"Missing capability module: {c['id']}")
        elif c['id'] not in path.read_text(encoding='utf-8'):
            errors.append(f"Capability id absent from module: {c['id']}")
        for sid in c['source_ids']:
            if sid not in ids:
                errors.append(f'Unknown capability source: {sid}')
    local_links=0
    for p in root.rglob('*.md'):
        if '.git' in p.parts or '__pycache__' in p.parts: continue
        txt=p.read_text(encoding='utf-8')
        for sid in re.findall(r'\[([MAPR]\d{2})\]',txt):
            if sid not in ids:
                errors.append(f'Unknown source {sid} in {p.relative_to(root)}')
        # Relative file links checked. Section anchors and live URL reachability not checked.
        for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',txt):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):
                continue
            target=unquote(target.split('#',1)[0])
            q=(p.parent/target).resolve();local_links+=1
            if not q.is_relative_to(root) or not q.exists():
                errors.append(f'Broken/escaping link in {p.relative_to(root)}: {target}')
    manifest=root/'manifest.sha256'
    if manifest.exists():
        try:
            listed=read_manifest(root)
            current={p.relative_to(root).as_posix() for p in root.rglob('*')
                     if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix!='.pyc'}
            extras=current-set(listed)-{'manifest.sha256'}
            if extras: errors.append('Unlisted release files: '+', '.join(sorted(extras)))
        except (OSError,ValueError) as exc: errors.append(str(exc))
    files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.suffix!='.pyc']
    return {'ok':not errors,'errors':errors,'file_count':len(files),
            'feature_family_count':len(families),'source_count':len(sources),'capability_count':len(caps),
            'document_backed_count':sum(c['status']=='document-backed' for c in caps),
            'index_only_count':sum(c['status']=='index-only' for c in caps),
            'local_links_checked':local_links,'skill_lines':len(text.splitlines()),
            'scope':'Local structure, links, source ids and optional hashes; not live URLs, GUI, or all Agent Skills host behaviors.'}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();report=check(args.root)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
