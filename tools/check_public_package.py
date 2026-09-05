"""Check the selected public Git tree, without reading excluded local material."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT).decode().split('\0')
    staged = {}
    for entry in filter(None, entries):
        header, name = entry.split('\t', 1)
        mode, blob, stage = header.split()
        if stage != '0' or mode not in {'100644', '100755'}:
            raise SystemExit(f'Non-regular or unmerged public material: {name}')
        staged[name] = blob
    names = list(staged)
    names = sorted(name for name in names if name)
    if not names:
        raise SystemExit('Stage the reviewed public source files first.')
    forbidden = re.compile(r'/(?:Users/[A-Za-z0-9]|var/folders/)|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}')
    materials = []
    for name in names:
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise SystemExit(f'Public symlink or out-of-tree material: {name}')
        if name.startswith(('.codex/', 'receipts/', 'output/', 'integration/pinned-explorer/')) or path.suffix.lower() in {'.zip', '.docx'}:
            raise SystemExit(f'Local-only material selected: {name}')
        raw = subprocess.check_output(['git', 'cat-file', 'blob', staged[name]], cwd=ROOT)
        if forbidden.search(raw.decode('utf-8', errors='replace')):
            raise SystemExit(f'Machine path or credential-shaped text selected: {name}')
        materials.append({'path':name, 'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()})
    output = ROOT / 'output/publication'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'public-materials.json').write_text(json.dumps(materials, indent=2)+'\n')
    print(json.dumps({'status':'passed','files':len(materials),'bytes':sum(row['bytes'] for row in materials),'scope':'Selected current text and paths; not a full history or legal audit'}))

if __name__ == '__main__':
    main()
