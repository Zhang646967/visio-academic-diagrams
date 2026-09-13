#!/usr/bin/env python3
"""Dependency-free static checks for a Visio design specification (Python 3.10+).

This does NOT open Visio or validate VSDX/PDF, glyph metrics, endpoint glue,
scientific correctness, algorithm termination, or complete journal compliance.
Run: python scripts/validate_spec.py path/to/diagram-spec.json
Exit codes: 0 no errors (warnings allowed), 1 validation errors, 2 input errors.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

TYPES = {'start', 'end', 'process', 'decision', 'input_output', 'subprocess',
         'data_store', 'component', 'container', 'annotation', 'topic', 'concept', 'claim', 'assumption', 'evidence'}
DIAGRAMS = {'algorithm', 'flowchart', 'pipeline', 'architecture', 'dfd',
            'uml', 'bpmn', 'er', 'methodology', 'mindmap', 'concept_map', 'evidence_map', 'proof_map', 'causal_dag', 'timeline', 'swimlane'}
PORTS = {'north', 'south', 'east', 'west', 'auto'}


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def choice(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def box(node: dict[str, Any]) -> tuple[float, float, float, float]:
    return (node['x_mm'] - node['width_mm'] / 2, node['y_mm'] - node['height_mm'] / 2,
            node['x_mm'] + node['width_mm'] / 2, node['y_mm'] + node['height_mm'] / 2)


def segment_crosses_box(a: list[float], b: list[float], bounds: tuple[float, ...]) -> bool:
    """Test intersection with the interior of an axis-aligned box (not mere touch)."""
    eps = 1e-7
    xmin, ymin, xmax, ymax = bounds
    limits = ((xmin + eps, xmax - eps), (ymin + eps, ymax - eps))
    lower, upper = 0.0, 1.0
    for dim, (lo, hi) in enumerate(limits):
        if lo >= hi:
            return False
        delta = b[dim] - a[dim]
        if abs(delta) < 1e-12:
            if not lo <= a[dim] <= hi:
                return False
        else:
            t1, t2 = (lo - a[dim]) / delta, (hi - a[dim]) / delta
            lower = max(lower, min(t1, t2))
            upper = min(upper, max(t1, t2))
            if lower > upper:
                return False
    return upper >= lower


def validate(spec: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    metrics: dict[str, Any] = {}
    def issue(code: str, message: str, item: str = '', warning: bool = False) -> None:
        (warnings if warning else errors).append({'code': code, 'item': item, 'message': message})
    def result() -> dict[str, Any]:
        return {'ok': not errors, 'errors': errors, 'warnings': warnings, 'metrics': metrics,
                'scope': 'Static JSON and nominal geometry only; no Visio rendering or journal certification.'}
    if not isinstance(spec, dict):
        issue('ROOT_TYPE', 'Specification must be a JSON object.')
        return result()
    if not choice(spec.get('schema_version'), {'1.0', '1.1'}):
        issue('SCHEMA_VERSION', 'Only schema_version 1.0 and 1.1 are supported.')
    if not isinstance(spec.get('title'), str) or not spec['title'].strip():
        issue('TITLE', 'A nonempty title is required.')
    if not choice(spec.get('diagram_type'), DIAGRAMS):
        issue('DIAGRAM_TYPE', 'Unknown diagram_type.')
    objects: dict[str, dict[str, Any]] = {}
    for key in ('canvas', 'style', 'publication', 'environment'):
        if not isinstance(spec.get(key), dict):
            issue('SECTION_TYPE', f'{key} must be an object.', key)
        else:
            objects[key] = spec[key]
    if len(objects) < 4:
        return result()
    canvas, style, publication, environment = (objects[k] for k in ('canvas', 'style', 'publication', 'environment'))
    numeric = ((canvas, 'width_mm', 'canvas', True), (canvas, 'height_mm', 'canvas', True),
               (canvas, 'margin_mm', 'canvas', False), (style, 'font_pt', 'style', True),
               (style, 'line_pt', 'style', True), (publication, 'final_width_mm', 'publication', True))
    for obj, field, parent, positive in numeric:
        v = obj.get(field)
        if not is_number(v) or (v <= 0 if positive else v < 0):
            issue('NUMBER', f'{field} must be finite and {"positive" if positive else "nonnegative"}.', parent)
    if errors and any(e['code'] == 'NUMBER' for e in errors):
        return result()
    width, height, margin = canvas['width_mm'], canvas['height_mm'], canvas['margin_mm']
    if 2 * margin >= min(width, height):
        issue('MARGIN', 'Margins leave no usable drawing area.')
    if not isinstance(style.get('font_family'), str) or not style['font_family'].strip():
        issue('FONT_FAMILY', 'Specify the intended font family, not a bundled font file.')
    if environment.get('coordinate_origin') != 'bottom-left' or environment.get('pin') != 'center':
        issue('COORDINATE_SYSTEM', 'Only bottom-left origin with center pins is supported.')
    if not is_number(environment.get('drawing_scale')) or environment['drawing_scale'] != 1:
        issue('DRAWING_SCALE', 'Only unscaled 1:1 drawings are supported.')
    if publication.get('uniform_scale') is not True:
        issue('NONUNIFORM_SCALE', 'Final size checks require uniform_scale=true and no unrecorded crop.')
    dpi = publication.get('raster_dpi')
    if dpi is not None and (not is_number(dpi) or dpi <= 0):
        issue('DPI', 'raster_dpi must be positive when provided.')
    raw_nodes, raw_edges = spec.get('nodes'), spec.get('edges')
    if not isinstance(raw_nodes, list) or not raw_nodes:
        issue('NODES', 'nodes must be a nonempty list.')
        return result()
    if not isinstance(raw_edges, list):
        issue('EDGES', 'edges must be a list.')
        return result()
    nodes: dict[str, dict[str, Any]] = {}
    for index, n in enumerate(raw_nodes):
        if not isinstance(n, dict):
            issue('NODE_TYPE', 'Node must be an object.', str(index)); continue
        ident = n.get('id')
        if not isinstance(ident, str) or not ident.strip():
            issue('NODE_ID', 'Node id must be a nonempty string.', str(index)); continue
        if ident in nodes:
            issue('DUPLICATE_NODE', 'Duplicate node id.', ident); continue
        if not choice(n.get('type'), TYPES):
            issue('NODE_KIND', 'Unknown node type.', ident); continue
        if not isinstance(n.get('label'), str) or not n['label'].strip():
            issue('NODE_LABEL', 'Node label must be nonempty text.', ident)
        valid_geom = True
        for field in ('x_mm', 'y_mm', 'width_mm', 'height_mm'):
            if not is_number(n.get(field)) or (field in {'width_mm','height_mm'} and n[field] <= 0):
                issue('NODE_NUMBER', f'{field} must be a valid finite coordinate/positive dimension.', ident)
                valid_geom = False
        if not valid_geom:
            continue
        if 'angle_deg' in n and (not is_number(n['angle_deg']) or n['angle_deg'] != 0):
            issue('ROTATION_UNSUPPORTED', 'Static geometry checks require angle_deg=0.', ident)
        for field in ('font_pt', 'line_pt'):
            if field in n and (not is_number(n[field]) or n[field] <= 0):
                issue('NODE_STYLE', f'{field} must be positive.', ident)
        nodes[ident] = n
        x1,y1,x2,y2 = box(n)
        if x1 < margin-1e-7 or y1 < margin-1e-7 or x2 > width-margin+1e-7 or y2 > height-margin+1e-7:
            issue('OUT_OF_BOUNDS', 'Node bounding box extends beyond the declared safe margins.', ident)
    # Exclude intentional containers; annotations still need space.
    solids = [(i,n) for i,n in nodes.items() if n['type'] != 'container']
    for k,(a,an) in enumerate(solids):
        ab = box(an)
        for b,bn in solids[k+1:]:
            bb=box(bn)
            if min(ab[2],bb[2])-max(ab[0],bb[0]) > 1e-7 and min(ab[3],bb[3])-max(ab[1],bb[1]) > 1e-7:
                issue('NODE_OVERLAP', 'Axis-aligned bounding boxes overlap; inspect real shape/text geometry.', f'{a},{b}')
    edges: list[dict[str,Any]] = []
    edge_ids: set[str] = set()
    for index,e in enumerate(raw_edges):
        if not isinstance(e,dict):
            issue('EDGE_TYPE', 'Edge must be an object.',str(index)); continue
        ident=e.get('id')
        if not isinstance(ident,str) or not ident.strip():
            issue('EDGE_ID', 'Edge id must be nonempty text.',str(index)); continue
        if ident in edge_ids:
            issue('DUPLICATE_EDGE', 'Duplicate edge id.',ident); continue
        edge_ids.add(ident)
        if not isinstance(e.get('from'),str) or not isinstance(e.get('to'),str) or e['from'] not in nodes or e['to'] not in nodes:
            issue('EDGE_ENDPOINT', 'Both endpoints must reference valid node ids.',ident); continue
        if not isinstance(e.get('label',''),str):
            issue('EDGE_LABEL', 'Edge label must be text.',ident); continue
        if not choice(e.get('arrow','end'), {'end','none','both'}):
            issue('ARROW', 'Unknown arrow value.',ident)
        if not choice(e.get('route','orthogonal'), {'orthogonal','straight'}):
            issue('ROUTE_KIND', 'Only straight/orthogonal nominal paths are supported.',ident)
        for key in ('from_port','to_port'):
            if key in e and not choice(e[key], PORTS):
                issue('PORT', 'Unknown port value.',ident)
        if 'line_pt' in e and (not is_number(e['line_pt']) or e['line_pt']<=0):
            issue('EDGE_STYLE','line_pt must be positive.',ident)
        edges.append(e)
        points=e.get('points_mm')
        if points is None:
            issue('ROUTE_UNCHECKED','No nominal route points; manually check routing.',ident,True); continue
        if not isinstance(points,list) or len(points)<2 or any(not isinstance(p,list) or len(p)!=2 or not all(is_number(v) for v in p) for p in points):
            issue('ROUTE_POINTS','points_mm must contain at least two finite [x,y] points.',ident); continue
        for p in points:
            if p[0]<0 or p[1]<0 or p[0]>width or p[1]>height:
                issue('ROUTE_OUTSIDE','A nominal route point is outside the canvas.',ident)
            elif p[0]<margin or p[1]<margin or p[0]>width-margin or p[1]>height-margin:
                issue('ROUTE_MARGIN','A nominal route enters the safe margin.',ident,True)
        for a,b in zip(points,points[1:]):
            if e.get('route','orthogonal')=='orthogonal' and abs(a[0]-b[0])>1e-7 and abs(a[1]-b[1])>1e-7:
                issue('NONORTHOGONAL','Orthogonal route contains a diagonal segment.',ident)
            for nid,n in nodes.items():
                if nid in {e['from'],e['to']} or n['type']=='container':
                    continue
                if segment_crosses_box(a,b,box(n)):
                    issue('ROUTE_HITS_NODE','A nominal route crosses another node bounding box.',f'{ident}:{nid}')
    # Reachability is structural, not a proof of termination or valid conditions.
    active = {i for i,n in nodes.items() if n['type'] not in {'container','annotation'}}
    outgoing: dict[str,list[dict[str,Any]]] = {i:[] for i in nodes}
    for e in edges:
        outgoing[e['from']].append(e)
    for i,n in nodes.items():
        if n['type']=='decision':
            labels=[e.get('label','').strip().casefold() for e in outgoing[i]]
            if len(labels)<2 or any(not l for l in labels) or len(labels)!=len(set(labels)):
                issue('DECISION_BRANCHES','Decision needs at least two distinct nonempty outgoing labels.',i)
    if choice(spec.get('diagram_type'), {'algorithm','flowchart'}):
        starts={i for i in active if nodes[i]['type']=='start'}
        ends={i for i in active if nodes[i]['type']=='end'}
        if len(starts)!=1:
            issue('START_COUNT','This flowchart profile requires exactly one start node.')
        if not ends:
            issue('END_COUNT','At least one end node is required.')
        def walk(seeds: set[str], reverse: bool=False) -> set[str]:
            seen=set(seeds); stack=list(seeds)
            adjacency: dict[str,list[str]]={i:[] for i in nodes}
            for e in edges:
                a,b=(e['to'],e['from']) if reverse else (e['from'],e['to'])
                adjacency[a].append(b)
            while stack:
                for nxt in adjacency[stack.pop()]:
                    if nxt not in seen:
                        seen.add(nxt);stack.append(nxt)
            return seen
        if starts:
            for ident in sorted(active-walk(starts)):
                issue('UNREACHABLE','Node is not reachable from start.',ident)
        if ends:
            for ident in sorted(active-walk(ends,True)):
                issue('NO_PATH_TO_END','Node has no graph path to an end.',ident)
        for ident in ends:
            if outgoing[ident]:
                issue('END_HAS_OUTPUT','End nodes must not have outgoing control edges.',ident)
        for e in edges:
            if e.get('arrow','end')!='end':
                issue('CONTROL_ARROW','Control edges in this flowchart profile need an end arrow.',e['id'])
    quality=spec.get('quality',{})
    if not isinstance(quality,dict):
        issue('QUALITY_TYPE','quality must be an object.');quality={}
    scale=publication['final_width_mm']/width
    if not is_number(scale) or not is_number(height*scale):
        issue('SCALE_OVERFLOW','Derived dimensions exceed finite numeric range.')
        return result()
    min_font=quality.get('min_final_font_pt',8)
    min_line=quality.get('min_final_line_pt',0.5)
    if not is_number(min_font) or min_font<=0:
        issue('QUALITY_NUMBER','min_final_font_pt must be positive.');min_font=8
    if not is_number(min_line) or min_line<=0:
        issue('QUALITY_NUMBER','min_final_line_pt must be positive.');min_line=0.5
    metrics.update(node_count=len(nodes),edge_count=len(edges),scale=scale,
                   final_height_mm=height*scale,
                   base_final_font_pt=style['font_pt']*scale,
                   base_final_line_pt=style['line_pt']*scale)
    if is_number(dpi) and dpi>0:
        px_w=publication['final_width_mm']/25.4*dpi
        px_h=height*scale/25.4*dpi
        if is_number(px_w) and is_number(px_h):
            metrics['raster_width_px']=math.ceil(px_w)
            metrics['raster_height_px']=math.ceil(px_h)
        else:
            issue('PIXEL_OVERFLOW','Derived pixel dimensions exceed finite numeric range.')
    for i,n in nodes.items():
        font=n.get('font_pt',style['font_pt'])
        line=n.get('line_pt',style['line_pt'])
        if is_number(font) and font>0:
            if font*scale < min_font-1e-9:
                issue('SMALL_FONT',f'Final font {font*scale:.3g} pt is below the declared design threshold {min_font} pt.',i,True)
            # Approximate text fit: NEVER an actual font/Visio measurement.
            if isinstance(n.get('label'),str) and n['label']:
                text_lines=n['label'].splitlines()
                longest=max(sum(1 if ord(ch)>127 else 0.52 for ch in l) for l in text_lines)
                factor=0.60 if n['type']=='decision' else 0.85 if n['type']=='input_output' else 1.0
                usable_width=max(0,n['width_mm']*factor-4)*72/25.4
                usable_height=max(0,n['height_mm']-2)*72/25.4
                if longest*font>usable_width or len(text_lines)*font*1.2>usable_height:
                    issue('TEXT_FIT_HEURISTIC','Approximate text metrics suggest crowding; inspect in Visio, do not auto-shrink.',i,True)
        if is_number(line) and line>0 and line*scale < min_line-1e-9:
            issue('THIN_LINE',f'Final node line is below the declared design threshold {min_line} pt.',i,True)
    for e in edges:
        line=e.get('line_pt',style['line_pt'])
        if is_number(line) and line>0 and line*scale<min_line-1e-9:
            issue('THIN_EDGE','Final connector line is below the declared design threshold.',e['id'],True)
    return result()


def load_json(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f'Non-finite JSON constant is not allowed: {value}')
    return json.loads(path.read_text(encoding='utf-8-sig'),parse_constant=reject_constant)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec',type=Path)
    parser.add_argument('--output',type=Path,help='Optional output report path; choose a new file, not your input.')
    args=parser.parse_args()
    if args.output and args.output.resolve()==args.spec.resolve():
        parser.error('--output cannot overwrite the input specification')
    try:
        report=validate(load_json(args.spec))
    except (OSError,UnicodeError,ValueError) as exc:
        print(f'Input error: {exc}',file=sys.stderr);return 2
    text=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:
        try:
            # Do not silently overwrite a previous review report.
            with args.output.open('x',encoding='utf-8') as f:
                f.write(text+'\n')
        except OSError as exc:
            print(f'Output error: {exc}',file=sys.stderr);return 2
    print(text)
    return 0 if report['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
