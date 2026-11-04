"""Build the reviewed submission, without temporary jobs or duplicate reports."""
import gzip, hashlib, json, re, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS='assembler.py generate.py verify.py prepare_mapped_sim.py post_synthesis.py run_mapped_wsl.sh run_mapped_ff_wsl.sh install_env_wsl.sh run_wsl.sh experiments.py collect_physical.py analyze_synthesis.py plot_physical.py final_report.py export_layout.py render_layout.py render_antenna.py run_fpga_audit.sh capture_environment.sh capture_pdk.py collect_simulation.py repair_ff_antenna.sh recheck_all_corners.sh package_delivery.py validate_delivery.py'.split()
STUDIES=['rom_100_40','ffq_100_40','rom_80_40','rom_60_40','rom_63_40','rom_62_40','rom_40_40','rom_30_40','rom_100_30','rom_100_50','rom_100_60','rom_fast_100_40','ffq_60_40']
EXPLORATORY=['ff_100_40','ff_100_20','ffp_100_40']
files={}
TEXT_SUFFIXES={'.sh','.py','.v','.vh','.json','.cfg','.md','.s','.hex','.txt','.rpt','.log'}

def payload(name,value):
 data=value.read_bytes() if isinstance(value,Path) else value
 if Path(name).suffix in TEXT_SUFFIXES or name in ['.gitignore','.gitattributes']:
  data=data.replace(b'\r\n',b'\n')
 return data

def add(path,required=True):
 p=ROOT/path
 if not p.is_file():
  if required:raise FileNotFoundError(p)
  return
 files[p.relative_to(ROOT).as_posix()]=p

def generated(path,text):files[path]=text.encode('utf-8')

for name in ['.gitignore','.gitattributes','requirements-report.txt','Proyecto_3_arquitectura.pdf','Proyecto_3.pdf']:add(name)
for directory in ['rtl','sw','tests','results/layout','results/plots','results/simulation','results/simulation_ff']:
 for p in (ROOT/directory).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and not p.name.endswith('.symbols.json'):add(p.relative_to(ROOT))
for name in TOOLS:add('tools/'+name)
for name in ['verification.json','mapped_verification.json','mapped_verification_ff.json','memory.log','alu_False.log','alu_True.log','fpga_audit.log','antenna_incident.json','layout_cells.json','environment.txt','pdk_sources.txt','pdk_manifest.json','toolchain_flake.lock','rtl_game.log','mapped_game.log','interrupted_experiments.json']:add('results/'+name)

rows=json.loads((ROOT/'results/physical/summary.json').read_text())
rows=[r for r in rows if r['tag'] in STUDIES+EXPLORATORY]
assert {r['tag'] for r in rows}==set(STUDIES+EXPLORATORY)
generated('results/physical/summary.json',json.dumps(rows,indent=2)+'\n')
for row in rows:
 tag=row['tag'];base=ROOT/'results/physical'/tag
 for name in ['latest_state.json','resolved.json','flow.log']:add((base/name).relative_to(ROOT))
 add('config/'+tag+'.json')
 # Area summaries for each reported case; full mapped synthesis inputs for both references.
 for name in ['area_analysis.json','stat.json','stat.rpt']:add((base/'synthesis'/name).relative_to(ROOT))
 if tag in ['rom_100_40','ffq_100_40']:
  for name in ['asic_top.nl.v.json','asic_top.nl.v','instance_areas.json','yosys-synthesis.log']:add((base/'synthesis'/name).relative_to(ROOT))
 if tag in STUDIES and row.get('timing_source'):
  stage=Path(row['timing_source']).name;timing=base/'timing'/stage
  # Original multicorner summary contains all nine corners, not just the typical one.
  for name in ['summary.rpt','critical_paths.json']:add((timing/name).relative_to(ROOT))
  detailed=[]
  if tag in ['rom_100_40','ffq_100_40']:detailed=['nom_tt_025C_5v00','max_ss_125C_4v50','min_ff_n40C_5v50']
  elif tag in ['rom_63_40','rom_62_40']:detailed=['max_ss_125C_4v50']
  for corner in detailed:
   for name in ['max.rpt','min.rpt']:
    p=timing/corner/name
    if not p.exists():p=p.with_suffix(p.suffix+'.gz')
    add(p.relative_to(ROOT))
 # Keep primary final signoff reports and logs; discard repeated per-step configuration,
 # state_in, process statistics, runtimes and redundant machine-readable report copies.
 signoff=base/'signoff'
 for kind in ['magic-drc','netgen-lvs','checkantennas','reportmanufacturability']:
  steps=sorted([p for p in signoff.glob('*') if p.is_dir() and kind in p.name],key=lambda p:int(p.name.split('-')[0]))
  if not steps:continue
  chosen=[steps[-1]]
  if tag=='rom_100_40' and kind=='checkantennas':chosen.append(steps[0])
  if tag=='ffq_100_40' and kind=='checkantennas':chosen.extend(p for p in steps if p.name.startswith('46-'))
  for step in set(chosen):
   for p in step.rglob('*'):
    if p.is_file() and p.name.endswith(('.rpt','.rpt.gz')):add(p.relative_to(ROOT))
   if kind in ['magic-drc','netgen-lvs']:
    for p in step.glob('*.log'):add(p.relative_to(ROOT))
 if tag=='rom_100_40':
  for p in (base/'final').iterdir():
   if p.is_file():add(p.relative_to(ROOT))
add('config/pins.cfg')

# Consolidate actual run metadata; unexecuted queue entries are not submission artifacts.
experiments={}
for name in ['experiments.json','refinements.json','boundary.json','padded_memory.json','placement_density.json']:
 p=ROOT/'results'/name
 if p.exists():
  for r in json.loads(p.read_text()):
   if r['tag'] in STUDIES+EXPLORATORY:
    experiments.setdefault(r['tag'],{}).update(r)
generated('results/experiments.json',json.dumps(list(experiments.values()),indent=2)+'\n')

readme=(ROOT/'README.md').read_text(encoding='utf-8')
old='Crear un entorno Python con requirements-report.txt. Ejecutar en orden tools/collect_physical.py desde WSL, tools/analyze_synthesis.py, tools/plot_physical.py, tools/final_report.py, tools/write_readme.py y tools/package.py. final_report.py rechaza la generación final si faltan la referencia FF cerrada, la evidencia física exigida o la comprobación directa de ciclos. El paquete verifica gzip, ZIP y hashes.'
new='Para regenerar el informe usando la evidencia incluida: instalar requirements-report.txt y ejecutar `python tools/plot_physical.py` y `python tools/final_report.py`. No es necesario repetir LibreLane. Para recalcular las áreas de las dos referencias, ejecutar `python tools/analyze_synthesis.py`. Para construir y validar nuevamente este ZIP, ejecutar `python tools/package_delivery.py`. Para recopilar corridas nuevas completas, ejecutar tools/collect_physical.py desde WSL con --runs y --out apuntando a las carpetas correspondientes. El índice [docs/ENTREGA.md](docs/ENTREGA.md) explica exactamente qué evidencia se conserva.'
readme=readme.replace(old,new)
readme=readme.replace('Las pruebas interrumpidas se identifican en interrupted_experiments.json','Las pruebas interrumpidas se identifican en results/interrupted_experiments.json')
readme=readme.replace('las pruebas interrumpidas se identifican en interrupted_experiments.json','las pruebas interrumpidas se identifican en results/interrupted_experiments.json')
if '## Comprobación local de esta entrega' not in readme:readme+='\n## Comprobación local de esta entrega\n\nEjecutar desde la carpeta descomprimida: `python tools/validate_delivery.py .`. Para repetir las pruebas del assembler: `python -m unittest discover -s tests -v`. Con Icarus Verilog y Yosys instalados, `python tools/verify.py` repite la regresión funcional de ambas memorias. Los comandos WSL anteriores repiten la simulación GF180 y la implementación física.\n\nPara entregar en GitHub se debe publicar el contenido descomprimido, con README.md en la raíz. El ZIP no contiene credenciales, dependencias instaladas ni una carpeta .git. La defensa presencial corresponde a los integrantes.\n'
generated('README.md',readme)
generated('results/README.md','''# Evidencia conservada

- `physical/summary.json`: métricas de 13 estudios y tres controles exploratorios que explican la decisión física. Los intentos rechazados o interrumpidos conservan su estado real.
- Cada estudio contiene configuración resuelta, estado final disponible, log del flujo, estadísticas de síntesis y resumen original de timing de los nueve corners.
- Se conservan reportes detallados de setup/hold en tres corners representativos para las dos referencias, y en el corner lento para el límite ROM de 63/62 ns. El resto de métricas completas está también en latest_state.json.
- `physical/rom_100_40/final`: GDSII, DEF, OpenDB, LEF, netlist, SDC, SPICE y vista del macro final.
- Los subdirectorios signoff conservan los reportes originales finales de DRC, LVS, antena y manufacturabilidad. Las antenas previas relevantes se conservan como incidentes corregidos.
- `simulation` y `simulation_ff`: trazas completas y netlists GF180 de prueba, comprimidos sin pérdida, con sus hashes. Ambas estrategias aprobaron 89186 ciclos.
- `fpga_audit.log`: error real de primitivas del diseño FPGA original. `layout` y `plots`: figuras utilizadas en el PDF.
- `environment.txt`, `pdk_sources.txt`, `pdk_manifest.json`, `toolchain_flake.lock`: herramientas y PDK realmente utilizados.

Las rutas /opt/lab3 dentro de logs/estados son procedencia histórica. El README indica cómo reconstruir el entorno; no se requieren archivos temporales de otra máquina para leer la entrega o ejecutar las pruebas desde sus fuentes.
''')
generated('docs/ENTREGA.md','''# Índice de entrega del Proyecto 3

El documento de referencia es Proyecto_3_arquitectura.pdf. El informe terminado está en [Proyecto_3.pdf](../Proyecto_3.pdf).

| Actividad del enunciado | Archivos de entrega |
|---|---|
| 3.1 Adaptación de FPGA a ASIC | rtl/asic_top.v, rtl/, results/fpga_audit.log; sección 1 del PDF |
| 3.2 Memoria, uso del programa y assembler | sw/game.s, tools/assembler.py, tools/generate.py, rtl/generated/, config/rom_100_40.json, config/ffq_100_40.json; secciones 2 y 2.1 |
| 3.3 Síntesis y atribución jerárquica | results/physical/rom_100_40/synthesis/, tools/analyze_synthesis.py; sección 3 |
| 3.4 Barrido, ruta crítica, optimización y constantes | config/rom_*_40.json, results/physical/*/timing/, latest_state.json, rom_fast_100_40; secciones 4 y 5 |
| 3.5 Floorplan, alimentación, ubicación y costo | rom_100_30, rom_100_40, rom_100_50, rom_100_60, config/pins.cfg, results/plots/; sección 6 |
| 3.6 DRC/LVS/antena y layout anotado | results/physical/rom_100_40/signoff/, final/, results/layout/, results/antenna_incident.json, results/layout_cells.json; secciones 7 y 8 |
| 3.7 Simulación funcional post-síntesis | tests/, tools/post_synthesis.py, tools/run_mapped_wsl.sh, tools/run_mapped_ff_wsl.sh, results/simulation/, results/simulation_ff/, mapped_verification*.json; sección 9 |
| Instalación, versiones y reproducción | README.md, tools/install_env_wsl.sh, tools/run_wsl.sh, results/environment.txt, pdk_sources.txt y toolchain_flake.lock; sección 10 |

## Selección de evidencia

Se mantienen los trece estudios físicos que respaldan las tablas del informe, incluidos los puntos de timing rechazados. Se mantienen tres controles adicionales: ff_100_40 (conflictos persistentes de ruteo), ff_100_20 (prueba de menor utilización interrumpida) y ffp_100_40 (fallo de congestión con densidad automática). Son evidencia de decisiones, no diseños aceptados. Los demás trabajos cancelados se registran en results/interrupted_experiments.json, sin repetir sus archivos parciales.

El resumen original de STA de cada estudio contiene los nueve corners. Los reportes detallados se limitan a las referencias y al límite ROM 63/62 ns; las tablas numéricas completas quedan en los estados originales. No se eliminan advertencias eléctricas ni se presenta un experimento rechazado como limpio.

Se excluyen vigilancia de procesos, control de colas, reparación de metadatos, instalación preliminar reemplazada, informe de avance, ejemplos auxiliares, cachés, dependencias instaladas, configuración de trabajos no ejecutados, reportes intermedios duplicados y vistas físicas completas de alternativas. Se conservan las vistas físicas del macro final y los scripts necesarios para regenerar los demás resultados.

## Alcance de la entrega

La entrega cumple los criterios expresos de la corrida final del enunciado: 100 ns, 40 %, DRC/LVS limpios, antena corregida y setup/hold multicorner. El informe también declara las advertencias de slew/capacitancia y la omisión del runset KLayout DRC. No acredita fabricación industrial ni simulación SDF. La publicación en GitHub y la defensa presencial son pasos posteriores a este archivo.

manifest.sha256.json permite comprobar cada archivo. tools/validate_delivery.py verifica integridad, rutas de fuentes, evidencia de cierre, trazas, enlaces del README y tamaños antes de dar el paquete por válido.
''')

# Make Git's checkout behavior explicit: exact bytes for binary/unknown formats,
# LF for the text formats whose hashes are recorded below.
attributes='* -text\n'
attributes+=''.join('*'+suffix+' text eol=lf\n' for suffix in sorted(TEXT_SUFFIXES))
attributes+='.gitignore text eol=lf\n.gitattributes text eol=lf\n'
attributes+='*.gds binary\n*.odb binary\n*.png binary\n*.pdf binary\n*.gz binary\n'
generated('.gitattributes',attributes)

manifest={name:hashlib.sha256(payload(name,value)).hexdigest() for name,value in sorted(files.items())}
generated('manifest.sha256.json',json.dumps(manifest,indent=2)+'\n')
dest=ROOT/'output/proyecto3_entrega_github.zip';dest.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,value in sorted(files.items()):
  z.writestr(name,payload(name,value))
from validate_delivery import validate
result=validate(dest)
print(json.dumps(result,indent=2))
print(dest)
