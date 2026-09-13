#!/usr/bin/env python3
"""Cross-check a paper model, figure plan and nominal layout for drift."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from typing import Any
from validate_research import validate as validate_research
from validate_spec import validate as validate_geometry, load_json


def validate(paper: Any, plan: Any, layout: Any) -> dict:
    research = validate_research(paper, plan); geometry = validate_geometry(layout)
    errors = research['errors'] + geometry['errors']; warnings = research['warnings'] + geometry['warnings']
    def issue(code, message, item=''): errors.append(dict(code=code, message=message, item=item))
    if not research['ok'] or not geometry['ok']:
        return dict(ok=False,errors=errors,warnings=warnings,scope='Model, plan and nominal geometry; not rendered Visio.')
    if layout.get('figure_plan_id') != plan['figure_id']: issue('PLAN_ID','Layout points to a different figure plan.')
    expected = {'flowchart': {'flowchart','algorithm'}, 'swimlane': {'swimlane'}}.get(plan['graph_type'], {plan['graph_type']})
    if layout['diagram_type'] not in expected: issue('GRAPH_KIND_DRIFT','Layout has a different graph kind.')
    pn={n['id']:n for n in plan['nodes']};ln={n['id']:n for n in layout['nodes']}
    pe={e['id']:e for e in plan['edges']};le={e['id']:e for e in layout['edges']}
    if set(pn)!=set(ln): issue('NODE_SET_DRIFT','Plan and layout node IDs differ.')
    if set(pe)!=set(le): issue('EDGE_SET_DRIFT','Plan and layout edge IDs differ.')
    def norm(s): return ' '.join(s.split())
    for nid in set(pn)&set(ln):
        if norm(pn[nid]['label'])!=norm(ln[nid]['label']): issue('LABEL_DRIFT','Layout changed a node label.',nid)
        role=pn[nid]['role'];allowed={'topic','container','annotation'} if role=='organizer' else {role}
        if ln[nid]['type'] not in allowed: issue('NODE_ROLE_DRIFT','Layout shape role differs from semantic plan.',nid)
    for eid in set(pe)&set(le):
        p,e=pe[eid],le[eid]
        if (p['from'],p['to'])!=(e['from'],e['to']): issue('EDGE_DRIFT','Layout rewired a semantic edge.',eid)
        if norm(p['label'])!=norm(e['label']): issue('EDGE_LABEL_DRIFT','Layout changed a relation or condition.',eid)
        if p['kind'] in {'association','hierarchy'} and e.get('arrow','end')!='none':
            issue('UNDIRECTED_ARROW','This profile uses no arrowheads for hierarchy/association.',eid)
        if p['kind'] in {'control','causal','dependency','data','message','evidence'} and e.get('arrow','end')!='end':
            issue('DIRECTED_ARROW','Declared directed relations need an end arrow.',eid)
    return dict(ok=not errors,errors=errors,warnings=warnings,scope='ID, label, role, direction and nominal geometry; not actual Visio text, glue or scientific entailment.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('paper','plan','layout'): p.add_argument(name,type=Path)
    a=p.parse_args()
    try:r=validate(*(load_json(getattr(a,n)) for n in ('paper','plan','layout')))
    except (OSError,ValueError,UnicodeError) as exc: print(f'Input error: {exc}',file=sys.stderr);return 2
    print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['ok'] else 1
if __name__=='__main__': raise SystemExit(main())
