"""Collect actual LibreLane states and synthesis evidence; never infer missing metrics."""
import argparse, json, re, shutil, hashlib, gzip
from pathlib import Path

def copy_file(source,target):
    source=Path(source);target=Path(target)
    if source.suffix=='.rpt' and source.stat().st_size>250000:
        compressed=target.with_suffix(target.suffix+'.gz')
        if compressed.exists():return
        temporary=compressed.with_suffix('.gz.tmp')
        with source.open('rb') as src,gzip.open(temporary,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst)
        temporary.replace(compressed)
        return
    # Step outputs are immutable once written; logs may keep growing.
    if target.exists() and source.suffix!='.log' and source.stat().st_size==target.stat().st_size:
        return
    shutil.copy2(source,target)

def paths_in_report(text):
    rows=[]
    corner='unknown'
    for chunk in re.split(r'(?=Startpoint:)',text):
        corners=re.findall(r'={3,}\s*(\S+) Corner',chunk)
        current=corner
        if not chunk.startswith('Startpoint:'):
            if corners:corner=corners[-1]
            continue
        start=re.search(r'Startpoint:\s*(.*)',chunk)
        end=re.search(r'Endpoint:\s*(.*)',chunk)
        slack=re.search(r'([-+]?\d+\.\d+)\s+slack\s+\((?:MET|VIOLATED)\)',chunk)
        group=re.search(r'Path Group:\s*(.*)',chunk)
        if start and end and slack:
            rows.append(dict(corner=current,start=start[1].strip(),end=end[1].strip(),
                             slack_ns=float(slack[1]),group=group[1].strip() if group else None))
        if corners:corner=corners[-1]
    return sorted(rows,key=lambda r:r['slack_ns'])

def collect(runs,out):
    out.mkdir(parents=True,exist_ok=True);summary=[]
    for run in sorted(runs.iterdir()):
        if not run.is_dir():continue
        states=sorted(run.glob('*/state_out.json'),key=lambda p:int(p.parent.name.split('-')[0]) if p.parent.name.split('-')[0].isdigit() else -1)
        if not states:continue
        last=states[-1];state=json.loads(last.read_text());m=state.get('metrics',{})
        tag=run.name;dest=out/tag;dest.mkdir(exist_ok=True)
        (dest/'latest_state.json').write_text(json.dumps(state,indent=2))
        cfg=run/'config.json'
        if cfg.exists():copy_file(cfg,dest/'resolved_config.json')
        row=dict(tag=tag,stage=last.parent.name,has_final=(run/'final').is_dir(),metrics=m,
                 metrics_source=str(last),critical_paths=[])
        required=['timing__setup__ws','timing__setup__tns','timing__hold__ws','timing__hold__tns',
                  'magic__drc_error__count','design__lvs_error__count','antenna__violating__nets','antenna__violating__pins']
        row['meets_project_criteria']=None
        if all(key in m for key in required):
            row['meets_project_criteria']=bool(row['has_final'] and m['timing__setup__ws']>=0 and m['timing__hold__ws']>=0
                and all(m[key]==0 for key in required if not key.endswith('__ws')))
        for source in ['config.json','resolved.json']:
            if (run/source).exists():copy_file(run/source,dest/source)
        synth=next(iter(run.glob('*-yosys-synthesis')),None)
        if synth and (synth/'state_out.json').exists():
            d=dest/'synthesis';d.mkdir(exist_ok=True)
            for f in (synth/'reports').glob('*'):
                if f.suffix in ['.json','.rpt']:copy_file(f,d/f.name)
            for name in ['asic_top.nl.v','asic_top.nl.v.json','asic_top.nl.v.hierarchy.nl.v','yosys-synthesis.log','config.json']:
                if (synth/name).exists():copy_file(synth/name,d/name)
        sta=[p for p in run.iterdir() if p.is_dir() and 'sta' in p.name and (p/'state_out.json').exists() and list(p.rglob('max.rpt'))]
        sta.sort(key=lambda p:int(p.name.split('-')[0]))
        if sta:
            d=dest/'timing'/sta[-1].name;d.mkdir(parents=True,exist_ok=True)
            for f in sta[-1].rglob('*.rpt'):
                target=d/f.relative_to(sta[-1]);target.parent.mkdir(parents=True,exist_ok=True);copy_file(f,target)
            row['timing_source']=str(sta[-1])
            cache=d/'critical_paths.json'
            if cache.exists():row['critical_paths']=json.loads(cache.read_text())
            else:
                paths=[]
                for f in sta[-1].rglob('max.rpt'):
                    paths.extend(paths_in_report(f.read_text()))
                row['critical_paths']=sorted(paths,key=lambda r:r['slack_ns'])[:30]
                cache.write_text(json.dumps(row['critical_paths'],indent=2))
        log=runs.parent.parent/'results'/f'{tag}.log'
        resumed=runs.parent.parent/'results'/f'{tag}_antenna_repair.log'
        if resumed.exists():log=resumed
        if log.exists():
            txt=log.read_text(errors='replace');row['flow_complete_message']='Flow complete.' in txt
            copy_file(log,dest/'flow.log')
        if not row.get('flow_complete_message',False) and row['meets_project_criteria']:
            row['meets_project_criteria']=False
        for view in ['gds','def','odb','nl','sdc','klayout_gds','mag_gds','render','lef','spice']:
            src=state.get(view)
            if tag=='rom_100_40' and isinstance(src,str) and Path(src).exists() and (run/'final').exists():
                d=dest/'final';d.mkdir(exist_ok=True);copy_file(src,d/Path(src).name)
        # Keep actual signoff evidence, including report coordinates if a violation occurred.
        for step in run.iterdir():
            if not step.is_dir() or not any(x in step.name for x in ['magic-drc','netgen-lvs','checkantennas','repairantennas','reportmanufacturability']):continue
            for f in step.rglob('*'):
                if f.is_file() and f.suffix in ['.rpt','.json','.log','.xml','.txt'] and f.stat().st_size<10000000:
                    target=dest/'signoff'/step.name/f.relative_to(step);target.parent.mkdir(parents=True,exist_ok=True);copy_file(f,target)
        summary.append(row)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    for row in summary:
        m=row['metrics'];print(row['tag'],row['stage'],'complete=',row.get('flow_complete_message'),
          'area=',m.get('design__instance__area'),'setup=',m.get('timing__setup__ws'),
          'hold=',m.get('timing__hold__ws'),'drc=',m.get('magic__drc_error__count'),
          'lvs=',m.get('design__lvs_error__count'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,default=Path('/opt/lab3/design/config/runs'))
    p.add_argument('--out',type=Path,default=Path('results/physical'));a=p.parse_args();collect(a.runs,a.out)
