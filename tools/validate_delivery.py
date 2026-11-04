"""Validate a submission ZIP or its extracted directory without installed EDA tools."""
import gzip,hashlib,json,posixpath,re,sys,zipfile
from pathlib import Path

def validate(target):
 target=Path(target)
 archive=zipfile.ZipFile(target) if target.is_file() else None
 try:
  names=set(archive.namelist()) if archive else {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and '.git' not in p.parts}
  def read(name):return archive.read(name) if archive else (target/name).read_bytes()
  manifest=json.loads(read('manifest.sha256.json'))
  assert set(manifest)|{'manifest.sha256.json'}<=names,'Missing manifest entries'
  if archive:
   assert len(archive.namelist())==len(names),'Duplicate archive paths'
   assert names==set(manifest)|{'manifest.sha256.json'},'Unlisted archive contents'
  largest=('',0)
  for name,digest in manifest.items():
   assert not name.startswith('/') and '..' not in Path(name).parts,'Unsafe archive path'
   data=read(name);assert hashlib.sha256(data).hexdigest()==digest,'Hash mismatch: '+name
   assert not re.search(rb'gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',data),'Credential pattern: '+name
   if name.endswith('.gz'):gzip.decompress(data)
   assert len(data)<25*1024*1024,'File exceeds 25 MiB: '+name
   if len(data)>largest[1]:largest=(name,len(data))
  required=['README.md','Proyecto_3.pdf','rtl/asic_top.v','sw/game.s','tools/assembler.py','tests/tb_asic.v','results/physical/rom_100_40/final/asic_top.gds','results/physical/summary.json','docs/ENTREGA.md']
  for name in required:assert name in names,'Required artifact missing: '+name
  for name in names:
   if name.startswith('config/') and name.endswith('.json'):
    cfg=json.loads(read(name))
    for src in cfg.get('VERILOG_FILES',[]):
     assert src.startswith('dir::'),'Unexpected source path: '+src
     rel=posixpath.normpath(posixpath.join(posixpath.dirname(name),src[5:]))
     assert rel in names,'Configuration source missing: '+rel
    if cfg.get('IO_PIN_ORDER_CFG'):
     rel=posixpath.normpath(posixpath.join(posixpath.dirname(name),cfg['IO_PIN_ORDER_CFG'][5:]))
     assert rel in names,'Pin configuration missing: '+rel
    for key in ['TIMING_VIOLATION_CORNERS','SETUP_VIOLATION_CORNERS','HOLD_VIOLATION_CORNERS']:assert cfg[key]==['*'],name+' '+key
  rows={r['tag']:r for r in json.loads(read('results/physical/summary.json'))}
  for tag in ['rom_100_40','ffq_100_40']:
   r=rows[tag];m=r['metrics']
   assert r['has_final'] and r['flow_complete_message'] and r['meets_project_criteria'],tag+' incomplete'
   for k in ['magic__drc_error__count','design__lvs_error__count','antenna__violating__nets','antenna__violating__pins']:assert m[k]==0,(tag,k)
   for typ in ['setup','hold']:
    corners=[k for k in m if k.startswith('timing__'+typ+'__ws__corner:')]
    assert len(corners)==9,(tag,typ,len(corners))
    assert all(m[k]>=0 for k in corners),(tag,typ,'negative slack')
    assert all(m[k.replace('__ws__','__tns__')]==0 for k in corners),(tag,typ,'nonzero TNS')
  for suffix,folder in [('', 'simulation'),('_ff','simulation_ff')]:
   proof=json.loads(read('results/mapped_verification'+suffix+'.json'))
   assert proof['trace_equal'] and proof['direct_capture_register_asserted']
   traces=[]
   for kind in ['rtl','mapped']:
    trace=gzip.decompress(read('results/'+folder+'/'+kind+'_trace.csv.gz'))
    assert hashlib.sha256(trace).hexdigest()==proof[kind+'_sha256']
    assert len(trace.splitlines())==proof[kind+'_observed_cycles']==89186
    traces.append(trace)
   assert traces[0]==traces[1]
  for doc in ['README.md','docs/ENTREGA.md']:
   for link in re.findall(r'\]\(([^)]+)\)',read(doc).decode('utf-8')):
    if '://' not in link and not link.startswith('#'):
     rel=posixpath.normpath(posixpath.join(posixpath.dirname(doc),link.split('#')[0]))
     assert rel in names or any(n.startswith(rel.rstrip('/')+'/') for n in names),'Broken link: '+link
  forbidden=['stop_superseded.py','record_control_stop.py','progress.py','tune_density.py','report.py','setup_linux.sh','ejemplo_traduccion.py','write_readme.py','package.py']
  assert all('tools/'+f not in names for f in forbidden)
  assert not any('/__pycache__/' in n or '/runs/' in n or n.endswith('.pyc') or n.startswith('.git/') for n in manifest)
  return dict(valid=True,files=len(manifest)+1,studies=len(rows),largest_file=largest[0],largest_bytes=largest[1],zip_bytes=target.stat().st_size if archive else None,checks=['SHA256','gzip CRC','configuration sources','9-corner closure of both references','89186-cycle traces of both memories','README links','file sizes','auxiliary-file exclusion'])
 finally:
  if archive:archive.close()

if __name__=='__main__':
 target=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'output/proyecto3_entrega_github.zip'
 print(json.dumps(validate(target),indent=2))
