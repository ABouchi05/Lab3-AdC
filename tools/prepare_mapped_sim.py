import json,argparse
from pathlib import Path
from generate import generate
ROOT=Path(__file__).resolve().parents[1]
generate('sim',ROOT/'build/verify')
parser=argparse.ArgumentParser();parser.add_argument('--unified',type=int,choices=[0,1],default=0);args=parser.parse_args()
cfg=json.loads((ROOT/'config/rom_100_40.json').read_text())
cfg['SYNTH_PARAMETERS']=[f'Unified={args.unified}']
cfg['VERILOG_FILES']=[s.replace('rtl/generated/asic_memory.v','build/verify/asic_memory.v') for s in cfg['VERILOG_FILES']]
(ROOT/'config'/('sim_ff.json' if args.unified else 'sim_rom.json')).write_text(json.dumps(cfg,indent=2))
