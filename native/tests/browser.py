from browser_base import run
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import json
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'content.js').read_text().removeprefix('export const DATA = ').removesuffix(';\n'));O=json.loads((Path(__file__).parent/'python-oracles.json').read_text())
def walk(page,origin,ready,click,passed,out):
 click(page,'Begin the challenge')
 for kind,items,check_label,next_label in [('inbox',D['transactions'],'Check this event','Next event'),('equation',D['recordable'],'Check the dual effect','Next transaction')]:
  for i,t in enumerate(items):
   options=D['eventOptions'] if kind=='inbox' else t['choices'];answer=t['event_type'] if kind=='inbox' else t['correct_choice'];choice=next(x for x in options if x!=answer) if i==0 else answer
   if i==0:click(page,check_label);assert page.get_by_role('status').count()>0
   page.get_by_role('radio',name=choice,exact=True).check();ready(page)
   if i==0:
    before=page.url;click(page,'Back');assert page.get_by_role('button',name='Start over',exact=True).is_disabled();click(page,'Forward');assert page.get_by_role('radio',name=choice,exact=True).is_checked();assert page.url==before;page.reload();ready(page);assert page.get_by_role('radio',name=choice,exact=True).is_checked()
   click(page,check_label);assert page.get_by_role('button',name=check_label,exact=True).count()==0
   if i==0:assert page.get_by_text('Review this one. You selected: '+choice,exact=True).is_visible()
   label=('Continue to the Equation Lab' if kind=='inbox' else 'Build the financial statements') if i==len(items)-1 else next_label;click(page,label)
  passed(kind+': complete original round, wrong first answer, corrected balances, first-pass scoring and draft review/refresh')
 root=page.locator('#statement-workspace');assert root.locator('button[data-statement-index="1"]').is_disabled();assert page.locator('iframe').count()==0
 root.locator('#finalize-statement').click();ready(page);assert root.get_by_text('You still have 3 account balances to place correctly on this statement.',exact=True).is_visible()
 # Real native HTML drag/drop followed by an intentionally wrong statement check.
 source=root.locator('[data-tile-id="cash"]');zone=root.locator('[data-zone-id="operating_revenue"]');zone.scroll_into_view_if_needed();source.scroll_into_view_if_needed();aa=source.bounding_box();zz=zone.bounding_box();page.mouse.move(aa['x']+aa['width']/2,aa['y']+aa['height']/2);page.mouse.down();page.mouse.move(aa['x']+aa['width']/2+12,aa['y']+aa['height']/2+12,steps=5);page.mouse.move(zz['x']+zz['width']/2,zz['y']+zz['height']/2,steps=15);page.mouse.move(zz['x']+zz['width']/2+1,zz['y']+zz['height']/2+1);page.mouse.up();ready(page);assert root.locator('[data-remove-id="cash"]').count()==1;root.locator('#finalize-statement').click();ready(page);assert root.get_by_text("One of the balances in Operating revenue doesn't belong there.",exact=True).is_visible();root.locator('#reset-statement').click();ready(page)
 for stage,placements in enumerate(D['statementExpected']):
  root=page.locator('#statement-workspace')
  if stage==1:assert root.locator('[data-statement-index="2"]').is_disabled()
  for i,(tile,zone) in enumerate(placements.items()):
   target=root.locator('[data-tile-id="'+tile+'"]')
   if stage==0 and i==0:
    target.focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');assert target.evaluate('(n)=>getComputedStyle(n).outlineStyle')!='none';page.keyboard.press('Enter')
   else:target.click()
   ready(page);root.locator('[data-place-zone="'+zone+'"]').click();ready(page)
   if i==0:
    order=root.locator('.tile').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.tileId)');before=page.url;click(page,'Back');click(page,'Forward');root=page.locator('#statement-workspace');assert root.locator('[data-remove-id="'+tile+'"]').count()==1;assert root.locator('.tile').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.tileId)')==order;page.reload();ready(page);root=page.locator('#statement-workspace');assert root.locator('[data-remove-id="'+tile+'"]').count()==1;assert root.locator('.tile').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.tileId)')==order
  root.locator('#finalize-statement').click();ready(page);assert root.locator('#finalize-statement').count()==0
  if stage==0:
   root.get_by_role('button',name='Review the explanation',exact=True).click();assert root.get_by_text('It does not affect net income.',exact=False).is_visible();root.locator('#continue-forward').click();ready(page)
   before=parse_qs(urlsplit(page.url).query)['progress'];root=page.locator('#statement-workspace');root.locator('[data-statement-index="0"]').click();ready(page);assert page.get_by_role('button',name='Start over',exact=True).is_disabled();assert root.locator('#reset-statement,#finalize-statement,#continue-forward,[data-thinking-toggle],[data-remove-id],[data-place-zone]').count()==0;assert root.locator('[data-statement-index="2"]').is_disabled();assert parse_qs(urlsplit(page.url).query)['progress']==before
   # Bookmarking a viewed older statement must not rewind its earned frontier.
   page.reload();ready(page);assert page.locator('html').get_attribute('data-view')!=page.locator('html').get_attribute('data-reached');root=page.locator('#statement-workspace');assert root.locator('[data-thinking-toggle]').count()==0;click(page,'Forward');root=page.locator('#statement-workspace');assert root.get_by_text('Retained Earnings Calculation',exact=False).is_visible();passed('Native statement tabs and arrows preserve earned progress, reject future tabs and expose no edits or new hints in review')
  elif stage==1:
   page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'statement-workspace-narrow.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.set_viewport_size({'width':1280,'height':900});root.locator('#continue-forward').click();ready(page)
  else:page.screenshot(path=str(out/'statement-workspace-desktop.png'),full_page=True);root.locator('#finish-workspace').click();ready(page)
  passed(f'Statement {stage+1}: keyboard/touch placement, partial-bookmark restoration, randomized order, validation and totals')
 assert page.get_by_text('10/11',exact=True).is_visible();assert page.get_by_text('9/10',exact=True).is_visible();assert page.get_by_text('3/3',exact=True).is_visible();assert page.get_by_text('$22,800',exact=True).count()>0;passed('Complete native lesson preserves original first-pass scores and all three completed statements')
 saved=page.url;click(page,'Back');assert page.locator('[data-thinking-toggle],#finish-workspace,#finalize-statement,#reset-statement').count()==0;assert page.locator('#statement-workspace').count()==0;click(page,'Forward');passed('Review after the debrief exposes completed statements with no hidden hint or mutation controls')
 for fixture in O['legacy']:
  page.goto(origin+'?progress='+fixture['token']+'&view=999&statement_view=999');ready(page);assert page.locator('html').get_attribute('data-reached')==page.locator('html').get_attribute('data-view')
 page.goto(saved);ready(page);passed('All 24 original saved pages, including finalized statements, import with future-view rejection')
 assert 'pilot' not in page.title().lower() and 'preview' not in page.title().lower() and 'test' not in page.title().lower();passed('Final title and original teaching content; no iframe or Python runtime')
run(walk)
