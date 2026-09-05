"""Browser smoke tests for the independent offline preview, not upstream Explorer."""
from pathlib import Path
import json,datetime,sys,os,threading,http.server,functools
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
OUTPUT=R/'output/preview'
OUTPUT.mkdir(parents=True,exist_ok=True)
checks=[];errors=[];network=[]
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append({'check':name,'status':'passed'})
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(R/'preview'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/index.html'
RENDER_ONLY='--render-only' in sys.argv
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('BROWSER_PATH'),headless=True,chromium_sandbox=os.environ.get('BROWSER_SANDBOX','1')!='0')
 page=browser.new_page(viewport={'width':1440,'height':1060})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith(f'http://127.0.0.1:{server.server_port}/') else None)
 if RENDER_ONLY: page.set_content((R/'preview/index.html').read_text(),wait_until='load')
 else: page.goto(URL)
 page.wait_for_selector('#title')
 check('Default candidate is clearly labelled',page.locator('#title').inner_text().startswith('C-01'))
 check('Independent preview boundary is visible','not the canonical Svelte' in page.locator('.banner').inner_text())
 check('Twenty-two concepts available',page.locator('#results button').count()==22)
 check('Candidate has three outgoing relations',page.locator('.relation').count()==3)
 page.locator('#search').fill('no-contact');check('Search reduces results',0<page.locator('#results button').count()<22)
 page.locator('#search').fill('');page.locator('#type').select_option('Support action');check('Type filter returns three actions',page.locator('#results button').count()==3)
 page.locator('#results button[data-route="action/a-01"]').click();check('Proposed action does not render as completed','"action_status": "proposed"' in page.locator('#facts').inner_text())
 page.locator('#mode').select_option('plain');check('Control hides structured relationship projection',not page.locator('#relationships-panel').is_visible())
 check('Control still retains the same source facts','"action_status": "proposed"' in page.locator('#facts').inner_text())
 page.locator('#mode').select_option('typed');page.locator('#type').select_option('')
 page.locator('#results button[data-route="record/e-04"]').click()
 check('Source HTML renders inertly',page.locator('#facts').inner_text().find('<script>')>=0 and page.evaluate('window.__fixtureExecuted===undefined'))
 page.locator('#results button[data-route="record/h-01"]').click()
 check('Competing candidates both visible','C-01' in page.locator('#relationships').inner_text() and 'C-02' in page.locator('#relationships').inner_text())
 page.screenshot(path=str(OUTPUT/'desktop.png'),full_page=True)
 if not RENDER_ONLY:
  page.reload();check('Deep link survives reload',page.locator('#title').inner_text().startswith('H-01'))
 else:
  check('Selection updates URL fragment',page.evaluate('decodeURIComponent(location.hash)').endswith('record/h-01'))
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUTPUT/'mobile.png'),full_page=True)
 check('No horizontal overflow at 390px',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 page.locator('#search').focus();check('Search is keyboard focusable',page.locator('#search').evaluate('(e)=>document.activeElement===e'))
 check('No external network requests',not network);check('No JavaScript errors',not errors)
 version=browser.version;browser.close()
server.shutdown()
receipt={'status':'passed','test_count':len(checks),'checks':checks,'browser':'Chromium '+version,'browser_sandbox':os.environ.get('BROWSER_SANDBOX','1')!='0','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network_requests':network,'page_errors':errors,'navigation':'DOM rendering only; file and loopback URL navigation were blocked by the browser policy' if RENDER_ONLY else 'Loopback HTTP', 'skipped':['Actual URL loading and reload restoration'] if RENDER_ONLY else [], 'boundary':'These results apply only to preview/index.html, not the canonical Svelte Explorer.'}
(OUTPUT/'acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
