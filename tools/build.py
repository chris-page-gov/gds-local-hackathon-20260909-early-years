#!/usr/bin/env python3
"""Offline rehearsal compiler. This is NOT the canonical OKF Explorer generator.

Source facts and authored Markdown stay unchanged. JSON, JSON-LD, YAML-LD and RDF
are projections. Network access and executable YAML features are not supported.
"""
from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import io
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from ruamel.yaml import YAML
from ruamel.yaml.tokens import AliasToken, AnchorToken, TagToken
from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph, URIRef, BNode

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://example.invalid/okf-plus/rehearsal/'
EY = BASE + 'vocab/'
OWL_SAME_AS = 'http://www.w3.org/2002/07/owl#sameAs'
MAX_FILE = 2_000_000

class ContractError(ValueError):
    """A source or projection violates the explicitly bounded rehearsal contract."""

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def json_bytes(value: Any) -> bytes:
    # Deterministic project serialisation, not JCS/RFC 8785.
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)+'\n').encode('utf-8')

def safe_path(root: Path, relative: str) -> Path:
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative:
        raise ContractError(f'Unsafe relative path: {relative!r}')
    path = root / p
    if any(x.is_symlink() for x in [path, *path.parents] if x != root.parent):
        raise ContractError(f'Symlink not accepted: {relative}')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ContractError('Path escapes the working tree')
    return path

def read_bytes(path: Path) -> bytes:
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ContractError(f'Missing or oversized input: {path.name}')
    return path.read_bytes()

def check_json_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError('Non-finite number')
        return
    if isinstance(value, list):
        for item in value: check_json_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str): raise ContractError('Non-string YAML mapping key')
            check_json_value(item)
        return
    raise ContractError(f'Not JSON-compatible: {type(value).__name__}; quote dates and identifiers')

def load_yaml(text: str) -> dict[str, Any]:
    y = YAML(typ='safe'); y.version = (1, 2); y.allow_duplicate_keys = False
    try:
        for token in y.scan(text):
            if isinstance(token, (AliasToken, AnchorToken, TagToken)):
                raise ContractError('Tags, anchors and aliases are outside this rehearsal subset')
        value = y.load(text)
    except ContractError: raise
    except Exception as exc: raise ContractError(f'Invalid YAML: {exc}') from exc
    check_json_value(value)
    if not isinstance(value, dict): raise ContractError('Top-level YAML must be a mapping')
    return value

def parse_note(path: Path) -> tuple[dict[str, Any], str]:
    text = read_bytes(path).decode('utf-8')
    if not text.startswith('---\n'): raise ContractError(f'Missing front matter: {path.name}')
    try: front, body = text[4:].split('\n---\n', 1)
    except ValueError as exc: raise ContractError('Missing closing front-matter delimiter') from exc
    return load_yaml(front), body.lstrip('\n')

def load_json(path: Path) -> Any:
    def unique(pairs):
        result = {}
        for k,v in pairs:
            if k in result: raise ContractError(f'Duplicate JSON key: {k}')
            result[k] = v
        return result
    return json.loads(read_bytes(path), object_pairs_hook=unique,
                      parse_constant=lambda s: (_ for _ in ()).throw(ContractError(f'Invalid constant {s}')))

def evidence_value(root: Path, item: dict[str, Any]) -> Any:
    path = safe_path(root, item['source_artifact'])
    if not item['source_artifact'].startswith('sources/'):
        raise ContractError('Evidence must point into the frozen sources directory')
    raw = read_bytes(path)
    if digest(raw) != item['source_sha256']: raise ContractError('Source evidence hash mismatch')
    if item['url'] != BASE + item['source_artifact']:
        raise ContractError('Fixture URL does not identify its local source artefact')
    locator = item['locator']
    if locator == 'file':
        return load_json(path) if path.suffix == '.json' else raw.decode('utf-8')
    if locator.startswith('csv:'):
        key, value = locator[4:].split('=', 1)
        rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        found = [r for r in rows if r.get(key) == value]
        if len(found) != 1: raise ContractError('CSV locator is absent or ambiguous')
        return found[0]
    if locator.startswith('json:'):
        value = load_json(path)
        for part in locator[5:].split('/')[1:]:
            part = part.replace('~1', '/').replace('~0', '~')
            try: value = value[int(part)] if isinstance(value, list) else value[part]
            except (KeyError, ValueError, IndexError) as exc: raise ContractError('JSON pointer does not resolve') from exc
        return value
    raise ContractError('Unsupported evidence locator')

def validate_notes(root: Path, notes: list[tuple[dict[str, Any], str, str]]) -> dict[str, Any]:
    contract = load_json(root/'profile/contract.json')
    if digest(read_bytes(root/contract['context_path'])) != contract['context_sha256']:
        raise ContractError('Pinned context bytes changed without a contract update')
    context = load_json(root/contract['context_path'])['@context']
    predicates = load_json(root/'profile/predicate-registry.json')['predicates']
    schema = load_json(root/'profile/note.schema.json')
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    ids, routes, triples, assertions = {}, set(), set(), set()
    for note,body,path in notes:
        try: validator.validate(note)
        except Exception as exc: raise ContractError(f'{path}: schema: {exc.message}') from exc
        if note['@context'] != contract['context_iri']: raise ContractError('Unpinned context')
        type_map={'Source collection':'ey:SourceCollection','Source record':'ey:SourceRecord','Support action':'ey:SupportAction','Candidate record link':'ey:CandidateRecordLink','Interpretation rule':'ey:InterpretationRule','Scope statement':'ey:ScopeStatement'}
        if note['type'] not in type_map or note['@type'] != type_map[note['type']]:
            raise ContractError('Source and semantic type do not match the rehearsal vocabulary')
        if note['@id'] in ids: raise ContractError('Duplicate entity IRI')
        if note['route'] in routes: raise ContractError('Duplicate browser route')
        if not re.fullmatch(r'[a-z0-9]+(?:[-/][a-z0-9]+)*', note['route']):
            raise ContractError('Unsafe browser route')
        if note['@id'] != contract['entity_base'] + note['route']:
            raise ContractError('Fixture entity identity does not match its declared registry rule')
        ids[note['@id']] = note;routes.add(note['route'])
        for key in note:
            if key in ('@context','@id','@type') or key in context or key in predicates: continue
            raise ContractError(f'Unmapped semantic field: {key}')
        if 'verified' in note: raise ContractError('This exercise has no human verification event')
        values = [evidence_value(root, item) for item in note['sources']]
        facts = note['facts']
        if note['type'] in ('Source record', 'Candidate record link', 'Scope statement') and facts != values[0]:
            raise ContractError('Facts differ from their exact source locator')
        if note['type'] == 'Support action' and any(values[0].get(k) != v for k,v in facts.items()):
            raise ContractError('Action facts differ from source')
        if note['type'] == 'Interpretation rule' and facts['rule'] != values[0]:
            raise ContractError('Rule differs from its evidence')
        if note['type'] == 'Source collection' and facts['source_file'] != note['sources'][0]['source_artifact']:
            raise ContractError('Collection and source file disagree')
    for note,body,path in notes:
        local_triples = set()
        for pred in predicates:
            for obj in note.get(pred, []):
                if not isinstance(obj, dict) or set(obj) != {'@id'}: raise ContractError('IRI object required')
                t = (note['@id'],pred,obj['@id'])
                if t in local_triples: raise ContractError('Duplicate direct triple')
                local_triples.add(t)
        reified = set()
        for a in note['assertions']:
            if a['@id'] in assertions: raise ContractError('Duplicate assertion IRI')
            assertions.add(a['@id'])
            if a['source'] != note['@id'] or a['target'] not in ids: raise ContractError('Unresolved or incorrect endpoint')
            if a['predicate'] not in predicates: raise ContractError('Unregistered predicate')
            if a['assertion_scope'] != 'synthetic-fixture' or a['authority']['class'] != 'synthetic':
                raise ContractError('Synthetic authority was promoted')
            if a['assertion_status'] != 'normalized': raise ContractError('This fixture permits deterministic projections only')
            t=(a['source'],a['predicate'],a['target'])
            if t in triples: raise ContractError('Duplicate assertion of the same triple')
            triples.add(t);reified.add(t)
            if not a['evidence']: raise ContractError('Assertion has no evidence')
            values=[evidence_value(root, e) for e in a['evidence']]
            if a['evidence'] != note['sources']: raise ContractError('Relationship evidence must identify this source record')
            target=ids[a['target']];pred=a['predicate'];facts=note['facts']
            if pred.endswith('/isPartOf'):
                if target['type'] != 'Source collection' or target['facts']['source_file'] != note['sources'][0]['source_artifact']:
                    raise ContractError('Source membership is not supported')
            elif pred in (EY+'hasPlannedAction',EY+'hasCompletedAction',EY+'hasCancelledAction'):
                required={EY+'hasPlannedAction':'proposed',EY+'hasCompletedAction':'completed',EY+'hasCancelledAction':'cancelled'}[pred]
                if facts.get('action_status') != required or facts.get('action_id') != target['facts'].get('action_id'):
                    raise ContractError('Action relationship upgrades or changes the source state')
            elif pred in (EY+'candidateSource',EY+'candidateTarget'):
                field='source_ref' if pred.endswith('candidateSource') else 'target_ref'
                if facts.get(field) != target['facts'].get('record_id'): raise ContractError('Candidate endpoint changed')
            elif pred == EY+'usesCandidateRule':
                if note['type'] != 'Candidate record link' or target['route'] != 'rule/candidate-interpretation':
                    raise ContractError('Incorrect interpretation rule')
            for field in ['label','inverse_label']:
                if a[field] != predicates[pred][field]: raise ContractError('Predicate label mismatch')
        if local_triples != reified: raise ContractError('Direct triples and evidence-bearing assertions differ')
    if len(notes)!=contract['expected_concepts'] or len(assertions)!=contract['expected_relationships']:
        raise ContractError('Declared fixture coverage does not reconcile')
    return {'contract':contract,'context':context,'predicates':predicates,'ids':ids,'triples':triples}

def collect(root: Path):
    notes=[]
    for path in sorted((root/'bundle/concepts').rglob('*.md')):
        if path.is_symlink(): raise ContractError('Symlink concept')
        note,body=parse_note(path)
        notes.append((note,body,str(path.relative_to(root/'bundle'))))
    # OKF reserved files and front matter are checked separately from our profile.
    index,_=parse_note(root/'bundle/index.md')
    if index != {'okf_version':'0.2'}: raise ContractError('Unexpected root index metadata')
    log=read_bytes(root/'bundle/log.md').decode()
    dates=re.findall(r'^## (\d{4}-\d{2}-\d{2})$',log,re.M)
    if dates != sorted(dates,reverse=True): raise ContractError('Log is not newest first')
    return notes

def make_outputs(root: Path) -> dict[str, bytes]:
    notes=collect(root);v=validate_notes(root,notes);contract=v['contract']
    nodes={};rels=[];baseline_nodes={};outputs={};graphnodes=[]
    for note,body,path in notes:
        n=copy.deepcopy(note);n.pop('@context')
        n['body']=body;n['source_path']=path;graphnodes.append(n)
        runtime={k:copy.deepcopy(note[k]) for k in ['type','route','title','description','tags','generated','sources','facts','status']}
        runtime.update(id=note['route'],semantic_id=note['@id'],body=body,source=path,section=note['route'].split('/')[0],assertion_scope='synthetic-fixture')
        nodes[note['route']]=runtime
        baseline_nodes[note['route']]=copy.deepcopy(runtime)
        minimal={k:copy.deepcopy(note[k]) for k in ['type','title','description','tags','generated','sources','facts','status']}
        out=io.StringIO();y=YAML();y.width=100;y.representer.ignore_aliases=lambda *args: True;y.dump(minimal,out)
        outputs['baseline/'+path]=('---\n'+out.getvalue()+'---\n\n'+body).encode()
        for a in note['assertions']:
            row={k:copy.deepcopy(value) for k,value in a.items() if k not in ['@id','@type','source','target']}
            row.update(schema='okf-relationship-assertion.v2',id=a['@id'],source_iri=a['source'],target_iri=a['target'],
                       source=note['route'],target=v['ids'][a['target']]['route'])
            rels.append(row)
    rels.sort(key=lambda r:r['id'])
    title='Synthetic early-years relationship rehearsal'
    bundle={'schema':'okf-explorer-bundle.v0','kind':'okf-bundle','okf_version':'0.2',
      'generated_by':'tools/build.py (independent rehearsal compiler)','generated_at':contract['snapshot_date'],
      'meta':{'title':title,'description':'22 fictional concepts. No identity merge, diagnosis or live referral.',
        'default_corpus':'ey-rehearsal','corpus_order':['ey-rehearsal'],'profile':contract['profile_iri'],
        'release_grade':False,'semantic_descriptor':'okf-bundle.yamlld','limitations':contract['not_claimed']},
      'corpora':{'ey-rehearsal':{'id':'ey-rehearsal','label':'Early years rehearsal','title':title,
        'subtitle':'SYNTHETIC • PROTOTYPE • NO OPERATIONAL AUTHORITY','root':'index.md','source_root':'.',
        'markdown_url':'./','sections':sorted({r.split('/')[0] for r in nodes}), 'nodes':nodes,'relationships':rels,'assertion_scope':'synthetic-fixture'}}}
    doc={'@context':v['context'],'@graph':graphnodes}
    jsonld=json_bytes(doc)
    rdf=Graph().parse(data=jsonld.decode(),format='json-ld')
    if any(isinstance(term,BNode) for triple in rdf for term in triple):
        raise ContractError('Blank nodes are outside this tiny deterministic N-Triples serialiser')
    if list(rdf.triples((None,URIRef(OWL_SAME_AS),None))): raise ContractError('Identity equivalence is prohibited')
    for s,p,o in v['triples']:
        if (URIRef(s),URIRef(p),URIRef(o)) not in rdf: raise ContractError('A declared relation was lost in RDF projection')
    nt='\n'.join(sorted(line for line in rdf.serialize(format='nt').splitlines() if line.strip()))+'\n'
    yf=io.StringIO();y=YAML();y.width=100;y.representer.ignore_aliases=lambda *args: True;y.dump(doc,yf)
    outputs.update({'bundle/okf-bundle.json':json_bytes(bundle),'bundle/okf-bundle.jsonld':jsonld,
      'bundle/okf-bundle.yamlld':yf.getvalue().encode(),'bundle/okf-bundle.nt':nt.encode(),
      'bundle/iri-route-registry.json':json_bytes({n['semantic_id']:{'route':r,'label':n['title']} for r,n in nodes.items()}),
      'bundle/coverage.json':json_bytes({'concepts':len(nodes),'relationships':len(rels),'rdf_triples':len(rdf),'scope':'synthetic-fixture','source_records':11,'candidate_links':3,
         'counts_prove':'Reconciliation to this declared fictional fixture only, not real-world completeness.'})})
    baseline=copy.deepcopy(bundle);baseline['meta'].pop('semantic_descriptor')
    baseline['meta']['profile']='minimal-okf-rehearsal-control';baseline['corpora']['ey-rehearsal']['relationships']=[]
    outputs['baseline/okf-bundle.json']=json_bytes(baseline)
    outputs['baseline/index.md']=read_bytes(root/'bundle/index.md')
    outputs['baseline/log.md']=read_bytes(root/'bundle/log.md')
    # Export exact source/context copies for a self-contained transport bundle.
    # These copies are generated; the root sources/ and profile/ remain authoritative.
    for family in ('sources','profile'):
        for asset in sorted((root/family).glob('*')):
            if asset.is_file():
                rel=str(asset.relative_to(root))
                outputs['bundle/'+rel]=read_bytes(asset)
                if family=='sources': outputs['baseline/'+rel]=read_bytes(asset)
    outputs['bundle/integrity.json']=json_bytes({'algorithm':'SHA-256 of exact UTF-8 output bytes (not RDF canonicalisation)',
       'files':{p:{'sha256':digest(b),'bytes':len(b)} for p,b in sorted(outputs.items())}})
    return outputs

def run(root: Path=ROOT, check: bool=False) -> dict[str,Any]:
    outputs=make_outputs(root)
    changed=[]
    for name,content in outputs.items():
        path=safe_path(root,name)
        if not path.is_file() or path.read_bytes()!=content:
            changed.append(name)
            if not check:
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    if check and changed: raise ContractError('Missing or changed projections: '+', '.join(changed))
    return {'status':'passed','mode':'check' if check else 'build','output_files':len(outputs),
        'changed':changed,'scope':'local rehearsal compiler; not canonical Explorer acceptance'}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--root',type=Path,default=ROOT)
    args=ap.parse_args()
    try: print(json.dumps(run(args.root,args.check),indent=2));return 0
    except (ContractError, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)},indent=2),file=sys.stderr);return 1
if __name__=='__main__': raise SystemExit(main())
