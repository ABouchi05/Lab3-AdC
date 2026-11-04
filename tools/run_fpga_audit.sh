#!/usr/bin/env bash
set -euo pipefail
reference=/opt/lab3/fpga_reference
if ! test -d "$reference/.git"; then
 git clone https://github.com/ABouchi05/Lab2-AdC.git "$reference"
 git -C "$reference" checkout 4a0a9128566306269fa97b195bb28ef2fa42885f
fi
python3 - <<'PY'
import json
from pathlib import Path
cfg=json.loads(Path('config/rom_100_40.json').read_text())
cfg['DESIGN_NAME']='game_top';cfg['CLOCK_PORT']='i_Clk'
cfg['VERILOG_FILES']=[str(p) for p in Path('/opt/lab3/fpga_reference/rtl').rglob('*.v')]
for key in ['SYNTH_PARAMETERS','IO_PIN_ORDER_CFG']:cfg.pop(key,None)
Path('config/fpga_audit.json').write_text(json.dumps(cfg,indent=2))
PY
set +e
librelane --pdk gf180mcuD --run-tag fpga_audit --to Yosys.Synthesis config/fpga_audit.json > results/fpga_audit.log 2>&1
status=$?
set -e
echo "$status" > results/fpga_audit_exit_code.txt
echo "FPGA reference audit exit=$status (failure is expected because the original contains FPGA primitives)"
