import json
from pathlib import Path
import pya
import re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/layout_cells.json').read_text())
incident=json.loads((ROOT/'results/antenna_incident.json').read_text())
cfg=json.loads((ROOT/'config/runs/rom_100_40/resolved.json').read_text())
lv=pya.LayoutView();lv.load_layout(data['gds']);lv.max_hier();lv.load_layer_props(cfg['KLAYOUT_PROPERTIES'])
lv.set_config('background-color','#101923');lv.set_config('grid-visible','false');lv.set_config('text-visible','false')
layout=lv.active_cellview().layout();top=layout.top_cell();dbu=layout.dbu
items=[(2001,incident['victim_box_um'],0xff6178)]+[(2002,d['box_um'],0x45f3a7) for d in incident['diodes']]
for layerid,bbox,color in items:
    top.shapes(layout.layer(pya.LayerInfo(layerid,0))).insert(pya.DBox(*bbox).to_itype(dbu))
lv.add_missing_layers();iterator=lv.begin_layers()
sources=[p.findtext('source','') for p in ET.parse(cfg['KLAYOUT_PROPERTIES']).getroot().iter('properties')]
metals={int(re.search(r'(\d+)/0',s)[1]) for s in sources if re.match(r'Metal[1-6] ',s) and re.search(r'(\d+)/0',s)}
while not iterator.at_end():
    node=iterator.current()
    if node.source_layer in [2001,2002]:
        node.fill_color=0xff6178 if node.source_layer==2001 else 0x45f3a7;node.frame_color=node.fill_color;node.dither_pattern=0;node.visible=True
        lv.set_layer_properties(iterator,node)
    else:
        node.visible=node.source_layer in metals and node.source_datatype==0
        node.fill_color=0x405364;node.frame_color=0x405364;node.dither_pattern=0;lv.set_layer_properties(iterator,node)
    iterator.next()
bounds=[item[1] for item in items]
x0=min(b[0] for b in bounds)-15;y0=min(b[1] for b in bounds)-15;x1=max(b[2] for b in bounds)+15;y1=max(b[3] for b in bounds)+15
ann=pya.Annotation();ann.p1=pya.DPoint(x0,y1+5);ann.p2=pya.DPoint(x1,y1+5);ann.style=pya.Annotation.StyleLine
ann.fmt='Rojo: pin afectado | Verde: diodo de antena';ann.fmt_x='';ann.fmt_y='';lv.insert_annotation(ann)
out=ROOT/'results/layout/antena_corregida.png'
lv.save_image_with_options(str(out),1600,1100,0,2,0,pya.DBox(x0,y0,x1,y1+12));print(out)
