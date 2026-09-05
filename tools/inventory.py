#!/usr/bin/env python3
"""Read-only byte inventory. Does not certify sensitivity, synthetic status or rights."""
from pathlib import Path
import argparse,hashlib,json,sys

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory',type=Path);ap.add_argument('--max-files',type=int,default=500)
    ap.add_argument('--max-total-bytes',type=int,default=100_000_000)
    args=ap.parse_args();root=args.directory.resolve()
    if not root.is_dir():ap.error('The approved source directory does not exist')
    rows=[];skipped=[];total=0
    for path in sorted(root.rglob('*')):
        rel=str(path.relative_to(root))
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p!=root):
            skipped.append({'path':rel,'reason':'symlink'});continue
        if not path.is_file():continue
        size=path.stat().st_size
        if len(rows)>=args.max_files or total+size>args.max_total_bytes:
            skipped.append({'path':rel,'reason':'budget'});continue
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(1_048_576),b''):h.update(block)
        total+=size;rows.append({'path':rel,'bytes':size,'sha256':h.hexdigest(),'extension':path.suffix.lower(),'extraction':'not_performed','rights':'unknown','synthetic_status':'not_determined_by_hashing'})
    print(json.dumps({'schema':'read-only-input-inventory.v0.1','files':rows,'bytes_read':total,'skipped':skipped,'complete_listing_within_budget':not skipped,'classification':'not_performed'},indent=2))
    return 0 if not skipped else 2
if __name__=='__main__':raise SystemExit(main())
