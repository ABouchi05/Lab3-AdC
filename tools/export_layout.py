"""Run with openroad -exit -python tools/export_layout.py."""
import odb,json
from pathlib import Path
root=Path('/opt/lab3/design')
run=root/'config/runs/rom_100_40'
states=sorted(run.glob('*/state_out.json'),key=lambda p:int(p.parent.name.split('-')[0]))
state=json.loads(states[-1].read_text())
db=odb.dbDatabase.create();odb.read_db(db,state['odb']);block=db.getChip().getBlock()
scale=block.getDbUnitsPerMicron()
def box(rect):return [rect.xMin()/scale,rect.yMin()/scale,rect.xMax()/scale,rect.yMax()/scale]
groups={'Register file':'u_soc.u_core.u_rf.','ALU':'u_soc.u_core.u_id.u_alu.','Contador':'u_soc.u_periph.u_cycle_counter.'}
cells=[]
for inst in block.getInsts():
    group=next((name for name,prefix in groups.items() if inst.getName().startswith(prefix)),None)
    if group:cells.append(dict(name=inst.getName(),master=inst.getMaster().getName(),group=group,box_um=box(inst.getBBox())))
out=root/'results/layout_cells.json'
out.write_text(json.dumps(dict(odb=state['odb'],gds=state['gds'],die_um=box(block.getDieArea()),cells=cells),indent=2))
report=next(run.glob('*-openroad-checkantennas/reports/antenna_summary.rpt'))
for line in report.read_text().splitlines():
    fields=[s.strip() for s in line.split('│')]
    if len(fields)<8:continue
    try:ratio,partial,required=map(float,fields[1:4])
    except ValueError:continue
    victim_path=fields[5].replace('\\','');inst_name,pin=victim_path.rsplit('/',1)
    inst=block.findInst(inst_name)
    if inst is None:continue
    term=next((t for t in inst.getITerms() if t.getMTerm().getName()==pin),None)
    if term is None or term.getNet() is None:continue
    net=term.getNet()
    diodes=[t.getInst() for t in net.getITerms() if '__antenna' in t.getInst().getMaster().getName()]
    if not diodes:continue
    incident=dict(initial_report=str(report),initial_net=fields[4],victim=victim_path,layer=fields[6],
                  partial_ratio=partial,required_ratio=required,multiplier=ratio,
                  final_net=net.getName(),victim_box_um=box(inst.getBBox()),
                  diodes=[dict(name=d.getName(),box_um=box(d.getBBox())) for d in diodes])
    (root/'results/antenna_incident.json').write_text(json.dumps(incident,indent=2));break
print('Exported',len(cells),'named placed cells',out)
