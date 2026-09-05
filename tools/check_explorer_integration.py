"""Check the exact fixture against the pinned consumer schema and prepare bad copies."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from importlib.metadata import version
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--explorer', type=Path, default=ROOT.parent / 'okf-explorer')
parser.add_argument('--out', type=Path, default=ROOT / 'output/explorer')
args = parser.parse_args()
EXPLORER = args.explorer.resolve()
args.out.mkdir(parents=True, exist_ok=True)
PIN = 'c8af0b05cab49a5341e0b787e17d49a674868d3a'
schema_path = EXPLORER / 'profiles/federation/v1/relationship-assertion.schema.json'
schema_bytes = subprocess.check_output(['git', 'show', f'{PIN}:profiles/federation/v1/relationship-assertion.schema.json'], cwd=EXPLORER)
schema = json.loads(schema_bytes)
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
bundle_path = ROOT / 'bundle/okf-bundle.json'
bundle = json.loads(bundle_path.read_bytes())
corpus = bundle['corpora']['ey-rehearsal']
rows = corpus['relationships']
assert len(corpus['nodes']) == 22 and len(rows) == 23
for row in rows:
    validator.validate(row)
assert all(row['predicate'] != 'http://www.w3.org/2002/07/owl#sameAs' for row in rows)
assert {row['source'] for row in rows if row['target'] == 'record/h-01' and row['predicate'].endswith('/candidateSource')} == {'candidate/c-01', 'candidate/c-02'}
assert corpus['nodes']['action/a-01']['facts']['action_status'] == 'proposed'
fixtures = args.out / 'corrupt'
fixtures.mkdir(parents=True, exist_ok=True)
corrupt = json.loads(bundle_path.read_bytes())
corrupt['corpora']['ey-rehearsal']['relationships'][0]['assertion_status'] = 'invalid-rehearsal-status'
errors = list(validator.iter_errors(corrupt['corpora']['ey-rehearsal']['relationships'][0]))
assert errors, 'The pinned schema must reject a corrupted assertion status.'
(fixtures / 'corrupt-status.json').write_text(json.dumps(corrupt, ensure_ascii=False, indent=2) + '\n')
(fixtures / 'corrupt-syntax.json').write_bytes(b'{"corpora": ')
receipt = {
    'scope': 'Non-release rehearsal; exact upstream runtime row schema, not full Bundle Wiki conformance.',
    'explorer_commit': PIN, 'python': sys.version,
    'packages': {name: version(name) for name in ['jsonschema', 'ruamel.yaml', 'rdflib']},
    'schema_path': 'profiles/federation/v1/relationship-assertion.schema.json', 'schema_id': schema.get('$id'),
    'schema_sha256': hashlib.sha256(schema_bytes).hexdigest(),
    'bundle_sha256': hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
    'concepts': 22, 'relationships_validated': len(rows), 'format_checker': True,
    'candidate_regression': 'H-01 retains C-01 and C-02 without owl:sameAs',
    'action_regression': 'A-01 remains proposed',
    'corrupt_status_errors': [{'path': list(error.path), 'message': error.message} for error in errors],
    'corrupt_files': {str(p.relative_to(args.out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(fixtures.glob('corrupt-*.json'))},
    'pass': True,
}
(args.out / 'upstream-schema.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
