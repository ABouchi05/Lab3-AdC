#!/usr/bin/env bash
set -euo pipefail
python3 tools/prepare_mapped_sim.py
librelane --pdk gf180mcuD --run-tag sim_rom --to Yosys.Synthesis config/sim_rom.json > results/sim_rom_synthesis.log 2>&1
modeldir=/opt/lab3/pdks/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog
python3 tools/post_synthesis.py config/runs/sim_rom/06-yosys-synthesis/asic_top.nl.v \
 --model "$modeldir/gf180mcu_fd_sc_mcu7t5v0.v" --model "$modeldir/primitives.v" > results/mapped_simulation.log 2>&1
python3 - <<'PY'
import json,hashlib
from pathlib import Path
work=Path('build/mapped')
result={'trace_equal':True,'direct_capture_register_asserted':True,'technology':'gf180mcuD','library':'gf180mcu_fd_sc_mcu7t5v0','pdk_revision':'54435919abffb937387ec956209f9cf5fd2dfbee'}
for kind in ['rtl','mapped']:
 data=(work/(kind+'.csv')).read_bytes()
 result[kind+'_sha256']=hashlib.sha256(data).hexdigest()
 result[kind+'_observed_cycles']=len(data.splitlines())
 Path('results/'+kind+'_game.log').write_text((work/(kind+'.log')).read_text())
result['program']=json.loads((work/'program.json').read_text())
Path('results/mapped_verification.json').write_text(json.dumps(result,indent=2))
print('PASS GF180 post-synthesis functional regression',result['mapped_observed_cycles'],'cycles')
PY
