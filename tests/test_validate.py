"""Executable regression tests. Does not run or mock the Visio UI."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_spec import validate, load_json


class DesignSpecTests(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((ROOT/'examples/iterative-optimization/diagram-spec.json').read_text(encoding='utf-8'))

    def codes(self):
        return {e['code'] for e in validate(self.spec)['errors']}

    def test_01_valid_example(self):
        r=validate(self.spec)
        self.assertTrue(r['ok']);self.assertEqual(r['warnings'],[])
        self.assertEqual(r['metrics']['node_count'],8)
        self.assertEqual(r['metrics']['raster_width_px'],7087)

    def test_02_duplicate_node(self):
        self.spec['nodes'].append(copy.deepcopy(self.spec['nodes'][0]))
        self.assertIn('DUPLICATE_NODE',self.codes())

    def test_03_duplicate_edge(self):
        self.spec['edges'].append(copy.deepcopy(self.spec['edges'][0]))
        self.assertIn('DUPLICATE_EDGE',self.codes())

    def test_04_unknown_endpoint(self):
        self.spec['edges'][0]['to']='NOT_FOUND'
        self.assertIn('EDGE_ENDPOINT',self.codes())

    def test_05_empty_decision_label(self):
        self.spec['edges'][4]['label']=''
        self.assertIn('DECISION_BRANCHES',self.codes())

    def test_06_duplicate_decision_label(self):
        self.spec['edges'][4]['label']='No'
        self.assertIn('DECISION_BRANCHES',self.codes())

    def test_07_out_of_bounds(self):
        self.spec['nodes'][0]['x_mm']=0
        self.assertIn('OUT_OF_BOUNDS',self.codes())

    def test_08_overlapping_nodes(self):
        self.spec['nodes'][2]['y_mm']=63
        self.assertIn('NODE_OVERLAP',self.codes())

    def test_09_feedback_crosses_decision(self):
        self.spec['edges'][-1]['points_mm']=[[27,14],[62,14],[62,63],[27,63]]
        self.assertIn('ROUTE_HITS_NODE',self.codes())

    def test_10_unreachable_node(self):
        self.spec['nodes'].append(dict(id='ORPHAN',label='Orphan',type='process',x_mm=155,y_mm=100,width_mm=16,height_mm=8))
        self.assertIn('UNREACHABLE',self.codes())

    def test_11_cycle_without_exit(self):
        self.spec['edges']=[e for e in self.spec['edges'] if e['id']!='E5']
        self.assertIn('NO_PATH_TO_END',self.codes())

    def test_12_shrink_warns(self):
        self.spec['publication']['final_width_mm']=90
        r=validate(self.spec)
        self.assertTrue(r['ok'])
        self.assertIn('SMALL_FONT',{w['code'] for w in r['warnings']})
        self.assertIn('THIN_EDGE',{w['code'] for w in r['warnings']})
        self.assertEqual(r['metrics']['base_final_font_pt'],4.25)

    def test_13_architecture_needs_no_start_end(self):
        self.spec['diagram_type']='architecture'
        for n in self.spec['nodes']:
            if n['type'] in {'start','end','decision'}:n['type']='component'
        self.assertTrue(validate(self.spec)['ok'])

    def test_14_boolean_not_coordinate(self):
        self.spec['nodes'][0]['x_mm']=True
        self.assertIn('NODE_NUMBER',self.codes())

    def test_15_nonfinite_coordinate(self):
        self.spec['nodes'][0]['x_mm']=float('inf')
        self.assertIn('NODE_NUMBER',self.codes())

    def test_16_nonuniform_scaling_rejected(self):
        self.spec['publication']['uniform_scale']=False
        self.assertIn('NONUNIFORM_SCALE',self.codes())

    def test_17_rotated_geometry_not_claimed(self):
        self.spec['nodes'][0]['angle_deg']=90
        self.assertIn('ROTATION_UNSUPPORTED',self.codes())

    def test_18_diagonal_in_orthogonal_route(self):
        self.spec['edges'][0]['points_mm'][1]=[63,107]
        self.assertIn('NONORTHOGONAL',self.codes())

    def test_19_missing_route_warns(self):
        del self.spec['edges'][0]['points_mm']
        r=validate(self.spec)
        self.assertTrue(r['ok']);self.assertIn('ROUTE_UNCHECKED',{w['code'] for w in r['warnings']})

    def test_20_malformed_types_do_not_crash(self):
        cases=[('diagram_type',[]),('nodes',{}),('canvas',[]),('edges',None)]
        for key,value in cases:
            with self.subTest(key=key):
                s=copy.deepcopy(self.spec);s[key]=value
                self.assertFalse(validate(s)['ok'])
        s=copy.deepcopy(self.spec);s['nodes'][0]['type']=[]
        self.assertFalse(validate(s)['ok'])
        s=copy.deepcopy(self.spec);s['edges'][0]['arrow']={}
        self.assertFalse(validate(s)['ok'])
        self.assertFalse(validate([])['ok'])

    def test_21_text_crowding_warns(self):
        self.spec['nodes'][0]['label']='An excessively long label that cannot fit in this tiny start node'
        r=validate(self.spec)
        self.assertIn('TEXT_FIT_HEURISTIC',{w['code'] for w in r['warnings']})

    def test_22_container_overlap_allowed(self):
        self.spec['nodes'].append(dict(id='GROUP',label='Group',type='container',x_mm=62,y_mm=90,width_mm=90,height_mm=60))
        self.assertTrue(validate(self.spec)['ok'])

    def test_23_input_json_rejects_nan(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json';p.write_text('{"x": NaN}')
            with self.assertRaises(ValueError):load_json(p)

    def test_24_cli_does_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'spec.json';p.write_text(json.dumps(self.spec))
            before=p.read_bytes()
            r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_spec.py'),str(p),'--output',str(p)],capture_output=True)
            self.assertEqual(r.returncode,2);self.assertEqual(p.read_bytes(),before)

    def test_25_cli_errors_for_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_spec.py'),str(Path(tmp)/'missing.json')],capture_output=True)
            self.assertEqual(r.returncode,2)

    def test_26_negative_dpi(self):
        self.spec['publication']['raster_dpi']=-1
        self.assertIn('DPI',self.codes())


if __name__=='__main__':
    unittest.main(verbosity=2)
