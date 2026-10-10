"""Install the packed library in an isolated Vite consumer, including SSR import/render."""
import tempfile,subprocess,json,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];pkg=ROOT/'artifacts/neha-pd-inkwell-vue-0.3.0.tgz';work=Path(tempfile.mkdtemp(prefix='inkwell-v3-consumer-'))
(work/'package.json').write_text(json.dumps({'name':'inkwell-consumer-check','private':True,'type':'module','dependencies':{'@neha-pd/inkwell-vue':str(pkg),'vue':'^3.5.0','vite':'^8.0.0'}}))
subprocess.run(['npm','install','--no-audit','--no-fund'],cwd=work,check=True,capture_output=True)
(work/'ssr.mjs').write_text("import {createSSRApp,h} from 'vue';import {renderToString} from 'vue/server-renderer';import {InkwellEditor} from '@neha-pd/inkwell-vue';const out=await renderToString(createSSRApp({render:()=>h(InkwellEditor,{modelValue:'<p>SSR data</p>',label:'SSR editor'})}));if(!out.includes('Preparing editor'))throw Error('No SSR placeholder');console.log('SSR placeholder passes');")
subprocess.run(['node','ssr.mjs'],cwd=work,check=True)
(work/'index.html').write_text('<html><body><div id="app"></div><script type="module" src="/main.js"></script></body></html>')
(work/'main.js').write_text("import {createApp,h,ref} from 'vue';import {InkwellEditor} from '@neha-pd/inkwell-vue';import '@neha-pd/inkwell-vue/style.css';createApp({setup(){const text=ref('<p>Consumer words</p>');return()=>h(InkwellEditor,{modelValue:text.value,'onUpdate:modelValue':v=>text.value=v,label:'Consumer editor'})}}).mount('#app')")
server=subprocess.Popen([str(work/'node_modules/.bin/vite'),'--host','127.0.0.1','--port','8859','--strictPort'],cwd=work,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://127.0.0.1:8859',timeout=1);break
  except Exception:time.sleep(.15)
 with sync_playwright() as p:
  b=p.chromium.launch();page=b.new_page(viewport={'width':1024,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8859',wait_until='networkidle');ed=page.get_by_role('textbox',name='Consumer editor',exact=True);expect(ed).to_have_text('Consumer words');ed.click();ed.press('ControlOrMeta+a');ed.press('Shift+F10');menu=page.get_by_role('menu',name='Text editing');expect(menu.get_by_role('menuitemcheckbox',name='Bold',exact=True)).to_be_focused();page.keyboard.press('Enter');expect(ed.locator('strong')).to_have_text('Consumer words');assert not errors,errors;b.close()
 (ROOT/'artifacts/consumer-v3.json').write_text(json.dumps({'version':'0.3.0','isolated_install':True,'ssr_render':True,'browser_edit':True,'context_keyboard':True,'runtime_errors':errors},indent=2));print('Isolated package install, SSR render and keyboard context editing pass.')
finally:server.terminate();server.wait(timeout=5)
