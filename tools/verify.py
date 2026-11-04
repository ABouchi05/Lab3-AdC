"""Portable RTL and generic post-synthesis regression, both memory strategies."""
import os, shutil, subprocess, sys, json
from pathlib import Path
from generate import generate
ROOT=Path(__file__).resolve().parents[1]
suite=Path.home()/'.apio/packages/oss-cad-suite'
if suite.exists():
    os.environ['PATH']=str(suite/'bin')+os.pathsep+str(suite/'lib')+os.pathsep+os.environ['PATH']
def run(args, cwd=ROOT, log=None):
    env=os.environ.copy()
    if str(args[0]) in ['iverilog','vvp'] and Path('C:/iverilog/bin').exists():
        args=[str(Path('C:/iverilog/bin')/(str(args[0])+'.exe')),*args[1:]]
        env['PATH']='C:/iverilog/bin'+os.pathsep+env['PATH']
    r=subprocess.run(list(map(str,args)),cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if log: Path(log).write_text(r.stdout,encoding='utf-8')
    if r.returncode: raise RuntimeError(f'{args[0]} exit={r.returncode}\n{r.stdout}')
    return r.stdout
def sources(memory):
    return [p for p in sorted((ROOT/'rtl').rglob('*.v')) if p.name not in ['game_top.v','pochoco_ram.v','asic_memory.v']]+[memory]
def main():
    build=ROOT/'build/verify'; build.mkdir(parents=True,exist_ok=True)
    generate('sim',build)
    memory_exe=build/'memory.vvp'
    run(['iverilog','-g2012','-s','tb_memory','-o',memory_exe,build/'asic_memory.v',ROOT/'tests/tb_memory.v'])
    run(['vvp',memory_exe],log=ROOT/'results/memory.log')
    for fast in [False,True]:
        exe=build/f'alu_{fast}.vvp'
        run(['iverilog','-g2012','-s','tb_alu',*(['-DASIC_FAST_ADD'] if fast else []),'-o',exe,ROOT/'rtl/espino_core/espino_alu.v',ROOT/'tests/tb_alu.v'])
        run(['vvp',exe],log=ROOT/'results'/f'alu_{fast}.log')
    rtl=sources(build/'asic_memory.v')
    summary={}
    for unified in [0,1]:
        work=build/str(unified); work.mkdir(exist_ok=True)
        # Relative paths keep Yosys scripts portable across Windows and Linux.
        rel=lambda p: os.path.relpath(p,ROOT).replace('\\','/')
        src=' '.join(rel(p) for p in rtl)
        script=work/'synth.ys'
        script.write_text(f'read_verilog {src}\nchparam -set Unified {unified} asic_top\nhierarchy -top asic_top\nsynth -top asic_top\ncheck -assert\nwrite_verilog -noattr {rel(work/"netlist.v")}\nstat\n')
        run(['yosys','-Q','-s',rel(script)],log=work/'synthesis.log')
        logs={}
        for kind in ['rtl','netlist']:
            exe=work/(kind+'.vvp')
            files=rtl if kind=='rtl' else [work/'netlist.v']
            run(['iverilog','-g2012','-s','tb',f'-DUNIFIED={unified}',*(['-DNETLIST'] if kind=='netlist' else []),'-o',exe,*files,ROOT/'tests/tb_asic.v'])
            logs[kind]=run(['vvp',exe],cwd=work,log=work/(kind+'.log'))
            shutil.copyfile(work/'trace.csv',work/(kind+'.csv'))
        if (work/'rtl.csv').read_bytes() != (work/'netlist.csv').read_bytes():
            raise AssertionError(f'Cycle trace mismatch: Unified={unified}')
        summary[str(unified)]={'trace_equal':True,'rtl':logs['rtl'],'netlist':logs['netlist']}
    if (build/'0/rtl.csv').read_bytes() != (build/'1/rtl.csv').read_bytes():
        raise AssertionError('Memory strategies differ on game behavior')
    (ROOT/'results/verification.json').write_text(json.dumps(summary,indent=2))
    print('PASS: both memories; RTL == generic post-synthesis each clock; full game regression')
if __name__=='__main__': main()
