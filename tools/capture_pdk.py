"""Fingerprint the exact installed PDK library and simulation models used by the run."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads(Path('/opt/lab3/design/config/runs/rom_100_40/resolved.json').read_text())
files=set()
for key in ['LIB','TECH_LEFS','CELL_LEFS','CELL_GDS']:
 value=cfg.get(key,[])
 if isinstance(value,dict):value=list(value.values())
 def walk(v):
  if isinstance(v,str):files.add(v)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(value)
for paths in cfg['LIB'].values():
 for lib in paths:
  base=Path(lib).parents[1]/'verilog'
  files.update(str(f) for f in base.glob('*.v'))
sources=Path(cfg['PDK_ROOT'])/cfg['PDK']/'SOURCES'
if sources.exists():files.add(str(sources))
manifest={'pdk':cfg['PDK'],'bundle_revision':Path(cfg['PDK_ROOT']).name,'standard_cell_library':cfg['STD_CELL_LIBRARY'],'files':{}}
for name in sorted(files):
 p=Path(name)
 if p.is_file():manifest['files'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
(ROOT/'results/pdk_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Fingerprint recorded for',len(manifest['files']),'PDK/library/model inputs')
