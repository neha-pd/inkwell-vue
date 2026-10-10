"""Axe WCAG automated checks for both presentation themes and the custom menu."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];axe=ROOT.parents[1]/'reports/qa-tools/node_modules/axe-core/axe.min.js';results={}
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1050})
 for theme in ['light','dark']:
  page.emulate_media(color_scheme=theme);page.goto(os.environ.get('INKWELL_URL','http://127.0.0.1:8844'),wait_until='networkidle');page.add_script_tag(path=str(axe))
  for state in ['default','listbox']:
   if state=='listbox':page.get_by_role('button',name='Structure',exact=True).click()
   result=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))}")
   results[theme+'-'+state]=result
 b.close()
(ROOT/'artifacts/axe-v3.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));assert not any(results.values()),'Automated WCAG violations remain'
