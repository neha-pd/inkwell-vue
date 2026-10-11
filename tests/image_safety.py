"""Images retain safe supported content and require descriptions on every import path."""
from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import os,json
out=Path(__file__).resolve().parents[1]/'artifacts'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True);page=b.new_page()
 page.route('https://example.invalid/**',lambda r:r.fulfill(status=200,content_type='image/png',body=b''))
 page.goto(os.environ.get('INKWELL_URL','http://127.0.0.1:8793/inkwell/'),wait_until='networkidle')
 page.get_by_text('Test an external content update',exact=True).click();editor=page.get_by_role('textbox',name='Draft document',exact=True)
 def replace(html):
  page.get_by_label('HTML source',exact=True).fill(html);page.get_by_role('button',name='Replace document',exact=True).click()
 replace('<p>Before</p><img src="https://example.invalid/image.png"><img src="https://example.invalid/image.png" alt="   "><p>After</p>');expect(editor.locator('img')).to_have_count(0);expect(editor).to_contain_text('Before')
 replace('<p>Described</p><img src="https://example.invalid/image.png" alt="A described diagram" onerror="window.hacked=true" style="position:fixed">');expect(editor.locator('img')).to_have_count(1);expect(editor.locator('img')).to_have_attribute('alt','A described diagram');assert editor.locator('img').get_attribute('onerror') is None;assert 'position' not in (editor.locator('img').get_attribute('style') or '');assert not page.evaluate('Boolean(window.hacked)')
 replace('<p>Unsafe schemes</p><img src="javascript:alert(1)" alt="Unsafe"><img src="data:image/svg+xml;base64,PHN2Zz4=" alt="Unsupported SVG">');expect(editor.locator('img')).to_have_count(0)
 pixel='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jGFAAAAAASUVORK5CYII='
 replace(f'<p>Raster</p><img src="{pixel}" alt="A small test pixel">');expect(editor.locator('img')).to_have_attribute('src',pixel);expect(editor.locator('img')).to_have_attribute('alt','A small test pixel')
 b.close()
checks=['Undescribed HTTPS images are removed even after clipboard URL normalization.','Described HTTPS image retained while active attributes and unsafe styles removed.','JavaScript and SVG sources removed even with an alt description.','Bounded described PNG data image preserved.']
(out/'image-safety-v3.1.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
