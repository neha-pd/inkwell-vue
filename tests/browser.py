"""Run against npm run dev (8842), or a built-demo server via INKWELL_URL."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
OUT=Path(__file__).resolve().parents[1]/'artifacts';OUT.mkdir(exist_ok=True)
checks=[]
with sync_playwright() as p:
 b=p.chromium.launch();ctx=b.new_context(viewport={'width':1440,'height':1050},permissions=['clipboard-read','clipboard-write']);page=ctx.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.environ.get('INKWELL_URL','http://127.0.0.1:8842'),wait_until='networkidle')
 mac=page.evaluate("navigator.platform.includes('Mac')")
 editor=page.get_by_role('textbox',name='Draft document',exact=True)
 expect(editor).to_have_attribute('aria-multiline','true')
 page.get_by_role('button',name='Bold',exact=True).focus();page.keyboard.press('ArrowRight');expect(page.get_by_role('button',name='Italic',exact=True)).to_be_focused();page.keyboard.press('End');expect(page.get_by_role('button',name='Redo',exact=True)).to_be_focused();page.keyboard.press('Home');expect(page.get_by_role('button',name='Bold',exact=True)).to_be_focused()
 checks.append('Labeled multiline textbox; toolbar roving Arrow/Home/End focus.')
 page.get_by_text('Test an external content update',exact=True).click()
 def replace(html):
  page.get_by_label('HTML source',exact=True).fill(html);page.get_by_role('button',name='Replace document',exact=True).click()
 def select():
  page.evaluate('() => new Promise(requestAnimationFrame)');editor.locator('p,h2,h3').first.click();editor.press('Meta+ArrowUp' if mac else 'Control+Home');editor.press('Meta+Shift+ArrowDown' if mac else 'Control+Shift+End');page.evaluate('() => new Promise(requestAnimationFrame)')
 replace('<p>Selected words</p>');expect(editor).to_have_text('Selected words');select();page.get_by_role('button',name='Bold',exact=True).click();expect(editor.locator('strong')).to_have_text('Selected words');assert '<strong>Selected words</strong>' in page.locator('#html-output').inner_text()
 page.get_by_role('button',name='Undo',exact=True).click();expect(editor.locator('strong')).to_have_count(0);page.get_by_role('button',name='Redo',exact=True).click();expect(editor.locator('strong')).to_have_text('Selected words')
 select();page.get_by_role('button',name='Italic',exact=True).click();expect(editor.locator('em')).to_have_text('Selected words')
 checks.append('Selection survives toolbar action; bold/italic emit HTML; undo and redo restore formatting.')
 replace('<p>A heading</p>');select();page.get_by_role('button',name='Heading 2',exact=True).click();expect(editor.locator('h2')).to_have_text('A heading');page.get_by_role('button',name='Heading 3',exact=True).click();expect(editor.locator('h3')).to_have_text('A heading')
 replace('<p>First item</p><p>Second item</p>');select();page.get_by_role('button',name='Bullet list',exact=True).click();expect(editor.locator('ul li')).to_have_count(2);page.get_by_role('button',name='Numbered list',exact=True).click();expect(editor.locator('ol li')).to_have_count(2)
 checks.append('Heading 2/3 and bullet/numbered list commands transform document structure.')
 replace('<p>Read more</p>');select();page.get_by_role('button',name='Link',exact=True).click();page.get_by_label('Link address',exact=True).fill('javascript:alert(1)');page.get_by_role('button',name='Apply link',exact=True).click();expect(page.get_by_role('alert')).to_contain_text('Enter a full');expect(editor.locator('a')).to_have_count(0)
 page.get_by_label('Link address',exact=True).fill('https://example.com/guide');page.get_by_role('button',name='Apply link',exact=True).click();expect(editor.locator('a')).to_have_attribute('href','https://example.com/guide');expect(editor.locator('a')).to_have_text('Read more')
 select();page.get_by_role('button',name='Link',exact=True).click();page.get_by_role('button',name='Remove link',exact=True).click();expect(editor.locator('a')).to_have_count(0)
 select();page.get_by_role('button',name='Link',exact=True).click();page.keyboard.press('Escape');expect(editor).to_be_focused();expect(page.get_by_role('form',name='Edit link')).to_have_count(0)
 checks.append('Link validation rejects executable URL; valid link round-trip, removal and Escape focus return.')
 replace('<p>Locked text</p>');page.get_by_label('Read only',exact=True).check();expect(editor).to_have_attribute('contenteditable','false');expect(editor).to_have_attribute('aria-readonly','true');expect(page.get_by_role('button',name='Bold',exact=True)).to_be_disabled();editor.click();page.keyboard.type('SHOULD NOT APPEAR');expect(editor).to_have_text('Locked text');page.get_by_label('Read only',exact=True).uncheck()
 page.get_by_label('Disabled',exact=True).check();expect(editor).to_have_attribute('aria-disabled','true');expect(editor).to_have_attribute('tabindex','-1');expect(editor).to_have_attribute('contenteditable','false');page.get_by_label('Disabled',exact=True).uncheck();expect(editor).to_have_attribute('contenteditable','true')
 checks.append('Reactive readonly blocks typing/commands; disabled removes textbox tab stop; editability restores.')
 replace('<p onclick="window.hacked=1">Safe <strong>text</strong><img src=x onerror="window.hacked=1"><script>window.hacked=1</script><a href="java&#x73;cript:alert(1)">bad link</a><a href="https://example.com">good link</a></p>');expect(editor.locator('script,img,[onclick]')).to_have_count(0);expect(editor.locator('a')).to_have_count(1);assert page.evaluate('window.hacked') is None
 clean=page.locator('#html-output').inner_text();assert 'onclick' not in clean and 'javascript:' not in clean and '<img' not in clean
 checks.append('External v-model sanitization removes scripts, handlers, images and encoded unsafe URLs.')
 # Exercise the actual clipboard/paste path through ProseMirror.
 page.evaluate('() => new Promise(requestAnimationFrame)');editor.locator('p,h2,h3').first.click();editor.press('Meta+ArrowUp' if mac else 'Control+Home');editor.press('Meta+Shift+ArrowDown' if mac else 'Control+Shift+End');page.evaluate('() => new Promise(requestAnimationFrame)');page.evaluate('''async () => { await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob(['<p>Pasted <strong>content</strong><img src=x onerror="window.hacked=1"></p>'],{type:'text/html'}),'text/plain':new Blob(['Pasted content'],{type:'text/plain'})})]) }''');editor.press('ControlOrMeta+v');expect(editor).to_have_text('Pasted content');expect(editor.locator('strong')).to_have_text('content');expect(editor.locator('img')).to_have_count(0)
 checks.append('Rich HTML clipboard paste preserves allowed formatting and drops unsafe content.')
 value=page.locator('#html-output').inner_text();page.get_by_role('button',name='Copy HTML',exact=True).click();assert page.evaluate('navigator.clipboard.readText()')==value
 with page.expect_download() as download:page.get_by_role('button',name='Export HTML',exact=False).click()
 assert Path(download.value.path()).read_text()==value
 replace(value);expect(editor).to_have_text('Pasted content');checks.append('HTML copy/export match v-model and imported output round-trips.')
 page.get_by_role('button',name='Restore sample',exact=True).click();page.get_by_text('Test an external content update',exact=True).click();page.evaluate('document.fonts.ready');page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/'inkwell-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/'inkwell-mobile.png'),full_page=True)
 assert not errors,errors;checks.append('390px mobile has no horizontal overflow; no runtime errors.')
 b.close()
(OUT/'checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
