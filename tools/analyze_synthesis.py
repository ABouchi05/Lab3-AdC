"""Sum the mapped Liberty areas embedded by Yosys, preserving instance ownership."""
from pathlib import Path
from collections import Counter,defaultdict
import json
ROOT=Path(__file__).resolve().parents[1]
def analyze(path):
    design=json.loads(path.read_text());modules=design['modules'];cells=modules['asic_top']['cells']
    types=Counter();leaves=defaultdict(float);hierarchy=defaultdict(float);total=0;ff=0;missing=set()
    trace=[]
    for name,cell in cells.items():
        kind=cell['type'];attrs=modules.get(kind,{}).get('attributes',{})
        if 'area' not in attrs:missing.add(kind);continue
        area=float(attrs['area']);types[kind]+=1;total+=area
        ff+=int('__dff' in kind or '__sdff' in kind)
        owner=name.rsplit('.',1)[0] if '.' in name else '(top buffers)'
        leaves[owner]+=area
        parts=owner.split('.')
        for i in range(1,len(parts)+1):hierarchy['.'.join(parts[:i])]+=area
        trace.append(dict(name=name,type=kind,area_um2=area,owner=owner))
    if missing:raise ValueError(f'Area unavailable for {missing}')
    result=dict(area_um2=total,flip_flops=ff,cell_count=len(cells),top_five=types.most_common(5),
                leaf_areas_um2=dict(sorted(leaves.items(),key=lambda kv:-kv[1])),
                hierarchy_areas_um2=dict(sorted(hierarchy.items(),key=lambda kv:-kv[1])),
                counter_area_um2=hierarchy.get('u_soc.u_periph.u_cycle_counter',0),
                counter_fraction=hierarchy.get('u_soc.u_periph.u_cycle_counter',0)/total,
                method='Sum Liberty area attributes of mapped standard cells by preserved hierarchical instance name',
                source=str(path.relative_to(ROOT)))
    (path.parent/'area_analysis.json').write_text(json.dumps(result,indent=2))
    (path.parent/'instance_areas.json').write_text(json.dumps(trace,indent=2))
    return result
if __name__=='__main__':
    for path in (ROOT/'results/physical').glob('*/synthesis/asic_top.nl.v.json'):
        state=json.loads((path.parents[1]/'latest_state.json').read_text())
        if 'design__instance__area' not in state.get('metrics',{}):
            print(path.parents[1].name,'synthesis still in progress');continue
        r=analyze(path);print(path.parents[1].name,r['area_um2'],r['flip_flops'],list(r['leaf_areas_um2'].items())[:3])
