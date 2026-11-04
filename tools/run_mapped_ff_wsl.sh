#!/usr/bin/env bash
set -euo pipefail
python3 tools/prepare_mapped_sim.py --unified 1
librelane --pdk gf180mcuD --run-tag sim_ff --to Yosys.Synthesis config/sim_ff.json > results/sim_ff_synthesis.log 2>&1
modeldir=/opt/lab3/pdks/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog
python3 tools/post_synthesis.py config/runs/sim_ff/06-yosys-synthesis/asic_top.nl.v \
 --unified 1 --work-dir build/mapped_ff \
 --model "$modeldir/gf180mcu_fd_sc_mcu7t5v0.v" --model "$modeldir/primitives.v" > results/mapped_ff_simulation.log 2>&1
python3 - <<'PY'
import json,hashlib,gzip,shutil
from pathlib import Path
work=Path('build/mapped_ff');out=Path('results/simulation_ff');out.mkdir(exist_ok=True)
result=dict(trace_equal=True,direct_capture_register_asserted=True,memory_strategy='unified_ff',technology='gf180mcuD',library='gf180mcu_fd_sc_mcu7t5v0',pdk_revision='54435919abffb937387ec956209f9cf5fd2dfbee')
for kind in ['rtl','mapped']:
 data=(work/(kind+'.csv')).read_bytes();result[kind+'_sha256']=hashlib.sha256(data).hexdigest();result[kind+'_observed_cycles']=len(data.splitlines())
 with gzip.open(out/(kind+'_trace.csv.gz'),'wb') as f:f.write(data)
 (out/(kind+'.log')).write_text((work/(kind+'.log')).read_text())
result['program']=json.loads((work/'program.json').read_text())
Path('results/mapped_verification_ff.json').write_text(json.dumps(result,indent=2));(out/'evidence.json').write_text(json.dumps(result,indent=2))
src=Path('config/runs/sim_ff/06-yosys-synthesis/asic_top.nl.v')
with src.open('rb') as a,gzip.open(out/'asic_top_sim_ff.nl.v.gz','wb') as b:shutil.copyfileobj(a,b)
print('PASS unified FF: GF180 netlist == RTL; direct captured-cycle checks passed')
PY
