"""Native KLayout renders with cell highlights derived from the real OpenDB names."""
import json
from pathlib import Path
import pya
import re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/layout_cells.json').read_text())
out=ROOT/'results/layout';out.mkdir(exist_ok=True)
colors={'Register file':0xf2ad33,'ALU':0x29d3e2,'Contador':0xff549c}
for group,color in colors.items():
    lv=pya.LayoutView();lv.set_config('background-color','#101923');lv.set_config('grid-visible','false');lv.set_config('text-visible','false')
    lv.load_layout(data['gds']);lv.max_hier()
    cfg=json.loads((ROOT/'config/runs/rom_100_40/resolved.json').read_text())
    lv.load_layer_props(cfg['KLAYOUT_PROPERTIES']);lv.add_missing_layers()
    sources=[p.findtext('source','') for p in ET.parse(cfg['KLAYOUT_PROPERTIES']).getroot().iter('properties')]
    metals={int(re.search(r'(\d+)/0',s)[1]) for s in sources if re.match(r'Metal[1-6] ',s) and re.search(r'(\d+)/0',s)}
    layout=lv.active_cellview().layout();top=layout.top_cell();dbu=layout.dbu
    layer=layout.layer(pya.LayerInfo(2000,0))
    for cell in data['cells']:
        if cell['group']==group:
            top.shapes(layer).insert(pya.DBox(*cell['box_um']).to_itype(dbu))
    lv.add_missing_layers()
    props=lv.begin_layers()
    while not props.at_end():
        node=props.current()
        if node.source_layer==2000:
            node.name=group+' - celdas por nombre jerarquico';node.fill_color=color;node.frame_color=color;node.dither_pattern=0;node.visible=True
            lv.set_layer_properties(props,node)
        else:
            node.visible=node.source_layer in metals and node.source_datatype==0
            node.fill_color=0x354351;node.frame_color=0x354351;node.dither_pattern=0;lv.set_layer_properties(props,node)
        props.next()
    count=sum(c['group']==group for c in data['cells'])
    ann=pya.Annotation();ann.p1=pya.DPoint(data['die_um'][0],data['die_um'][3]+15);ann.p2=pya.DPoint(data['die_um'][2],data['die_um'][3]+15)
    ann.fmt=f'{group}: {count} celdas identificadas';ann.fmt_x='';ann.fmt_y='';ann.style=pya.Annotation.StyleLine
    lv.insert_annotation(ann)
    target=pya.DBox(data['die_um'][0]-20,data['die_um'][1]-20,data['die_um'][2]+20,data['die_um'][3]+40)
    lv.save_image_with_options(str(out/(group.lower().replace(' ','_')+'.png')),1500,1550,0,2,0,target)
    lv.destroy()
print(out)
