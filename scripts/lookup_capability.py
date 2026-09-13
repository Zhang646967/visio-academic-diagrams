#!/usr/bin/env python3
"""Offline search of documented capabilities and official-document lookup routes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    '思维导图': ['mindmap', 'brainstorming'], '脑图': ['mindmap', 'brainstorming'],
    'mind map': ['mindmap', 'brainstorming'], 'mindmap': ['mindmap', 'brainstorming'],
    'shapesheet': ['shapesheet'], '形状表': ['shapesheet'],
    '流程图': ['flow', 'flowchart'], 'flowchart': ['flow', '流程'],
    '数据': ['data', 'datagraphics'], 'data visualizer': ['data visualizer', 'lifecycle'],
    '退役': ['lifecycle', 'retirement'], '退休': ['lifecycle', 'retirement'],
    '字体': ['text', 'font'], '导出': ['interop', 'export'],
    '连接线': ['connectors', 'connector'], '容器': ['structure', 'container'],
    '图层': ['structure', 'layer'], '时间线': ['timeline', 'project'],
    '证明': ['dependency', 'proof'], '论文': ['research'], '网页': ['web'],
}


def search(query: str, *, family: str | None = None, status: str | None = None,
           limit: int = 10, root: Path = ROOT) -> list[dict]:
    if not query.strip() and not family and not status:
        raise ValueError('Provide a query, family or status.')
    if not 1 <= limit <= 220:
        raise ValueError('limit must be between 1 and 220')
    entries = json.loads((root/'assets/capabilities.json').read_text(encoding='utf-8'))['capabilities']
    q = query.strip().casefold()
    tokens = set(re.findall(r'[a-z0-9_]+|[\u4e00-\u9fff]+', q))
    for key, aliases in ALIASES.items():
        if key in q: tokens.update(aliases)
    ranked = []
    for cap in entries:
        if family and cap['family'] != family: continue
        if status and cap['status'] != status: continue
        text = ' '.join([cap['title'], cap['family'], cap['official_query'],
                         cap['research_use'], *cap.get('keywords', [])]).casefold()
        score = sum(2 for token in tokens if token in text)
        if q and q == cap['id'].casefold(): score += 100
        if q and q in cap['title'].casefold(): score += 15
        if cap['family'] in tokens: score += 8
        if q and score == 0: continue
        ranked.append((score, cap['id'], cap))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return [dict(score=score, **cap) for score, _, cap in ranked[:limit]]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('query', nargs='?', default='')
    p.add_argument('--family'); p.add_argument('--status', choices=['document-backed', 'index-only'])
    p.add_argument('--limit', type=int, default=10); p.add_argument('--json', action='store_true')
    a = p.parse_args()
    try: result = search(a.query, family=a.family, status=a.status, limit=a.limit)
    except (OSError, ValueError) as exc: p.error(str(exc))
    if a.json: print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for cap in result:
            print(f"{cap['id']} | {cap['title']} | {cap['status']} | {cap['lifecycle']}")
            print(f"  Module: {cap['module']}; sources: {', '.join(cap['source_ids'])}")
            print(f"  Official lookup: {cap['official_query']}")
            print('  GUI not tested; index-only entries require precise official lookup.')
        if not result: print('No match. Try another term or --family.')
    return 0
if __name__ == '__main__': raise SystemExit(main())
