"""Synthetic contract tests. These do not measure full paper understanding or GUI success."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import hashlib
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_research import validate, shape_errors
from validate_bundle import validate as bundle
from lookup_capability import search
from release_manifest import read_manifest
from publish_github import valid_names


def load(relative): return json.loads((ROOT/relative).read_text(encoding='utf-8'))

class ResearchTests(unittest.TestCase):
    def setUp(self):
        base='examples/paper-to-multiview/'
        self.paper=load(base+'paper-model.json')
        self.plan=load(base+'algorithm-plan.json')
        self.layout=load(base+'algorithm-layout.json')
    def codes(self,paper=None,plan=None):
        return {e['code'] for e in validate(self.paper if paper is None else paper,self.plan if plan is None else plan)['errors']}
    def test_four_valid_bundles(self):
        for base,plan,layout in [
            ('paper-to-multiview','algorithm-plan','algorithm-layout'),
            ('paper-to-multiview','mindmap-plan','mindmap-layout'),
            ('association-not-causation','figure-plan','layout'),
            ('proof-dependencies','figure-plan','layout')]:
            with self.subTest(base=base,plan=plan):
                b=f'examples/{base}/'
                r=bundle(load(b+'paper-model.json'),load(b+plan+'.json'),load(b+layout+'.json'))
                self.assertTrue(r['ok'],r);self.assertEqual(r['warnings'],[])
    def test_schema_null(self): self.assertIn('SCHEMA',self.codes(paper=False))
    def test_schema_missing(self):
        del self.paper['items']; self.assertIn('SCHEMA',self.codes())
    def test_schema_additional_field(self):
        self.plan['invented']=1; self.assertIn('SCHEMA',self.codes())
    def test_schema_whitespace(self):
        self.paper['paper']['title']=' ';self.assertIn('SCHEMA',self.codes())
    def test_duplicate_item(self):
        self.paper['items'].append(copy.deepcopy(self.paper['items'][0]));self.assertIn('DUPLICATE_ID',self.codes())
    def test_duplicate_evidence(self):
        self.paper['evidence'].append(copy.deepcopy(self.paper['evidence'][0]));self.assertIn('DUPLICATE_ID',self.codes())
    def test_no_read_coverage(self):
        for c in self.paper['coverage']: c['status']='unread'
        self.assertIn('NO_READ_COVERAGE',self.codes())
    def test_evidence_required(self):
        self.paper['items'][0]['evidence_ids']=[];self.assertIn('EVIDENCE_REQUIRED',self.codes())
    def test_unknown_evidence(self):
        self.paper['items'][0]['evidence_ids']=['MISSING'];self.assertIn('UNKNOWN_EVIDENCE',self.codes())
    def test_unavailable_evidence(self):
        for ev in self.paper['evidence']:ev['available']=False
        self.assertIn('UNAVAILABLE_EVIDENCE',self.codes())
    def test_inference_rationale(self):
        self.paper['items'][0]['support']='inferred';self.assertIn('INFERENCE_REASON',self.codes())
    def test_proposal_cannot_become_inference(self):
        node=self.plan['nodes'][0];item=next(i for i in self.paper['items'] if i['id']==node['item_ids'][0])
        item['support']='proposed';node['support']='inferred';self.plan['uncertainty_disclosure']='Inference'
        self.assertIn('SUPPORT_UPGRADE',self.codes())
    def test_unknown_stays_unknown(self):
        node=self.plan['nodes'][0];item=next(i for i in self.paper['items'] if i['id']==node['item_ids'][0])
        item['support']='unknown';self.assertIn('UNKNOWN_DOWNPLAYED',self.codes())
    def test_relation_endpoint(self):
        self.paper['relations'][0]['to']='UNKNOWN';self.assertIn('RELATION_ENDPOINT',self.codes())
    def test_paper_id(self):
        self.plan['paper_id']='OTHER';self.assertIn('PAPER_MISMATCH',self.codes())
    def test_abstract_implementation(self):
        self.paper['paper']['input_scope']='abstract_only';self.plan['detail_level']='implementation'
        self.assertIn('ABSTRACT_IMPLEMENTATION',self.codes())
    def test_synthetic_disclosure(self):
        self.plan['caption']='An algorithm.';self.assertIn('SYNTHETIC_DISCLOSURE',self.codes())
    def test_unknown_node_item(self):
        self.plan['nodes'][0]['item_ids']=['missing'];self.assertIn('UNKNOWN_ITEM',self.codes())
    def test_missing_node_provenance(self):
        self.plan['nodes'][0]['item_ids']=[];self.assertIn('NODE_PROVENANCE',self.codes())
    def test_uncertainty_visible(self):
        self.plan['nodes'][0]['support']='proposed';self.plan['uncertainty_disclosure']=''
        self.assertIn('UNCERTAINTY_DISCLOSURE',self.codes())
    def test_missing_required_item(self):
        missing=self.plan['nodes'][0]['item_ids'][0];self.plan['nodes'][0]['item_ids']=[]
        self.plan['must_keep_item_ids']=[missing];self.assertIn('MISSING_REQUIRED_ITEM',self.codes())
    def test_omission_conflict(self):
        self.plan['omissions'].append({'item_id':self.plan['nodes'][0]['item_ids'][0],'reason':'excluded'})
        self.assertIn('OMITTED_BUT_PRESENT',self.codes())
    def test_edge_endpoint(self):
        self.plan['edges'][0]['to']='missing';self.assertIn('EDGE_ENDPOINT',self.codes())
    def test_missing_edge_provenance(self):
        self.plan['edges'][0]['source_relation_ids']=[];self.assertIn('EDGE_PROVENANCE',self.codes())
    def test_edge_support_upgrade(self):
        rid=self.plan['edges'][0]['source_relation_ids'][0]
        next(r for r in self.paper['relations'] if r['id']==rid)['support']='proposed'
        self.plan['edges'][0]['support']='inferred';self.assertIn('SUPPORT_UPGRADE',self.codes())
    def test_association_cannot_be_causal(self):
        p=load('examples/association-not-causation/paper-model.json');f=load('examples/association-not-causation/figure-plan.json')
        f['edges'][0]['kind']='causal';self.assertIn('SEMANTIC_CAST',self.codes(p,f))
    def test_proof_direction_must_be_declared(self):
        p=load('examples/proof-dependencies/paper-model.json');f=load('examples/proof-dependencies/figure-plan.json')
        f['edges'][0]['reverse_relation']=False;self.assertIn('RELATION_DIRECTION',self.codes(p,f))
    def test_proof_cycle(self):
        p=load('examples/proof-dependencies/paper-model.json');f=load('examples/proof-dependencies/figure-plan.json')
        new=copy.deepcopy(f['edges'][0]);new['id']='cycle';new['from'],new['to']=new['to'],new['from'];f['edges'].append(new)
        self.assertIn('PROOF_CYCLE',self.codes(p,f))
    def test_tree_multiple_parent(self):
        f=load('examples/paper-to-multiview/mindmap-plan.json');new=copy.deepcopy(f['edges'][0]);new['id']='duplicate-parent';f['edges'].append(new)
        self.assertIn('TREE_PARENT',self.codes(plan=f))
    def test_tree_cycle(self):
        f=load('examples/paper-to-multiview/mindmap-plan.json');new=copy.deepcopy(f['edges'][0]);new['id']='cycle';new['from'],new['to']=new['to'],new['from'];f['edges'].append(new)
        self.assertIn('HIERARCHY_CYCLE',self.codes(plan=f))
    def test_decision_branch_label(self):
        decision=next(n['id'] for n in self.plan['nodes'] if n['role']=='decision')
        for e in self.plan['edges']:
            if e['from']==decision:e['label']='Yes'
        self.assertIn('DECISION_BRANCHES',self.codes())
    def test_unknown_capability(self):
        self.plan['capability_ids']=['MISSING'];self.assertIn('UNKNOWN_CAPABILITY',self.codes())
    def test_retired_capability(self):
        self.plan['capability_ids']=['LC01'];self.assertIn('RETIRED_CAPABILITY',self.codes())
    def test_index_only_needs_lookup(self):
        caps=load('assets/capabilities.json')['capabilities'];self.plan['capability_ids']=[next(c['id'] for c in caps if c['status']=='index-only' and c['lifecycle']!='retired')]
        self.assertIn('CAPABILITY_REQUIRES_LOOKUP',{e['code'] for e in validate(self.paper,self.plan)['warnings']})
    def test_label_drift(self):
        self.layout['nodes'][0]['label']='Changed'
        self.assertIn('LABEL_DRIFT',{e['code'] for e in bundle(self.paper,self.plan,self.layout)['errors']})
    def test_plan_id_drift(self):
        self.layout['figure_plan_id']='changed'
        self.assertIn('PLAN_ID',{e['code'] for e in bundle(self.paper,self.plan,self.layout)['errors']})
    def test_association_arrow(self):
        base='examples/association-not-causation/';p=load(base+'paper-model.json');f=load(base+'figure-plan.json');g=load(base+'layout.json')
        g['edges'][0]['arrow']='end';self.assertIn('UNDIRECTED_ARROW',{e['code'] for e in bundle(p,f,g)['errors']})

class ToolTests(unittest.TestCase):
    def test_lookup_mindmap(self): self.assertTrue(any(c['id'].startswith('MM') for c in search('思维导图')))
    def test_lookup_shapesheet(self): self.assertTrue(any(c['family']=='shapesheet' for c in search('ShapeSheet')))
    def test_lookup_exact_id(self): self.assertEqual(search('LC01')[0]['id'],'LC01')
    def test_lookup_empty(self):
        with self.assertRaises(ValueError):search('')
    def test_lookup_filter(self): self.assertTrue(all(c['status']=='index-only' for c in search('data',status='index-only')))
    def test_name_injection_rejected(self):
        for owner,repo in [('a; echo x','demo'),('owner','--help'),('../x','demo'),('owner','x/y')]:
            with self.subTest(owner=owner,repo=repo),self.assertRaises(ValueError):valid_names(owner,repo)
    def test_valid_names(self):valid_names('Zhang646967','visio-academic-diagrams')
    def test_manifest_good_and_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td)
            for name in ('SKILL.md','README.md'): (r/name).write_text('demo')
            lines=[hashlib.sha256(b'demo').hexdigest()+'  '+n for n in ('SKILL.md','README.md')]
            (r/'manifest.sha256').write_text('\n'.join(lines))
            self.assertEqual(len(read_manifest(r)),2)
            (r/'SKILL.md').write_text('modified')
            with self.assertRaises(ValueError):read_manifest(r)
    def test_manifest_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);(r/'manifest.sha256').write_text('0'*64+'  ../outside')
            with self.assertRaises(ValueError):read_manifest(r)
    def test_manifest_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);(r/'real').write_text('demo')
            try:(r/'SKILL.md').symlink_to(r/'real')
            except (OSError,NotImplementedError):self.skipTest('Symlink creation is not permitted on this platform')
            (r/'manifest.sha256').write_text(hashlib.sha256(b'demo').hexdigest()+'  SKILL.md')
            with self.assertRaises(ValueError):read_manifest(r)

if __name__=='__main__':unittest.main()
