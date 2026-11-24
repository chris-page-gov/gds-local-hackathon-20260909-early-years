"""Check actual static guide navigation, images and asset failures in Chrome."""
from datetime import datetime,timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output/publication-browser';out.mkdir(parents=True,exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'_site')))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_port}/';views=[];errors=[];failed=[]
try:
    with sync_playwright() as runtime:
        browser=runtime.chromium.launch(executable_path=os.environ.get('BROWSER_PATH'),headless=True,chromium_sandbox=True)
        try:
            page=browser.new_page()
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('console',lambda message:errors.append(message.text) if message.type=='error' else None)
            page.on('response',lambda response:failed.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
            for scope in ('core','domain','control'):
                response=page.goto(base+'walkthrough/'+scope+'.html',wait_until='networkidle',timeout=15000)
                assert response.status==200
                icon=page.locator('link[rel="icon"]').evaluate('(link)=>link.href')
                assert icon==base+'favicon.svg' and page.request.get(icon).status==200
                assert page.get_by_role('link',name='Open this bundle and record in OKF Explorer',exact=True).count()==1
                for view,width,height in [('desktop',1440,1050),('mobile',390,844)]:
                    page.set_viewport_size({'width':width,'height':height})
                    suffix=scope+('-mobile' if view=='mobile' else '')+'.svg'
                    page.wait_for_function('(suffix)=>{const image=document.querySelector("picture img");return image.complete&&image.naturalWidth>0&&image.currentSrc.endsWith(suffix)}',arg=suffix,timeout=10000)
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                    page.screenshot(path=str(out/(scope+'-'+view+'.png')),full_page=True)
                    views.append({'scope':scope,'view':view,'diagram_loaded':True,'overflow':False,'favicon_status':200})
            assert not errors,errors
            assert not failed,failed
            receipt={'status':'passed','observed_at':datetime.now(timezone.utc).isoformat(),'browser':browser.version,'sandbox':True,'views':views,'console_and_page_errors':errors,'failed_asset_responses':failed,'scope':'Actual local publication pages and assets; public Reader access and release remain separate gates.'}
            (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
        finally:browser.close()
finally:
    server.shutdown();server.server_close();thread.join(timeout=5)
