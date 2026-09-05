"""Serve an exact Explorer build and the fictional rehearsal on loopback only."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--port', type=int, default=4175)
    parser.add_argument('--publication-root', type=Path)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    if not (build / 'explore/index.html').is_file():
        parser.error('Build the actual Svelte Explorer first.')
    mounts = {'/rehearsal/bundle/': ROOT / 'bundle',
              '/rehearsal/corrupt/': ROOT / 'output/explorer/corrupt'}
    if args.publication_root:
        mounts['/publication/'] = args.publication_root.resolve()

    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, raw):
            path = unquote(urlsplit(raw).path)
            base, relative = build, path.lstrip('/')
            for prefix, directory in mounts.items():
                if path.startswith(prefix):
                    base, relative = directory, path[len(prefix):]
                    break
            resolved = (base / relative).resolve()
            return str(resolved if resolved.is_relative_to(base.resolve()) else build / '__not_found__')

        def list_directory(self, path):
            self.send_error(404, 'Directory listing is not available')

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'http://127.0.0.1:{args.port}/explore/?bundle=/rehearsal/bundle/okf-bundle.json#record/h-01', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
