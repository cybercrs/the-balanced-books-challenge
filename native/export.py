"""Export original Balanced Books teaching screens, native workspace and Python oracles."""
import ast,json,sys
from pathlib import Path
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'native'))
from capture import Recorder,State,Container,flat
from balanced_books import case_data as c,engine as e,progress as p
source=(ROOT/'streamlit_app.py').read_text();tree=ast.parse(source);driver=next(n.lineno for n in tree.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='initialize_state')
# Strip only the component wrapper import; every renderer declaration is original.
nodes=[n for n in tree.body if n.lineno<driver and not (isinstance(n,ast.ImportFrom) and n.module=='balanced_books.statement_builder_component')];rec=Recorder();previous=sys.modules.get('streamlit');sys.modules['streamlit']=rec;ns={}
try:exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/'streamlit_app.py'),'exec'),ns)
finally:
 if previous is None:sys.modules.pop('streamlit',None)
 else:sys.modules['streamlit']=previous
rec.container=lambda **kw:Container(rec,rec.node('column',children=[]));rec.progress=lambda value,text:rec.node('progress',value=value,text=text)
ns['render_scroll_to_top_component']=lambda **kw:None
# Run the original wrapper with a build-only sink to obtain its account/derived args.
wsource=(ROOT/'balanced_books/statement_builder_component.py').read_text();wtree=ast.parse(wsource);wns={};exec(compile(ast.Module(body=[n for n in wtree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) and not (isinstance(n,ast.Import) and any(a.name.startswith('streamlit') for a in n.names))],type_ignores=[]),'<wrapper>','exec'),wns)
args={};wns['_statement_builder']=lambda **kw:args.update(kw);wns['render_statement_builder_component'](e.balances_after(),e.statement_values_from_balances(e.balances_after()),initial_progress=None,key='workspace');ns['render_statement_builder_component']=lambda *a,**kw:None
transactions=[asdict(t) for t in c.TRANSACTIONS];recordable=[asdict(t) for t in c.RECORDABLE_TRANSACTIONS]
def state(stage,index,status):
 s=State(p.activity_defaults());s.bbc_stage=stage;s.bbc_inbox_index=len(c.TRANSACTIONS)-1 if stage>1 else index if stage==1 else 0;s.bbc_equation_index=len(c.RECORDABLE_TRANSACTIONS)-1 if stage>2 else index if stage==2 else 0
 for group,items in [('inbox',c.TRANSACTIONS),('equation',c.RECORDABLE_TRANSACTIONS)]:
  groupstage=1 if group=='inbox' else 2
  for i,t in enumerate(items):
   if groupstage<stage or groupstage==stage and (i<index or i==index and status!='unanswered'):
    answer=t.event_type if group=='inbox' else t.correct_choice;opts=c.EVENT_TYPE_OPTIONS if group=='inbox' else t.choices
    selected=answer if i<index or groupstage<stage or status=='correct' else next(x for x in opts if x!=answer)
    s[f'bbc_{group}_responses'][t.id]=selected;s[f'bbc_{group}_feedback'][t.id]=(e.evaluate_event_type if group=='inbox' else e.evaluate_equation_choice)(t,selected)
 if stage==4:s.bbc_statement_completion={'statementsFinalized':3,'attempts':3}
 return s
positions=[(0,0)]+[(1,i) for i in range(len(c.TRANSACTIONS))]+[(2,i) for i in range(len(c.RECORDABLE_TRANSACTIONS))]+[(3,0),(4,0)];screens=[]
for stage,index in positions:
 variants={}
 for status in ['unanswered','wrong','correct']:
  rec.session_state=state(stage,index,status)
  with rec.capture() as items:ns[['render_welcome','render_transaction_inbox','render_equation_lab','render_statement_builder','render_debrief'][stage]]()
  variants[status]=flat(items)
 screens.append({'stage':stage,'index':index,'variants':variants})
rec.session_state=state(0,0,'unanswered')
with rec.capture() as hero:ns['render_header']()
# Completed statement HTML is exported separately so review exposes all completed work.
completed=[]
for name in ['Income Statement','Retained Earnings Statement','Classified Balance Sheet']:
 originalradio=rec.radio;rec.radio=lambda *a,**kw:name
 with rec.capture() as items:ns['render_completed_statements']()
 completed.extend(items);rec.radio=originalradio
DATA={'hero':hero,'stages':list(ns['STAGE_LABELS']),'positions':positions,'screens':screens,'transactions':transactions,'recordable':recordable,'eventOptions':list(c.EVENT_TYPE_OPTIONS),'statementArgs':args,'completed':completed,'statementExpected':list(p.STATEMENT_EXPECTED),'statementZones':[sorted(z) for z in p.STATEMENT_ZONES]}
(ROOT/'native/content.js').write_text('export const DATA = '+json.dumps(DATA,ensure_ascii=False,separators=(',',':'))+';\n');(ROOT/'native/original.css').write_text(ns['APP_CSS'].strip().removeprefix('<style>').removesuffix('</style>'))
# Reuse the accepted readonly statement-view correction, then remove all kernel/frame wiring.
from component_adapter import adapt_frontend
frontend=(ROOT/'balanced_books/statement_builder_frontend/index.html').read_text();adapted=adapt_frontend(frontend);css=adapted.split('<style>',1)[1].split('</style>',1)[0].replace(':root',':host').replace('html, body',':host');css+='\nbutton{min-height:44px;}button:focus-visible{outline:2px solid var(--blue);outline-offset:3px;} .remove{min-width:44px;min-height:44px;}\n'
script=adapted.split('<script>',1)[1].split('</script>',1)[0];start=script.index('    function post(');end=script.index('    function money(',start);script=script[:start]+'''    function setHeight() {}
    function setComponentValue(value) { onChange({...value,thinkingOpen:[...state.thinkingOpen]}); }
'''+script[end:];script=script[:script.index('    window.addEventListener("message"')];script=script.replace('state.thinkingOpen[state.stage] = !state.thinkingOpen[state.stage];','state.thinkingOpen[state.stage] = !state.thinkingOpen[state.stage];\n        onThinking([...state.thinkingOpen]);')
for name in ['placeTile','toggleTile','removeTile','resetCurrent','finalizeCurrent','continueForward','finishWorkspace']:
 marker='    function '+name+'('
 start=script.index(marker);body=script.index('{',start)
 guard='\n      if (state.stage < state.earnedStage) return;'
 if name=='finalizeCurrent':guard+='\n      if (state.finalized[state.stage]) return;'
 if name=='continueForward':guard+='\n      if (!state.finalized[state.stage]) return;'
 if name=='finishWorkspace':guard+='\n      if (!state.finalized.every(Boolean)) return;'
 script=script[:body+1]+guard+script[body+1:]
script+='''
    state.args = args;
    const initialProgress = args.initialProgress;
    const accountsById = new Map((args.accounts || []).map(account => [account.id, account]));
    const savedOrder = initialProgress?.shuffledAccountIds || [];
    state.shuffledAccounts = savedOrder.length === accountsById.size ? savedOrder.map(id => accountsById.get(id)).filter(Boolean) : shuffledCopy(args.accounts || []);
    restoreProgress(initialProgress);state.earnedStage = state.stage;
    const savedView=Number(args.browserView);
    if(args.browserView!==null&&args.browserView!==undefined&&Number.isInteger(savedView)&&savedView>=0&&savedView<=state.earnedStage)state.stage=savedView;
    state.thinkingOpen=args.thinkingOpen||[false,false,false];state.initialized=true;
    render(false);emitProgress();
'''
(ROOT/'native/statement-builder.js').write_text('''/** Native DOM workspace. No iframe, kernel, or message bridge. */
export function mount(target,args,onChange,onThinking){
 const document=target.attachShadow({mode:'open'});document.innerHTML='<style>'+'''+json.dumps(css)+'''+ '</style><main id="root" aria-live="polite"></main>';
'''+script+'\n}\n')
oracles={'balances':[{'ids':[t.id for t in c.RECORDABLE_TRANSACTIONS[:i]],'balances':e.balances_after([t.id for t in c.RECORDABLE_TRANSACTIONS[:i]]),'equation':e.equation_components(e.balances_after([t.id for t in c.RECORDABLE_TRANSACTIONS[:i]]))} for i in range(len(c.RECORDABLE_TRANSACTIONS)+1)],'statementValues':e.statement_values_from_balances(e.balances_after()),'legacy':[]}
for stage,index in positions:
 if stage==4:continue
 s=state(stage,index,'unanswered');oracles['legacy'].append({'stage':stage,'index':index,'token':p.encode_snapshot(p.snapshot_from_session(s))})
s=state(4,0,'correct');s.bbc_statement_progress={'stage':2,'finalized':[True]*3,'placements':list(p.STATEMENT_EXPECTED),'selected':None,'attempts':[1]*3,'feedbackKinds':['success']*3,'shuffledAccountIds':list(p.ACCOUNT_IDS)};s.bbc_statement_completion={'completed':True,'statementsFinalized':3,'attempts':3};oracles['legacy'].append({'stage':4,'index':0,'token':p.encode_snapshot(p.snapshot_from_session(s))})
(ROOT/'native/tests/python-oracles.json').write_text(json.dumps(oracles,indent=2)+'\n');print('Exported',len(positions),'original lesson pages and the native three-statement workspace')
