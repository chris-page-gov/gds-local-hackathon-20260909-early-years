"""Independently reconcile all three fixture scopes with the pinned Reader."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess

import build

PIN='cce6e68d95c2946bb425effbaab48fbf04281a09'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--explorer',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();consumer=args.explorer.resolve();out=args.output.resolve()
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=consumer,text=True).strip()!=PIN:
        raise build.ContractError('The exact accepted consumer revision is required')
    out.mkdir(parents=True,exist_ok=True)
    uv=shutil.which('uv')
    if not uv or not subprocess.check_output([uv,'--version'],text=True).startswith('uv 0.13.4 '):
        raise build.ContractError('The governed uv 0.13.4 command must be on PATH')
    env=os.environ.copy();env.pop('VIRTUAL_ENV',None)
    for name,folder,current in [('core','bundle',True),('control','baseline',False)]:
        command=[uv,'run','--locked','python','scripts/check_okf_03_source.py',str(build.ROOT/folder),'--output',str(out/(name+'-source.json')),'--projection',str(out/(name+'-projection.json'))]
        if current:command.append('--require-0.3')
        subprocess.run(command,cwd=consumer,env=env,check=True,timeout=120)
    projected=build.load_json(out/'core-projection.json')
    core=build.load_json(build.ROOT/'bundle/core-reference.json')
    if projected['nodes']!=core['nodes'] or projected['edges']!=core['edges']:
        raise build.ContractError('Generated core graph differs from the independent source import')
    full=build.load_json(build.ROOT/'bundle/okf-bundle.json')['corpora']['ey-rehearsal']
    schema=build.load_json(consumer/'profiles/federation/v1/relationship-assertion.schema.json')
    build.Draft202012Validator.check_schema(schema)
    validator=build.Draft202012Validator(schema,format_checker=build.FormatChecker())
    for row in full['relationships']:validator.validate(row)
    for note,body,path in build.collect(build.ROOT):
        node=full['nodes'][note['route']]
        if node['frontmatter']!=note or node['body']!=body or node['source_path']!=path or node['source_sha256']!=build.digest((build.ROOT/'bundle'/path).read_bytes()):
            raise build.ContractError('Domain runtime loses source front matter, prose or exact source binding')
    control_receipt=build.load_json(out/'control-source.json')
    if control_receipt['declared_okf_version']!='0.2':
        raise build.ContractError('The historical control was relabelled')
    build.check_frozen_baseline(build.ROOT)
    receipt={'schema':'ey-current-consumer-source-parity.v1','status':'passed','observed_at':datetime.now(timezone.utc).isoformat(),'consumer_commit':PIN,
        'typed_concepts':len(core['nodes']),'core_references':len(core['edges']),'domain_assertions':len(full['relationships']),
        'all_frontmatter_and_body_equal':True,'all_source_digest_bindings_equal':True,'core_graph_equals_independent_import':True,'historical_control_original_version_and_bytes_preserved':True,
        'scope':'Full declared source and graph parity with the exact Reader schema; native browser, public deployment and release are separate gates.'}
    (out/'consumer-parity.json').write_bytes(build.json_bytes(receipt));print(json.dumps(receipt))

if __name__=='__main__':main()
