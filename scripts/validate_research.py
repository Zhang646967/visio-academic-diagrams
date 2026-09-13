#!/usr/bin/env python3
"""Validate paper/figure provenance and typed graph structure. Standard library only.

Not a paper reader, theorem prover, causal inference engine or Visio renderer.
JSON shape validation below supports only the subset used by our two shipped schemas.
It is deliberately not advertised as a general JSON Schema implementation.
"""
from __future__ import annotations
import argparse
from collections import defaultdict, deque
import json
from pathlib import Path
import sys
from typing import Any
from validate_spec import load_json

ROOT = Path(__file__).resolve().parents[1]
# A figure may qualify a statement, but must never strengthen its declared support.
SUPPORT_RANK = {'explicit': 0, 'inferred': 1, 'proposed': 2, 'unknown': 3}
MATCH = {
    'contains': 'hierarchy', 'is_a': 'hierarchy', 'precedes': 'control',
    'controls': 'control', 'uses': 'data', 'produces': 'data',
    'depends_on': 'dependency', 'associated_with': 'association',
    'causes': 'causal', 'supports': 'evidence', 'contradicts': 'evidence',
    'communicates_with': 'message'
}


def shape_errors(value: Any, schema: dict, path: str = '$') -> list[str]:
    """Validate the small JSON-Schema subset present in package model/plan schemas."""
    errors: list[str] = []
    types = schema.get('type')
    checks = {'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
              'string': lambda v: isinstance(v, str), 'boolean': lambda v: type(v) is bool,
              'null': lambda v: v is None}
    if types:
        allowed = [types] if isinstance(types, str) else types
        if not any(t in checks and checks[t](value) for t in allowed):
            return [f'{path}: expected {types}']
    if 'const' in schema and value != schema['const']:
        errors.append(f'{path}: expected constant {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: value is not in the allowed enumeration')
    if isinstance(value, str) and 'minLength' in schema and len(value.strip()) < schema['minLength']:
        errors.append(f'{path}: nonblank text required')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in value: errors.append(f'{path}.{key}: required')
        for key, v in value.items():
            if key in props: errors.extend(shape_errors(v, props[key], f'{path}.{key}'))
            elif schema.get('additionalProperties') is False: errors.append(f'{path}.{key}: unexpected property')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0): errors.append(f'{path}: too few entries')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            errors.append(f'{path}: duplicate values')
        for i, v in enumerate(value): errors.extend(shape_errors(v, schema.get('items', {}), f'{path}[{i}]'))
    return errors


def cycle(nodes: set[str], edges: list[tuple[str, str]]) -> bool:
    incoming = dict.fromkeys(nodes, 0); outgoing: dict[str, list[str]] = defaultdict(list)
    for a, b in edges:
        if a in nodes and b in nodes: incoming[b] += 1; outgoing[a].append(b)
    queue = deque(n for n in nodes if incoming[n] == 0); visited = 0
    while queue:
        a = queue.popleft(); visited += 1
        for b in outgoing[a]:
            incoming[b] -= 1
            if incoming[b] == 0: queue.append(b)
    return visited != len(nodes)


def validate(paper: Any, plan: Any | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []; warnings: list[dict[str, str]] = []
    def issue(code: str, message: str, item: str = '', warning: bool = False):
        (warnings if warning else errors).append({'code': code, 'item': item, 'message': message})
    def report():
        return {'ok': not errors, 'errors': errors, 'warnings': warnings,
                'scope': 'Structure and declared provenance only; does not verify truth, source entailment, full comprehension, or Visio rendering.'}
    schemas = [('paper-model', paper)] + ([('figure-plan', plan)] if plan is not None else [])
    for name, data in schemas:
        schema = load_json(ROOT / f'assets/{name}.schema.json')
        for msg in shape_errors(data, schema): issue('SCHEMA', msg, name)
    if errors: return report()
    def unique(sequence: list[dict], name: str) -> dict:
        result = {}
        for obj in sequence:
            if obj['id'] in result: issue('DUPLICATE_ID', f'Duplicate {name} ID', obj['id'])
            result[obj['id']] = obj
        return result
    evidence = unique(paper['evidence'], 'evidence')
    items = unique(paper['items'], 'item')
    relations = unique(paper['relations'], 'relation')
    if not any(c['status'] == 'read' for c in paper['coverage']):
        issue('NO_READ_COVERAGE', 'At least one actually read source section is required.')
    for group in ('items', 'relations'):
        for item in paper[group]:
            refs = item['evidence_ids']; status = item['support']
            if status in {'explicit', 'inferred'} and not refs:
                issue('EVIDENCE_REQUIRED', 'Explicit and inferred content must have evidence IDs.', item['id'])
            if status == 'inferred' and not item.get('rationale', '').strip():
                issue('INFERENCE_REASON', 'An inference requires a rationale.', item['id'])
            for ref in refs:
                if ref not in evidence: issue('UNKNOWN_EVIDENCE', 'Evidence ID does not exist.', item['id'])
                elif status in {'explicit', 'inferred'} and not evidence[ref]['available']:
                    issue('UNAVAILABLE_EVIDENCE', 'Unavailable source cannot ground an explicit/inferred statement.', item['id'])
    for rel in relations.values():
        if rel['from'] not in items or rel['to'] not in items:
            issue('RELATION_ENDPOINT', 'Paper relation references a missing item.', rel['id'])
    if plan is None: return report()
    if plan['paper_id'] != paper['paper']['id']: issue('PAPER_MISMATCH', 'Plan points to a different paper.')
    if paper['paper']['input_scope'] == 'abstract_only' and plan['detail_level'] == 'implementation':
        issue('ABSTRACT_IMPLEMENTATION', 'An abstract alone cannot ground implementation-level reconstruction.')
    if paper['paper']['source_status'] == 'synthetic' and not any(w in plan['caption'].lower() for w in ('synthetic','合成','虚构','教学')):
        issue('SYNTHETIC_DISCLOSURE', 'Caption must disclose synthetic/teaching source.')
    if paper['paper']['input_scope'] != 'full_text':
        issue('PARTIAL_SOURCE', 'Reading scope is not full text; do not claim complete reconstruction.', warning=True)
    if any(c['status'] != 'read' for c in paper['coverage']):
        issue('READING_GAPS', 'Some declared sections are unread/unavailable.', warning=True)
    nodes = unique(plan['nodes'], 'node'); edges = unique(plan['edges'], 'edge')
    represented = set(); disclosed = bool(plan['uncertainty_disclosure'].strip())
    for node in nodes.values():
        if node['role'] != 'organizer' and not node['item_ids']:
            issue('NODE_PROVENANCE', 'Scientific node requires a source item.', node['id'])
        if node['role'] == 'organizer' and node['support'] != 'proposed':
            issue('ORGANIZER_STATUS', 'A purely editorial grouping must be marked proposed.', node['id'])
        for ref in node['item_ids']:
            if ref not in items: issue('UNKNOWN_ITEM', 'Node references missing paper item.', node['id']); continue
            represented.add(ref)
            if SUPPORT_RANK[node['support']] < SUPPORT_RANK[items[ref]['support']]:
                issue('SUPPORT_UPGRADE', 'A figure cannot strengthen the declared source support.', node['id'])
            if items[ref]['support'] == 'unknown' and node['support'] != 'unknown':
                issue('UNKNOWN_DOWNPLAYED', 'Unknown paper content must remain visibly uncertain.', node['id'])
        if node['support'] != 'explicit' and not disclosed:
            issue('UNCERTAINTY_DISCLOSURE', 'Non-explicit content requires a user-visible disclosure.', node['id'])
    for ref in plan['must_keep_item_ids']:
        if ref not in items: issue('UNKNOWN_REQUIRED_ITEM', 'Required item is not in paper.', ref)
        elif ref not in represented: issue('MISSING_REQUIRED_ITEM', 'Required item was omitted from this figure.', ref)
    omitted = set()
    for omission in plan['omissions']:
        ref = omission['item_id']
        if ref in omitted: issue('DUPLICATE_OMISSION', 'Duplicate omission.', ref)
        omitted.add(ref)
        if ref not in items: issue('UNKNOWN_OMISSION', 'Omission item is unknown.', ref)
        if ref in represented: issue('OMITTED_BUT_PRESENT', 'Item is both shown and omitted.', ref)
    # Figure boundaries must be inspectable, not silently lossy.
    for ref in sorted(set(items) - represented - omitted):
        issue('UNACCOUNTED_ITEM', 'Item is neither shown nor explicitly excluded for this figure.', ref, True)
    valid_edges = []
    for edge in edges.values():
        if edge['from'] not in nodes or edge['to'] not in nodes:
            issue('EDGE_ENDPOINT', 'Figure edge has missing endpoint.', edge['id']); continue
        valid_edges.append(edge)
        if edge['kind'] not in {'control','hierarchy'} and not edge['label'].strip():
            issue('RELATION_LABEL', 'Non-control/non-hierarchy edge needs a relation label.', edge['id'])
        refs = edge['source_relation_ids']
        editorial = (edge['kind'] == 'hierarchy' and edge['support'] == 'proposed')
        if not refs and not editorial:
            issue('EDGE_PROVENANCE', 'A scientific edge needs a paper relation; editorial hierarchy is the only exception.', edge['id'])
        if edge['support'] != 'explicit' and not disclosed:
            issue('UNCERTAINTY_DISCLOSURE', 'Uncertain/proposed edge needs disclosure.', edge['id'])
        for ref in refs:
            rel = relations.get(ref)
            if not rel: issue('UNKNOWN_RELATION', 'Source relation is missing.', edge['id']); continue
            if MATCH[rel['kind']] != edge['kind']:
                issue('SEMANTIC_CAST', 'Figure edge changes the scientific relation type.', edge['id'])
            if SUPPORT_RANK[edge['support']] < SUPPORT_RANK[rel['support']]:
                issue('SUPPORT_UPGRADE', 'Figure edge strengthens source certainty.', edge['id'])
            a, b = (rel['to'], rel['from']) if edge.get('reverse_relation', False) else (rel['from'], rel['to'])
            if a not in nodes[edge['from']]['item_ids'] or b not in nodes[edge['to']]['item_ids']:
                issue('RELATION_DIRECTION', 'Figure direction/endpoints do not match source relation mapping.', edge['id'])
            if rel['support'] == 'unknown' and edge['support'] != 'unknown':
                issue('UNKNOWN_DOWNPLAYED', 'Unknown relation must remain unknown.', edge['id'])
    graph = plan['graph_type']; pairs = lambda kind: [(e['from'],e['to']) for e in valid_edges if e['kind'] == kind]
    if graph == 'mindmap':
        root = plan['root_id']; tree = pairs('hierarchy'); incoming = dict.fromkeys(nodes, 0)
        for _, b in tree: incoming[b] += 1
        if root not in nodes: issue('ROOT', 'Mindmap needs a declared existing root.')
        if root in nodes and incoming[root] != 0: issue('ROOT_PARENT', 'Root cannot have a hierarchical parent.')
        for nid in nodes:
            if nid != root and incoming[nid] != 1: issue('TREE_PARENT', 'Every nonroot mindmap node needs exactly one parent.', nid)
        if cycle(set(nodes), tree): issue('HIERARCHY_CYCLE', 'Hierarchy must be acyclic.')
        if any(e['kind'] not in {'hierarchy', 'association'} for e in valid_edges):
            issue('MINDMAP_EDGE_KIND', 'Mindmap supports hierarchy plus labelled association; choose a different view for other relations.')
    if graph == 'proof_map' and cycle(set(nodes), pairs('dependency')):
        issue('PROOF_CYCLE', 'Proof dependency graph cannot be circular.')
    if graph == 'causal_dag' and cycle(set(nodes), pairs('causal')):
        issue('CAUSAL_CYCLE', 'A causal DAG cannot contain a directed causal cycle.')
    if graph in {'flowchart', 'swimlane'}:
        for nid, node in nodes.items():
            if node['role'] == 'decision':
                out = [e for e in valid_edges if e['from'] == nid and e['kind'] == 'control']
                labels = [e['label'].strip().casefold() for e in out]
                if len(labels) < 2 or any(not s for s in labels) or len(set(labels)) != len(labels):
                    issue('DECISION_BRANCHES', 'Decision requires at least two distinct labelled control exits.', nid)
    caps = {c['id']: c for c in load_json(ROOT/'assets/capabilities.json')['capabilities']}
    for cid in plan['capability_ids']:
        if cid not in caps: issue('UNKNOWN_CAPABILITY', 'Unknown Visio capability.', cid)
        elif caps[cid]['lifecycle'] == 'retired': issue('RETIRED_CAPABILITY', 'Do not base new construction on retired functionality.', cid)
        elif caps[cid]['status'] == 'index-only':
            issue('CAPABILITY_REQUIRES_LOOKUP', 'Read a precise source before giving menu instructions.', cid, True)
    return report()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('paper', type=Path); p.add_argument('plan', type=Path, nargs='?')
    a = p.parse_args()
    try: result = validate(load_json(a.paper), load_json(a.plan) if a.plan else None)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'Input error: {exc}', file=sys.stderr); return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__': raise SystemExit(main())
