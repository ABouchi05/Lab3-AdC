"""Scientific plot from actual routing metrics, not estimated congestion."""
import json,re,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'build/mpl_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=json.loads((ROOT/'results/physical/summary.json').read_text())
points=[]
for row in rows:
 match=re.fullmatch(r'rom_100_(\d+)',row['tag']);m=row['metrics']
 if not match or 'route__drc_errors__iter:0' not in m:continue
 logic=m['design__instance__area']-sum(m.get('design__instance__area__class:'+name,0) for name in ['fill_cell','tap_cell','endcap_cell'])
 points.append((100*logic/m['design__core__area'],m['route__drc_errors__iter:0'],int(match[1])))
points.sort();out=ROOT/'results/plots';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,ax=plt.subplots(figsize=(7.2,3.25),layout='constrained')
ax.plot([p[0] for p in points],[p[1] for p in points],color='#28608a',marker='o',linewidth=1.8)
for x,y,u in points:ax.annotate(f'U objetivo {u}%',(x,y),xytext=(4,8),textcoords='offset points',fontsize=9)
ax.set_xlabel('Utilización lógica final sin fill/tap/endcap (%)')
ax.set_ylabel('Violaciones de ruteo, iteración 0')
ax.set_title('Utilización y dificultad del ruteo a 100 ns',loc='left',weight='bold')
ax.grid(axis='y',alpha=.22);ax.spines[['top','right']].set_visible(False);ax.margins(x=.17,y=.25)
fig.savefig(out/'utilizacion_congestion.png',dpi=220);plt.close(fig)
(out/'plot_data.json').write_text(json.dumps([dict(util_logic_pct=x,route_drc_iter0=y,target_util_pct=u) for x,y,u in points],indent=2))
print(out/'utilizacion_congestion.png')
