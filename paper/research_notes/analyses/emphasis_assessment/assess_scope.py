"""Bounded descriptive assessment of existing motif/size results; no new inference."""
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / 'paper/research_notes'
SOURCE = NOTES / 'analyses/final_results/run-01/motif_size_metrics.csv'
OUT = Path(__file__).parent / 'run-01'
OUT.mkdir(exist_ok=False)
with SOURCE.open(newline='') as f:
    all_rows = list(csv.DictReader(f))
rows = [r for r in all_rows if r['series_id'] in ['core', 'size', 'full_braw']]
coverage = collections.defaultdict(dict)
for r in rows:
    key = tuple(r[k] for k in ['series_id','model','condition','noise'])
    coverage[key].setdefault(r['motif'], []).append(dict(size=int(r['size']),N=int(r['N']),valid=int(r['valid'])))
cover = [dict(series_id=k[0],model=k[1],condition=k[2],noise=k[3],motifs={m:sorted(cells,key=lambda x:x['size']) for m,cells in sorted(v.items())}) for k,v in sorted(coverage.items())]
endpoints=[]
for panel,conds in [('full_braw',['Braw','Braw+E']),('size',['K1','K5'])]:
    for c in conds:
        for model in sorted({r['model'] for r in rows if r['series_id']==panel}):
            for motif in sorted({r['motif'] for r in rows if r['series_id']==panel}):
                seq=sorted([r for r in rows if r['series_id']==panel and r['condition']==c and r['model']==model and r['motif']==motif],key=lambda x:int(x['size']))
                if len(seq)<2:continue
                endpoints.append(dict(series_id=panel,model=model,condition=c,motif=motif,smallest=seq[0],largest=seq[-1],f1_endpoint_difference=float(seq[-1]['f1'])-float(seq[0]['f1']),strictly_decreasing_f1=all(float(b['f1'])<float(a['f1']) for a,b in zip(seq,seq[1:])),nonincreasing_f1=all(float(b['f1'])<=float(a['f1']) for a,b in zip(seq,seq[1:])),interpretation='Descriptive comparison of different size strata; not a paired effect, monotonicity test or significance claim'))
errors=collections.defaultdict(collections.Counter)
bases=collections.defaultdict(set)
with gzip.open(ROOT/'results/observations.jsonl.gz','rt') as f:
    for line in f:
        o=json.loads(line)
        if o['series_id'] not in ['core','size','full_braw']:continue
        k=tuple(o[x] for x in ['series_id','model','condition','noise','motif','size'])
        z=errors[k];z['N']+=1
        bases[(o['series_id'],o['model'],o['condition'],o['noise'])].add(o['base_id'])
        if not o['valid']:
            z['invalid']+=1;continue
        met=o['metrics'];fp=met['fp'];fn=met['fn']
        category='exact' if fp==fn==0 else 'omission_only' if fp==0 else 'inclusion_only' if fn==0 else 'mixed'
        z[category]+=1
        z['f1_sum']+=met['f1']
err=[]
for k,z in sorted(errors.items()):
    assert sum(z[x] for x in ['invalid','exact','omission_only','inclusion_only','mixed'])==z['N']
    err.append(dict(zip(['series_id','model','condition','noise','motif','size'],k))|dict(z))
# Independent aggregate cross-check against the existing detailed CSV, no rescoring.
lookup={tuple(r[x] if x!='size' else int(r[x]) for x in ['series_id','model','condition','noise','motif','size']):r for r in rows}
maxdiff=0
for k,z in errors.items():
    r=lookup[k];assert int(r['N'])==z['N'];maxdiff=max(maxdiff,abs(float(r['f1'])-z['f1_sum']/z['N']))
assert maxdiff<1e-12
same_size=[r for r in rows if r['size']=='6' and ((r['series_id']=='core' and r['condition'] in ['K1','K2','K5','K6']) or (r['series_id']=='full_braw' and r['condition'] in ['Braw','Braw+E']))]
summary=dict(schema_version=1,checked_on='2026-10-25',scope='Descriptive scope assessment, not new model experiments, inference or raw-response reparse',coverage=cover,size_endpoints=endpoints,size6_rows=same_size,error_categories=err,base_overlap=[dict(model=m,core_K1_bases=len(bases[('core',m,'K1','disconnected')]),full_BrawE_bases=len(bases[('full_braw',m,'Braw+E','disconnected')]),intersection=len(bases[('core',m,'K1','disconnected')]&bases[('full_braw',m,'Braw+E','disconnected')])) for m in ['gemma-4-31b','qwen3.6-flash','ministral-14b']],baseline_size_note='For select-all among 25 candidates and |W|=s, F1=2s/(25+s), so increasing target size changes metric reference points even with a fixed pool.',validation=dict(status='passed',detailed_groups_checked=len(errors),max_cached_F1_aggregation_difference=maxdiff,categories='Mutually exclusive valid fp/fn categories plus invalid; invalid not assigned a scientific omission/inclusion interpretation'))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
sourcepaths=[SOURCE,ROOT/'results/observations.jsonl.gz',ROOT/'results/SOURCES.json',Path(__file__)]
(OUT/'provenance.json').write_text(json.dumps(dict(source_revision='3f4b7b9baccd1a369a9665507883a7c0152f52e3',working_tree='Prior contribution/outline edits retained; new assessment derived separately',files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sourcepaths},method='Stream saved observations; aggregate cached F1 and fp/fn; select existing motif/size rows; no independence tests or fitted regression'),indent=2)+'\n')
print(json.dumps(summary['validation']))
print('Overlap',summary['base_overlap'])
