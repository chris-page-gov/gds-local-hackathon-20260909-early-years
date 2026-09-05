"""Executable checks of the local rehearsal, not claims about an upstream reader."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rdflib import Graph, URIRef
from rdflib.compare import isomorphic
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build
R=build.ROOT

def copy_fixture(target):
    target.mkdir()
    for name in ('sources', 'profile', 'bundle', 'baseline'):
        shutil.copytree(R / name, target / name)

class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes=build.collect(R)
        cls.outputs=build.make_outputs(R)
    def changed(self,route):
        notes=copy.deepcopy(self.notes)
        n=next(n for n,b,p in notes if n['route']==route)
        return notes,n
    def rejects(self,notes):
        with self.assertRaises(build.ContractError):build.validate_notes(R,notes)
    def test_01_source_inventory_hashes(self):
        manifest=build.load_json(R/'sources/manifest.json')
        expected={str(p.relative_to(R)) for p in (R/'sources').iterdir() if p.name!='manifest.json'}
        self.assertEqual({x['path'] for x in manifest['files']},expected)
        for item in manifest['files']:self.assertEqual(build.digest((R/item['path']).read_bytes()),item['sha256'])
    def test_02_structural_concepts_and_relationships(self):
        result=build.validate_notes(R,self.notes)
        self.assertEqual(len(self.notes),22);self.assertEqual(len(result['triples']),23)
    def test_03_duplicate_yaml_key(self):
        with self.assertRaises(build.ContractError):build.load_yaml('type: Record\ntype: Other\n')
    def test_04_yaml_tags_rejected(self):
        with self.assertRaises(build.ContractError):build.load_yaml('value: !!str 123\n')
    def test_05_yaml_aliases_rejected(self):
        with self.assertRaises(build.ContractError):build.load_yaml('a: &a hello\nb: *a\n')
    def test_06_non_string_keys_rejected(self):
        with self.assertRaises(build.ContractError):build.load_yaml('1: value\n')
    def test_07_nonfinite_number_rejected(self):
        with self.assertRaises(build.ContractError):build.load_yaml('value: .nan\n')
    def test_08_implicit_timestamp_rejected(self):
        with self.assertRaises(build.ContractError):build.load_yaml('date: 2026-09-05\n')
    def test_09_duplicate_entity_rejected(self):
        notes=copy.deepcopy(self.notes);notes.append(copy.deepcopy(notes[0]));self.rejects(notes)
    def test_10_duplicate_route_rejected(self):
        notes,n=self.changed('record/h-01');n['route']='record/h-02';self.rejects(notes)
    def test_11_unsafe_route_rejected(self):
        notes,n=self.changed('record/h-01');n['route']='../outside';self.rejects(notes)
    def test_12_unpinned_remote_context_rejected(self):
        notes,n=self.changed('record/h-01');n['@context']='https://example.org/mutable';self.rejects(notes)
    def test_13_unknown_semantic_field_rejected(self):
        notes,n=self.changed('record/h-01');n['unmapped_relationship']='guess';self.rejects(notes)
    def test_14_unknown_jsonld_keyword_rejected(self):
        notes,n=self.changed('record/h-01');n['@reverse']={'some':'thing'};self.rejects(notes)
    def test_15_missing_direct_triple_rejected(self):
        notes,n=self.changed('record/h-01');del n['http://purl.org/dc/terms/isPartOf'];self.rejects(notes)
    def test_16_unregistered_predicate_rejected(self):
        notes,n=self.changed('record/h-01');n['assertions'][0]['predicate']='https://example.org/unknown';self.rejects(notes)
    def test_17_broken_endpoint_rejected(self):
        notes,n=self.changed('record/h-01');n['assertions'][0]['target']=build.BASE+'id/missing';self.rejects(notes)
    def test_18_duplicate_assertion_rejected(self):
        notes,n=self.changed('record/h-01');n['assertions'].append(copy.deepcopy(n['assertions'][0]));self.rejects(notes)
    def test_19_synthetic_cannot_be_official(self):
        notes,n=self.changed('record/h-01');n['assertions'][0]['authority']['class']='official';self.rejects(notes)
    def test_20_evidence_hash_mismatch_rejected(self):
        notes,n=self.changed('record/h-01');n['sources'][0]['source_sha256']='0'*64;self.rejects(notes)
    def test_21_missing_locator_rejected(self):
        notes,n=self.changed('record/e-01');n['sources'][0]['locator']='json:/records/99';self.rejects(notes)
    def test_22_source_facts_cannot_be_silently_changed(self):
        notes,n=self.changed('record/h-04');n['facts']['concern_state']='no-concern-recorded';self.rejects(notes)
    def test_23_proposal_cannot_be_completed_relationship(self):
        notes,n=self.changed('record/r-01');pred=build.EY+'hasPlannedAction';new=build.EY+'hasCompletedAction'
        n[new]=n.pop(pred)
        for a in n['assertions']:
            if a['predicate']==pred:a['predicate']=new;a['label']='records completed action';a['inverse_label']='is recorded completed in'
        self.rejects(notes)
    def test_24_candidate_target_cannot_be_substituted(self):
        notes,n=self.changed('candidate/c-01');pred=build.EY+'candidateTarget';target=build.BASE+'id/record/e-03'
        n[pred]=[{'@id':target}]
        for a in n['assertions']:
            if a['predicate']==pred:a['target']=target
        self.rejects(notes)
    def test_25_no_identity_equivalence_in_actual_rdf(self):
        g=Graph().parse(data=self.outputs['bundle/okf-bundle.jsonld'].decode(),format='json-ld')
        self.assertEqual(list(g.triples((None,URIRef(build.OWL_SAME_AS),None))),[])
        candidates=list(g.subjects(URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),URIRef(build.EY+'CandidateRecordLink')))
        self.assertEqual(len(candidates),3)
    def test_26_json_yaml_same_data_model(self):
        a=json.loads(self.outputs['bundle/okf-bundle.jsonld']);b=build.load_yaml(self.outputs['bundle/okf-bundle.yamlld'].decode())
        self.assertEqual(a,b)
    def test_27_real_rdf_parser_roundtrip(self):
        a=Graph().parse(data=self.outputs['bundle/okf-bundle.jsonld'].decode(),format='json-ld')
        b=Graph().parse(data=self.outputs['bundle/okf-bundle.nt'].decode(),format='nt')
        self.assertTrue(isomorphic(a,b));self.assertEqual(len(a),721)
    def test_28_rebuild_byte_identical(self):
        self.assertEqual(build.make_outputs(R),self.outputs)
    def test_29_control_has_identical_facts_and_prose(self):
        full=json.loads(self.outputs['bundle/okf-bundle.json'])['corpora']['ey-rehearsal']
        control=json.loads(self.outputs['baseline/okf-bundle.json'])['corpora']['ey-rehearsal']
        self.assertEqual(full['nodes'],control['nodes']);self.assertEqual(control['relationships'],[])
        for note,body,path in self.notes:
            text=self.outputs['baseline/'+path].decode();baseline_body=text[4:].split('\n---\n',1)[1].lstrip('\n')
            self.assertEqual(body,baseline_body)
    def test_30_unsafe_source_path_rejected(self):
        with self.assertRaises(build.ContractError):build.safe_path(R,'../not-a-source')
    def test_31_no_network_during_compilation(self):
        with patch('socket.create_connection',side_effect=AssertionError('Network forbidden')),patch('socket.socket.connect',side_effect=AssertionError('Network forbidden')):
            self.assertEqual(build.make_outputs(R),self.outputs)
    def test_32_tampered_projection_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'kit'
            copy_fixture(target)
            (target/'bundle/okf-bundle.json').write_text('{}\n')
            with self.assertRaises(build.ContractError):build.run(target,True)
    def test_33_context_byte_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'kit';copy_fixture(target)
            with (target/'profile/context.jsonld').open('a') as f:f.write(' ')
            with self.assertRaises(build.ContractError):build.make_outputs(target)
    def test_34_reification_does_not_cancel_a_direct_identity_triple(self):
        # A controlled semantic counterexample, never emitted in the bundle.
        source=URIRef(build.BASE+'test/a');target=URIRef(build.BASE+'test/b');pred=URIRef(build.OWL_SAME_AS)
        g=Graph();g.add((source,pred,target))
        g.add((URIRef(build.BASE+'test/claim'),URIRef(build.EY+'reviewStatus'),URIRef(build.EY+'pending')))
        self.assertIn((source,pred,target),g)

    def test_35_unknown_type_cannot_evade_source_validation(self):
        notes,n=self.changed('record/h-01');n['type']='Other';n['facts']['concern_state']='invented';self.rejects(notes)
    def test_36_candidate_cannot_be_retyped_as_person(self):
        notes,n=self.changed('candidate/c-01');n['@type']='ey:Person';self.rejects(notes)

if __name__=='__main__':unittest.main(verbosity=2)
