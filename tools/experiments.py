"""Generate reproducible LibreLane experiment inputs. Runs require Linux/WSL2."""
import argparse, json, subprocess, hashlib, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(); p.add_argument('--run',action='store_true')
 p.add_argument('--skip',default=''); p.add_argument('--only',default=''); p.add_argument('--jobs',type=int,default=1)
 p.add_argument('--manifest',default='experiments.json')
 a=p.parse_args()
 files=[x for x in sorted((ROOT/'rtl').rglob('*.v')) if x.name not in ['game_top.v','pochoco_ram.v']]
 matrix=[('rom_100_40',0,100,40),('ff_100_40',1,100,40),
         ('rom_80_40',0,80,40),('rom_60_40',0,60,40),
         ('rom_100_30',0,100,30),('rom_100_50',0,100,50),('rom_fast_100_40',0,100,40),
         ('rom_40_40',0,40,40),('rom_30_40',0,30,40),
         ('ff_60_40',1,60,40),('ff_40_40',1,40,40),('rom_100_60',0,100,60)]
 matrix += [('rom_63_40',0,63,40),('rom_62_40',0,62,40)]
 matrix += [('ff_100_20',1,100,20),('ff_60_20',1,60,20),('ff_40_20',1,40,20)]
 matrix += [('ffp_100_40',1,100,40),('ffp_60_40',1,60,40),('ffp_40_40',1,40,40)]
 matrix += [('ffq_100_40',1,100,40),('ffq_60_40',1,60,40),('ffq_40_40',1,40,40)]
 manifest=[]
 for tag,unified,period,util in matrix:
  config=dict(DESIGN_NAME='asic_top',VERILOG_FILES=['dir::../'+str(f.relative_to(ROOT)).replace('\\','/') for f in files],
    CLOCK_PORT='clk_i',CLOCK_PERIOD=period,FP_CORE_UTIL=util,
    PDK='gf180mcuD',STD_CELL_LIBRARY='gf180mcu_fd_sc_mcu7t5v0',
    SYNTH_PARAMETERS=[f'Unified={unified}'],SYNTH_HIERARCHY_MODE='deferred_flatten',
    IO_PIN_ORDER_CFG='dir::pins.cfg',TIMING_VIOLATION_CORNERS=['*'],
    SETUP_VIOLATION_CORNERS=['*'],HOLD_VIOLATION_CORNERS=['*'])
  dest=ROOT/'config'/f'{tag}.json'; dest.write_text(json.dumps(config,indent=2))
  if 'fast' in tag:
   config['VERILOG_DEFINES']=['ASIC_FAST_ADD']
   dest.write_text(json.dumps(config,indent=2))
  if tag.startswith(('ffp_','ffq_')):
   config.update(GPL_CELL_PADDING=4,DPL_CELL_PADDING=4)
   if tag.startswith('ffq_'):
    config['PL_TARGET_DENSITY_PCT']=60
    config['DRT_ANTENNA_REPAIR_ITERS']=10
   dest.write_text(json.dumps(config,indent=2))
  manifest.append(dict(tag=tag,unified=unified,period_ns=period,util_pct=util,
                       config_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
 dest_manifest=ROOT/'results'/a.manifest
 old={r['tag']:r for r in json.loads(dest_manifest.read_text())} if dest_manifest.exists() else {}
 for row in manifest:
  for key in ['returncode','elapsed_seconds']:
   if key in old.get(row['tag'],{}):row[key]=old[row['tag']][key]
 def save():dest_manifest.write_text(json.dumps(manifest,indent=2))
 save()
 def execute(row):
  tag=row['tag']; start=time.monotonic()
  with (ROOT/'results'/f'{tag}.log').open('w') as f:
   result=subprocess.run(['librelane','--pdk','gf180mcuD','--run-tag',tag,str(ROOT/'config'/f'{tag}.json')],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  return row,result.returncode,time.monotonic()-start
 if a.run:
  skip=set(a.skip.split(',')); only=set(a.only.split(',')) if a.only else None
  todo=[r for r in manifest if r['tag'] not in skip and (only is None or r['tag'] in only)]
  with ThreadPoolExecutor(max_workers=a.jobs) as pool:
   for future in as_completed([pool.submit(execute,r) for r in todo]):
    row,code,elapsed=future.result();row.update(returncode=code,elapsed_seconds=elapsed);save()
    print(row['tag'],code,round(elapsed,1),flush=True)
 print('Generated',len(matrix),'experiments')
if __name__=='__main__': main()
