"""Render manuscript assets from existing audited CSVs; no new inference or model calls."""
from pathlib import Path
import csv,json,hashlib,shutil
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
SRC=ROOT/'paper/research_notes/analyses/final_results/run-01'
OUT=ROOT/'paper/manuscript'
PROV=Path(__file__).parent/'run-01'; PROV.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'svg.fonttype':'none'})
def read(name):
 with (SRC/name).open(newline='') as f:return list(csv.DictReader(f))
def one(rows,**sel):
 r=[r for r in rows if all(r[k]==str(v) for k,v in sel.items())]
 assert len(r)==1,(sel,len(r));return r[0]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tex(s):return s.replace('_',r'\_')
rows=read('motif_size_metrics.csv'); conditions=read('condition_metrics.csv'); pairs=read('paired_contrasts.csv'); baselines=read('analytical_baselines.csv')
models=['gemma-4-31b','qwen3.6-flash','ministral-14b']; names=['Gemma','Qwen','Ministral']
motifs=['chain','star_in','star_out','tree_in','tree_out','rhombus','hourglass']; labels=['Chain','Star-in','Star-out','Tree-in','Tree-out','Rhombus','Hourglass']
records={}; manifest=[]
def save(fig,name,selected,caption):
 paths=[]
 for ext in ['png','pdf','svg']:
  p=OUT/'figures'/f'{name}.{ext}';fig.savefig(p,dpi=300,bbox_inches='tight');paths.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
  final_dir=ROOT/'paper/figures/structural_manuscript_v1';final_dir.mkdir(exist_ok=True)
  final_path=final_dir/p.name;shutil.copyfile(p,final_path);paths.append({'path':str(final_path.relative_to(ROOT)),'sha256':sha(final_path)})
 plt.close(fig);manifest.append(dict(asset=name,files=paths,rows=selected,caption=caption))
fig,axes=plt.subplots(2,3,figsize=(7.1,3.55),sharex=True,sharey=True)
sel=[]
for j,(model,name) in enumerate(zip(models,names)):
 for i,metric in enumerate(['f1','exact']):
  ax=axes[i,j]
  for condition,noise,color,marker in [('K1','disconnected','#176c9b','o'),('K2','adjacent','#c76222','s')]:
   rs=[one(rows,series_id='core',model=model,condition=condition,noise=noise,motif=m,size=4 if m=='rhombus' else 5 if m=='hourglass' else 6) for m in motifs]
   if i==0:sel.extend(rs)
   ax.plot(range(7),[float(r[metric]) for r in rs],marker=marker,color=color,label=noise,markersize=3,linewidth=1)
  ax.axvline(4.5,color='0.6',linewidth=.7,linestyle=':');ax.set_ylim(-.03,1.04);ax.grid(axis='y',alpha=.2)
  if i==0:ax.set_title(name)
  if j==0:ax.set_ylabel('Mean set-F1' if metric=='f1' else 'Exact selection')
  if i==1:ax.set_xticks(range(7),labels,rotation=45,ha='right')
axes[0,0].legend(loc='lower left',frameon=False,fontsize=6.7)
fig.subplots_adjust(left=.07,right=.99,top=.91,bottom=.22,wspace=.15,hspace=.17)
save(fig,'motif_profiles',sel,'Core K1/K2; 100 planned tasks per motif/model/condition. First five motifs have six nodes; rhombus four and hourglass five, separated by dotted line. Descriptive all-planned means, no inferential error bars. Adjacent contexts may contain different distractors.')
fig,axes=plt.subplots(3,5,figsize=(7.1,3.65),sharey=True)
sel=[]
for i,(model,name) in enumerate(zip(models,names)):
 for j,(m,label) in enumerate(zip(motifs[:5],labels[:5])):
  ax=axes[i,j]
  for cond,color,style in [('Braw','#8d8d8d','--'),('Braw+E','#176c9b','-')]:
   rs=sorted([r for r in rows if r['series_id']=='full_braw' and r['model']==model and r['condition']==cond and r['motif']==m],key=lambda r:int(r['size']))
   sel.extend(rs);xs=[int(r['size']) for r in rs]
   ax.plot(xs,[float(r['f1']) for r in rs],color=color,linestyle=style,marker='o',markersize=2.4,linewidth=1,label='Raw' if cond=='Braw' else 'Raw+E')
   ax.set_xticks([min(xs),max(xs)])
  if i==0:ax.set_title(label)
  if j==0:ax.set_ylabel(name+'\nMean set-F1')
  if i==2:ax.set_xlabel('Nodes')
  ax.set_ylim(-.03,1.04);ax.grid(alpha=.18)
axes[0,0].legend(frameon=False,loc='lower left',fontsize=6.5)
fig.subplots_adjust(left=.085,right=.99,top=.91,bottom=.13,wspace=.15,hspace=.35)
save(fig,'size_profiles',sel,'Full Braw/Raw+E; 100 planned tasks per motif-size/model/condition. Each panel compares different frozen size strata, with 25 candidates. Descriptive all-planned F1, no inferential error bars; exact endpoint results are in Appendix Table 5.')
# Table 2: condition contrasts, existing simultaneous bands, no new interval computation.
lines=[r'\begin{tabular}{llrr}',r'\toprule',r'Model & Contrast & $\Delta$F1 & Simultaneous band \\',r'\midrule'];sel=[]
for model,name in zip(models,names):
 for panel,c,label in [('raw','raw_explicit','Raw+E $-$ Raw'),('core','noise_triples','Adjacent $-$ disc., triples'),('core','noise_text','Adjacent $-$ disc., text')]:
  r=one(pairs,panel=panel,model=model,contrast=c,metric='f1');sel.append(r)
  lines.append(f"{name} & {label} & {float(r['delta']):+.3f} & [{float(r['simultaneous_low']):.3f}, {float(r['simultaneous_high']):.3f}]" + r" \\")
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/condition_effects.tex').write_text('\n'.join(lines)+'\n');records['table_condition_effects']=sel
# Full Core absolute scores; F1 / exact, not confidence intervals.
lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Condition & Gemma & Qwen & Ministral \\',r'\midrule'];sel=[]
for cond in ['K0','K1','K2','K3','K4','K5','K6','K7','K8','K5k','R0','R1-matched','R2-matched']:
 vals=[]
 for model in models:
  r=one(conditions,series_id='core',model=model,condition=cond,noise='adjacent' if cond in ['K2','K6','R2-matched'] else 'disconnected');sel.append(r);vals.append(f"{float(r['f1']):.3f} / {float(r['exact']):.3f}")
 lines.append(tex(cond)+' & '+' & '.join(vals)+r' \\')
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/core_summary.tex').write_text('\n'.join(lines)+'\n');records['table_core_summary']=sel
# All five variable-size families, both endpoints; E condition F1 and exact.
lines=[r'\begin{tabular}{llcrrrr}',r'\toprule',r'Model & Family & Sizes & F1$_{s}$ & F1$_{l}$ & Exact$_s$ & Exact$_l$ \\',r'\midrule'];sel=[]
for model,name in zip(models,names):
 for m,label in zip(motifs[:5],labels[:5]):
  rs=sorted([r for r in rows if r['series_id']=='full_braw' and r['model']==model and r['condition']=='Braw+E' and r['motif']==m],key=lambda r:int(r['size']));a,b=rs[0],rs[-1];sel.extend([a,b]);vals=[float(a['f1']),float(b['f1']),float(a['exact']),float(b['exact'])]
  lines.append(f"{name} & {label} & {a['size']}--{b['size']} & "+' & '.join(format(Decimal(str(v)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), '.3f') for v in vals)+r' \\')
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/size_endpoints.tex').write_text('\n'.join(lines)+'\n');records['table_size_endpoints']=sel
# Render the four controlled presentation estimates in a small appendix table.
lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Contrast & Gemma & Qwen & Ministral \\',r'\midrule'];sel=[]
for c,label in [('format_slots','Text $-$ triples, steps'),('format_goal','Text $-$ triples, direct'),('placement_object','Destination $-$ source'),('placement_both','Both $-$ source')]:
 vals=[]
 for model in models:
  r=one(pairs,panel='core',model=model,contrast=c,metric='f1');sel.append(r);vals.append(f"{float(r['delta']):+.3f}")
 lines.append(label+' & '+' & '.join(vals)+r' \\')
lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables/presentation.tex').write_text('\n'.join(lines)+'\n');records['table_presentation']=sel
# Existing simple reference rules, preserving their exact labels as provenance only.
shutil.copyfile(SRC/'tables/analytical_baselines.tex',OUT/'tables/analytical_baselines.tex');records['table_baselines']=baselines
payload={'figures':manifest,'tables':records,'sources':{f:sha(SRC/f) for f in ['motif_size_metrics.csv','condition_metrics.csv','paired_contrasts.csv','analytical_baselines.csv']},'script_sha256':sha(Path(__file__)),'new_inference':False,'metric_policy':'All planned N; invalid/missing contributes zero; cached audited scores; descriptive motif/size profiles'}
(PROV/'asset_sources.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps({'figures':len(manifest),'tables':len(records),'new_inference':False}))
