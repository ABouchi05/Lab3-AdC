"""Compare a real mapped netlist against the reduced RTL test.

Use a LibreLane synthesis run built with build/verify/asic_memory.v.
Never mix the final 3-second program with the reduced RTL image.
"""
import argparse, shutil
from pathlib import Path
from verify import ROOT, run, sources
from generate import generate

def main():
 p=argparse.ArgumentParser()
 p.add_argument('netlist',type=Path)
 p.add_argument('--model',type=Path,action='append',required=True,help='PDK Verilog models; repeat per file')
 p.add_argument('--unified',type=int,choices=[0,1],default=0)
 p.add_argument('--define',action='append',default=[],help='model compiler define; repeat if required by the installed PDK')
 p.add_argument('--work-dir',type=Path,help='separate trace directory for an additional strategy')
 a=p.parse_args()
 work=ROOT/a.work_dir if a.work_dir else ROOT/'build/mapped';work.mkdir(parents=True,exist_ok=True)
 generate('sim',work)
 for kind in ['rtl','mapped']:
  files=sources(work/'asic_memory.v') if kind=='rtl' else [a.netlist.resolve(),*[f.resolve() for f in a.model]]
  exe=work/(kind+'.vvp')
  run(['iverilog','-g2012','-s','tb',f'-DUNIFIED={a.unified}',*(['-DNETLIST','-DGF180_NETLIST'] if kind=='mapped' else []),
       *['-D'+x for x in a.define],'-o',exe,*files,ROOT/'tests/tb_asic.v'])
  run(['vvp',exe],cwd=work,log=work/(kind+'.log'))
  shutil.copyfile(work/'trace.csv',work/(kind+'.csv'))
 if (work/'rtl.csv').read_bytes() != (work/'mapped.csv').read_bytes():
  raise AssertionError('Mapped netlist differs from RTL: inspect traces/config/program/model')
 print('PASS mapped GF180 netlist and RTL match every observed clock')
if __name__=='__main__':main()
