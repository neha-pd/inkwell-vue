"""Keyboard/pointer checks for the custom controls; actual editor state and downloads."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
OUT=Path(__file__).resolve().parents[1]/'artifacts';checks=[]
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1050},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(os.environ.get('INKWELL_URL','http://127.0.0.1:8844'),wait_until='networkidle');editor=page.get_by_role('textbox',name='Draft document',exact=True)
 expect(page.locator('select')).to_have_count(0)
 def button(name):return page.get_by_role('button',name=name,exact=True)
 button('Structure').focus();page.keyboard.press('ArrowDown');expect(page.get_by_role('listbox',name='Structure')).to_be_focused();page.keyboard.press('Home');page.keyboard.press('ArrowDown');page.keyboard.press('Enter');expect(editor.locator('h1')).to_have_count(1);expect(button('Structure')).to_be_focused();checks.append('Structure menu opens by keyboard, moves active option and applies heading with trigger focus restored.')
 editor.click();editor.press('ControlOrMeta+a');button('Font').click();page.keyboard.press('m');page.keyboard.press('Enter');assert editor.locator('[style*="font-family: monospace"]').count()>0
 button('Size').click();page.keyboard.press('End');page.keyboard.press('Enter');assert editor.locator('[style*="font-size: 48px"]').count()>0;checks.append('Custom font and size listboxes apply actual document styles, including typeahead and End.')
 button('Align').click();page.keyboard.press('Escape');expect(page.get_by_role('listbox')).to_have_count(0);expect(button('Align')).to_be_focused();button('Align').click();page.get_by_role('heading',name='A blank page. Every possibility.').click();expect(page.get_by_role('listbox')).to_have_count(0);button('Size').click();page.keyboard.press('Tab');expect(page.get_by_role('listbox')).to_have_count(0);expect(button('Align')).to_be_focused();checks.append('Listboxes dismiss on Escape/outside/Tab, preserving logical keyboard navigation.')
 button('Restore sample').click();page.get_by_role('radio',name='Text',exact=True).check()
 with page.expect_download() as d:button('Export document').click()
 assert 'The best tools' in Path(d.value.path()).read_text();checks.append('Segmented export radio group produces real plain-text document.')
 page.get_by_label('Read only',exact=True).check();expect(button('Structure')).to_be_disabled();expect(editor).to_have_attribute('contenteditable','false');page.get_by_label('Read only',exact=True).uncheck();page.get_by_text('Import & local drafts',exact=True).click();page.get_by_label('Import document',exact=True).set_input_files({'name':'note.txt','mimeType':'text/plain','buffer':b'Imported through the designed upload control.'});expect(editor).to_have_text('Imported through the designed upload control.');page.get_by_text('Import & local drafts',exact=True).click();button('Restore sample').click();checks.append('Styled switch retains native checkbox operation; upload trigger retains the real file input and import behavior.')
 page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/'inkwell-v3-desktop.png'),full_page=True)
 workspace=page.locator('.workspace').bounding_box();pane=page.locator('.workspace>.settings').bounding_box();canvas=page.locator('.workspace>div').bounding_box();assert pane['height']<canvas['height']+90,(pane,canvas);checks.append('Collapsed inspector stays within the writing canvas height rather than extending a blank column.')
 for scheme in ['light','dark']:
  page.emulate_media(color_scheme=scheme);page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo(0,0)');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/f'inkwell-v3-{scheme}-mobile.png'),full_page=True);button('Structure').click();panel=page.get_by_role('listbox').bounding_box();assert panel['x']>=0 and panel['x']+panel['width']<=390;assert panel['y']>=0 and panel['y']+panel['height']<=844;page.screenshot(path=str(OUT/f'inkwell-v3-select-{scheme}.png'));page.keyboard.press('Escape')
 checks.append('390px light/dark layouts and custom menu bounds pass without horizontal overflow.');assert not errors,errors;b.close()
(OUT/'controls-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtime_errors':errors},indent=2));print(json.dumps(checks,indent=2))
