"""Verify a complete static candidate without rebuilding or fetching anything."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

def check(root: Path, expected_commit: str|None=None, require_clean: bool=False) -> dict:
    root=root.resolve(strict=True)
    manifest=json.loads((root/'checksums.json').read_bytes())
    files=manifest['files']
    actual=set()
    for path in root.rglob('*'):
        if path.is_symlink():raise ValueError('Publication symlinks are prohibited')
        if path.is_file():actual.add(path.relative_to(root).as_posix())
    if actual!=set(files)|{'checksums.json'}:raise ValueError('Publication file set differs from its manifest')
    for name,row in files.items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:raise ValueError('Unsafe manifest path')
        raw=(root/path).read_bytes()
        if len(raw)!=row['bytes'] or sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Publication digest mismatch: '+name)
    identity=json.loads((root/'publication.json').read_bytes())
    if expected_commit is not None and identity['producer_source_commit']!=expected_commit:raise ValueError('Wrong producer revision')
    if require_clean and identity['working_tree_clean'] is not True:raise ValueError('A dirty source tree cannot be promoted')
    return {'status':'passed','files':len(actual),'bytes':sum((root/name).stat().st_size for name in actual),'producer_source_commit':identity['producer_source_commit'],'working_tree_clean':identity['working_tree_clean'],'manifest_sha256':sha256((root/'checksums.json').read_bytes()).hexdigest()}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path('_site'));parser.add_argument('--expected-commit');parser.add_argument('--require-clean',action='store_true');args=parser.parse_args()
    print(json.dumps(check(args.root,args.expected_commit,args.require_clean)))

if __name__=='__main__':main()
