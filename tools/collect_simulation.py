"""Archive real mapped-simulation traces and netlist without changing their bytes."""
import gzip,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
design=Path('/opt/lab3/design');out=ROOT/'results/simulation';out.mkdir(exist_ok=True)
proof=json.loads((design/'results/mapped_verification.json').read_text())
for kind in ['rtl','mapped']:
 src=design/'build/mapped'/f'{kind}.csv';content=src.read_bytes()
 if hashlib.sha256(content).hexdigest()!=proof[kind+'_sha256']:raise RuntimeError('Trace proof mismatch')
 with gzip.open(out/f'{kind}_trace.csv.gz','wb',compresslevel=6) as f:f.write(content)
src=design/'config/runs/sim_rom/06-yosys-synthesis/asic_top.nl.v'
with src.open('rb') as a,gzip.open(out/'asic_top_sim.nl.v.gz','wb') as b:shutil.copyfileobj(a,b)
shutil.copyfile(design/'build/mapped/program.json',out/'program.json')
(out/'evidence.json').write_text(json.dumps(proof,indent=2))
print('Archived verified GF180 traces and netlist',out)
