"""Create the final report exclusively from collected run evidence."""
import json,re,sys
from pathlib import Path
from collections import Counter
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'results/physical'
rows={r['tag']:r for r in json.loads((DATA/'summary.json').read_text())}
DRAFT='--draft' in sys.argv
def closed(r):
 m=r['metrics']
 required=['magic__drc_error__count','design__lvs_error__count','antenna__violating__nets','antenna__violating__pins','timing__setup__tns','timing__hold__tns']
 return r.get('has_final') and r.get('flow_complete_message') and all(m.get(k)==0 for k in required) and m.get('timing__setup__ws',-1)>=0 and m.get('timing__hold__ws',-1)>=0
FF_REF=next((tag for tag in ['ffq_100_40','ffp_100_40','ff_100_40'] if tag in rows and (closed(rows[tag]) or DRAFT)),'ff_100_40')
required=['rom_100_40',FF_REF,'rom_fast_100_40','rom_100_30','rom_100_50','rom_100_60','rom_63_40','rom_62_40']
for tag in required:
 if not DRAFT and (tag not in rows or not rows[tag].get('has_final')):raise RuntimeError('Missing complete physical evidence: '+tag)
base=rows['rom_100_40'];assert closed(base)
if not DRAFT and not closed(rows[FF_REF]):raise RuntimeError('Unified-memory reference has not closed all project criteria')
proof=json.loads((ROOT/'results/mapped_verification.json').read_text())
assert proof['trace_equal'] and proof.get('direct_capture_register_asserted')
area={tag:json.loads((DATA/tag/'synthesis/area_analysis.json').read_text()) for tag in rows if (DATA/tag/'synthesis/area_analysis.json').exists()}
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9.5;styles['BodyText'].leading=13;styles['BodyText'].spaceAfter=7
styles['Title'].fontSize=22;styles['Title'].leading=26;styles['Title'].textColor=colors.HexColor('#183b56')
styles['Heading2'].textColor=colors.HexColor('#183b56')
styles['Normal'].fontSize=8;styles['Normal'].leading=10
story=[]
def p(s,style='BodyText'):story.append(Paragraph(escape(str(s)),styles[style]))
def h(s):p(s,'Heading2')
def page(title):
 if story:story.append(PageBreak())
 p(title,'Title');story.append(Spacer(1,8))
def num(v,n=3):return '-' if v is None else f'{v:,.{n}f}'
def tab(data,widths=None,small=False):
 cells=[[Paragraph(escape(str(v)),styles['Normal']) for v in row] for row in data]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf4')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#b9cbd8')),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 story.append(t);story.append(Spacer(1,9))
def figure(path,width=500,maxheight=360):
 img=Image(str(path));scale=min(width/img.imageWidth,maxheight/img.imageHeight);img.drawWidth=img.imageWidth*scale;img.drawHeight=img.imageHeight*scale;story.append(img);story.append(Spacer(1,6))
def best(prefix):
 pattern=(r'(?:ff|ffp|ffq)' if prefix=='ff' else prefix)+r'_(\d+(?:\.\d+)?)_40'
 vals=[float(re.fullmatch(pattern,tag)[1]) for tag,r in rows.items() if re.fullmatch(pattern,tag) and closed(r)]
 return min(vals) if vals else None
def util(m):return 100*(m['design__instance__area']-m.get('design__instance__area__class:fill_cell',0)-m.get('design__instance__area__class:tap_cell',0)-m.get('design__instance__area__class:endcap_cell',0))/m['design__core__area']

page('Proyecto 3 | Pochoco SoC a ASIC')
p('Arquitectura de Computadores - Grupo 18','Heading2')
p('Informe de implementación y comparación. Punto de partida: Proyecto 2 del grupo, commit 4a0a9128566306269fa97b195bb28ef2fa42885f. La corrida final elegida es rom_100_40: macro digital de celdas estándar, sin pads de I/O ni encapsulado.')
m=base['metrics'];die=m['design__die__area'];a=area['rom_100_40']
tab([['Resultado final','Medición / evidencia'],['Tecnología','gf180mcuD / gf180mcu_fd_sc_mcu7t5v0'],['Período / core solicitado','100 ns / 40 %'],['Área de síntesis',num(a['area_um2'])+' um2'],['Área de die',num(die)+' um2 = '+num(die/1e6,6)+' mm2'],['Peor slack setup / hold',num(m['timing__setup__ws'],6)+' ns / '+num(m['timing__hold__ws'],6)+' ns'],['TNS setup / hold','0 / 0 en todos los corners'],['DRC / LVS / antena','Magic DRC=0; Netgen LVS=0; antena=0'],['Costo equivalente',f'US$ {die*0.023:,.2f}']], [180,330])
h('Decisión de arquitectura')
p(f"Se adopta ROM más RAM reducida. La memoria unificada ocupa {area['ff_100_40']['area_um2']/a['area_um2']:.2f} veces el área de celdas de la alternativa ROM en síntesis. El programa tiene 99 palabras y no usa RAM de datos; la RAM de reserva tiene una palabra. No se usa bootloader para reemplazar las dos estrategias exigidas.")
h('Criterio de aceptación aplicado')
p('Se exige flujo completo, DRC y LVS limpios, antena resuelta, slack mínimo de setup y hold no negativo y TNS=0 en los nueve corners RC/PVT. Un retorno exitoso del flujo no basta. El PDK comprobaba setup en *tt* por defecto; la corrida a 60 ns se rechaza por el corner lento. Se repitieron los verificadores finales con comodines * para todos los corners: 100 y 80 ns pasan; 60 ns se rechaza.')

page('1. Del RTL de FPGA al RTL de ASIC')
p('asic_top.v expone clk_i, rst_ni, botones, cuatro LEDs, dos displays de siete segmentos activos bajos y SPI. Instancia el SoC del Proyecto 2 con sus módulos de core y periféricos. Los terminales representan conexiones del macro a un sistema mayor; no tienen protección ESD, pads o capacidad de corriente de una FPGA.')
tab([['Dependencia encontrada','Diagnóstico real y sustitución'],['SB_RAM40_4K en register file','Auditoría fpga_audit: %Error-MODMISSING, results/fpga_audit.log líneas 10-12 y 26-28; fuente original líneas 22 y 33. Se reemplaza por 15x32 FF y dos lecturas registradas.'],['initial + $readmemh','La auditoría se detiene antes de Yosys por los bloques SB_RAM. No produce un mensaje adicional de esta construcción. El archivo es una entrada del elaborador/simulador, no una fuente de estado de encendido en silicio. Se reemplaza por constantes ROM o reset explícito de FF.'],['Power-on reset inicializado','por_cnt=0 dependía de inicialización FPGA; tampoco alcanza síntesis en la auditoría. Se elimina y se expone reset externo.'],['RAM / BRAM inferida','La RAM unificada original se sustituye por FF dimensionados al juego; no se asume una macro SRAM disponible en el PDK.'],['Reloj de 25 MHz','No es necesariamente un error de herramientas: es un supuesto del software. Se recalculan las constantes para 10 MHz.']], [145,365])
h('Semántica conservada')
p('El register file tiene 15 registros de 32 bits y salidas registradas para conservar el handshake de lectura síncrona. x0 es cero por construcción y las escrituras a x0 no modifican estado. Se mantiene lectura antes de escritura. El reset se activa asíncronamente, se mantiene al menos cinco ciclos y se libera sincronizado externamente; la distribución física del reset se analiza con timing, sin declarar rutas falsas para ocultarla.')
p('Los botones y el SPI conservan sus sincronizadores. El contador libre se separa como cycle_counter para medir su área y localizar sus celdas. No se usan initial, $readmemh o primitivas FPGA en los archivos de la configuración ASIC. La auditoría del original se conserva como un intento fallido, separado de la corrida final.')

page('2. Memoria y programa del juego')
table=[['Estrategia','Área síntesis um2','FF','Util. lógica %','Uso / reserva','Fmáx verificada MHz']]
for prefix,tag,label in [('rom','rom_100_40','ROM + RAM FF'),('ff',FF_REF,'Unificada FF')]:
 b=best(prefix);aa=area[tag]
 table.append([label,num(aa['area_um2']),aa['flip_flops'],num(util(rows[tag]['metrics']),2),'99 instrucciones; 0 datos usados; 1 dato reservado',num(1000/b if b else None)])
tab(table,[100,95,40,70,110,95])
p('Las áreas anteriores son celdas mapeadas al mismo Liberty de síntesis, no LUTs ni área del die con fillers. La frecuencia se calcula a partir del menor período ensayado que satisface todos los criterios; no se extrapola como 1/(T-slack). Los barridos y la resolución del límite se detallan en timing.')
h('Obtención del uso real')
p('El assembler produce 99 palabras de 32 bits: 396 bytes, bajo el límite de 256 palabras. En game.s, x2 se carga con 0x80000000 y no vuelve a modificarse: todos los lw/sw se dirigen a MMIO. No hay pila, tablas de datos ni otras cargas a memoria. Las variables del juego y los enlaces permanecen en registros. Por ello se usan 0 palabras RAM de datos; se reserva una para comprobar el camino RAM, dentro del límite de 64 palabras.')
h('ROM combinacional más RAM reducida')
p('El assembler genera una función case de direcciones completas con las 99 constantes del programa. Su salida se registra para conservar la respuesta de un ciclo del core. La RAM de datos es una palabra de 32 bits en 0x18c, con byte enables. Las escrituras a la ROM no alteran instrucciones; direcciones fuera de rango no se pliegan a posiciones válidas.')
h('Memoria unificada con FF')
p('Contiene 100 palabras: 99 de programa y una de reserva. El reset carga explícitamente cada palabra del programa; después se permite escribir cualquier palabra válida con byte enables. Así el diseño no depende de un archivo de arranque y la comparación incluye el costo de almacenamiento escribible. El número de FF físicos se mide después de optimización, no se presupone a partir de 100x32 solamente.')
p('En u_ram se cuentan 95 FF para ROM+RAM y 3264 para la unificada. Esta última incluye 3200 bits de almacenamiento y 64 bits de respuesta registrada. En ROM, los bits constantes/equivalentes de instrucciones permiten compartir un FF de respuesta: 32 bits de reserva más 31 de fetch y 32 de lectura de datos. La diferencia de 3169 FF explica el cambio de 914 a 4083 en todo el SoC; los otros 819 FF son comunes.')
h('Extensión del assembler')
p('python tools/assembler.py sw/game.s sw/game.hex --asic-output rtl/generated genera el .hex, los símbolos y el módulo asic_memory.v. program.json registra cantidades, constantes y hash SHA-256 del programa. La imagen reducida de simulación se genera aparte y no sustituye la imagen final.')

if FF_REF.startswith(('ffp','ffq')):
 page('2.1. Cierre físico de la memoria unificada')
 ffm=rows[FF_REF]['metrics']
 tab([['Referencia unificada','Resultado final'],['Corrida',FF_REF],['Slack setup / hold',num(ffm.get('timing__setup__ws'),6)+' / '+num(ffm.get('timing__hold__ws'),6)+' ns'],['TNS setup / hold',str(ffm.get('timing__setup__tns'))+' / '+str(ffm.get('timing__hold__tns'))],['DRC / LVS / antena',str(ffm.get('magic__drc_error__count'))+' / '+str(ffm.get('design__lvs_error__count'))+' / '+str(ffm.get('antenna__violating__nets'))],['Die / ocupación lógica',num(ffm['design__die__area'])+' um2 / '+num(util(ffm),2)+' %']], [210,300])
 p('La referencia física de la unificada es '+FF_REF+': conserva T=100 ns y core objetivo 40 %, con GPL_CELL_PADDING=DPL_CELL_PADDING=4. La separación explícita se ensaya tras observar cero overflow global, pero conflictos persistentes de ruteo detallado en la prueba sin padding. Las pruebas interrumpidas están identificadas y no se declaran limpias; la frecuencia usa únicamente corridas completas. El padding afecta placement/ruteo y no cambia los 4083 FF o la semántica de la memoria.')
 if FF_REF.startswith('ffq'):
  p('La densidad automática del ensayo con padding llegó a 73,15 % y falló por congestión global. ffq fija PL_TARGET_DENSITY_PCT=60, por encima del mínimo factible calculado de aproximadamente 57 %. Es un ajuste de placement distinto de FP_CORE_UTIL=40; ambos parámetros se registran para evitar confundir utilización de core y densidad de colocación.')
  p('En la primera terminación de ffq_100_40 quedó una antena en net4042, fanout4041/I, Metal2: razón parcial 780,71 frente a 400. Se continuó desde el OpenDB ruteado con hasta diez iteraciones de reparación, sin repetir síntesis ni placement. Se conservan las etapas iniciales y se usan exclusivamente las métricas del signoff posterior a la reparación; tools/repair_ff_antenna.sh registra cómo se repitió el tramo físico.')
  p(f"La referencia unificada conserva advertencias eléctricas de max slew ({ffm.get('design__max_slew_violation__count')}) y max capacitance ({ffm.get('design__max_cap_violation__count')}) en las métricas agregadas. No se presentan como corregidas ni como fallos de setup/hold. La comparación aplica los criterios del enunciado y no acredita preparación industrial para fabricación.")

page('3. Síntesis y trazabilidad jerárquica')
cells=json.loads((DATA/'rom_100_40/synthesis/instance_areas.json').read_text())
table=[['Celda GF180 (prefijo común omitido)','Cantidad','Instancias que explican su uso']]
for kind,count in a['top_five']:
 owners=Counter(c['owner'] for c in cells if c['type']==kind).most_common(3)
 table.append([kind.split('__')[-1],count,'; '.join(f'{owner}: {n}' for owner,n in owners)])
tab(table,[160,55,295])
p('dffrnq_1 almacena registros, tiempos y estado. mux2_2 y aoi22_1 aparecen sobre todo en selección de lecturas y habilitación de escritura del register file. nand2_1 y nor2_1 implementan decodificación ROM, selección de control, comparaciones y lógica aritmética; la atribución por instancia de la tabla permite contrastar esta explicación.')
table=[['Módulo / instancia','Área um2','Fracción total']]
for label,key in [('Core completo','u_soc.u_core'),('Register file','u_soc.u_core.u_rf'),('ALU','u_soc.u_core.u_id.u_alu'),('Memoria','u_soc.u_ram'),('Contador de ciclos','u_soc.u_periph.u_cycle_counter')]:
 ar=a['hierarchy_areas_um2'][key];table.append([label,num(ar),num(ar/a['area_um2']*100,2)+' %'])
tab(table,[245,135,130])
p('El core es el mayor bloque de primer nivel; el register file domina entre sus submódulos. El contador representa '+num(a['counter_fraction']*100,3)+' % del área total de síntesis. Las filas anidadas no se suman entre sí: ALU y register file ya están incluidos en el core.')
h('Método reproducible')
p('SYNTH_HIERARCHY_MODE=deferred_flatten conserva la jerarquía durante el mapeo. Después del flatten, los nombres u_soc.u_core.u_rf.*, u_soc.u_core.u_id.u_alu.* y u_soc.u_periph.u_cycle_counter.* permiten atribuir cada celda. analyze_synthesis.py suma el atributo area del Liberty leído por Yosys para cada tipo y agrupa por prefijo de instancia. La suma coincide con stat.json; instance_areas.json conserva el detalle y layout_cells.json relaciona nombres con posiciones OpenDB.')
p('La hipótesis previa del informe de avance era que la memoria unificada aumentaría FF y área: las corridas lo confirman. En ROM, el register file supera a la memoria porque sus dos lecturas y almacenamiento con FF cuestan más que las constantes del programa. El contador de 32 bits no domina el área; incluye solo sus FF e incremento, no todos los registros de timestamps del periférico.')

page('4. Timing: barrido y cierre multicorner')
timing=[]
for tag,r in rows.items():
 match=re.fullmatch(r'(rom|ff|ffp|ffq)_(\d+(?:\.\d+)?)_40',tag)
 if match and r.get('has_final') and 'timing__setup__ws__corner:max_ss_125C_4v50' in r['metrics']:
  timing.append((match[1],float(match[2]),tag,r))
timing.sort(key=lambda x:(x[0],-x[1]))
table=[['Mem. / ns','Corner','WS setup','WNS setup','TNS setup','WS hold','WNS hold','TNS hold']]
for prefix,period,tag,r in timing:
 mm=r['metrics']
 for corner,label in [('nom_tt_025C_5v00','nom / tt 25C 5V'),('max_ss_125C_4v50','max / ss 125C 4,5V')]:
  sw=mm.get('timing__setup__ws__corner:'+corner);hw=mm.get('timing__hold__ws__corner:'+corner)
  table.append([f'{prefix} / {period:g}',label,num(sw),num(min(0,sw)),num(mm.get('timing__setup__tns__corner:'+corner)),num(hw),num(min(0,hw)),num(mm.get('timing__hold__tns__corner:'+corner))])
tab(table,[56,112,57,57,57,57,57,57])
p('Valores en ns. WS es el slack mínimo; WNS=min(WS,0). Se conservan reportes por los nueve corners: RC min/nom/max cruzados con tt a 25C/5V, ss a 125C/4,5V y ff a -40C/5,5V. El cálculo de Fmáx exige todos, no solamente las dos condiciones representativas de la tabla.')
p('ff identifica la prueba unificada sin separación adicional; ffp agrega padding de cuatro sitios; ffq mantiene ese padding y fija densidad de placement 60 %. Se conserva la distinción y no se combinan métricas parciales de una corrida con el signoff de otra.')
for prefix in ['rom','ff']:
 b=best(prefix)
 if b is None:p(prefix.upper()+': aún no hay una corrida cerrada en la colección actual.')
 else:p(f'{prefix.upper()}: menor período ensayado con cierre completo = {b:g} ns; Fmáx verificada = {1000/b:.3f} MHz.')
p('La resolución es la separación respecto del siguiente punto rechazado, no una garantía de máximo continuo. Cada CLOCK_PERIOD puede cambiar optimización, buffering y placement. En particular, no se acepta la corrida de 60 ns aunque el flujo original devolviera éxito: max_ss presenta setup negativo y TNS distinto de cero. Los JSON conservan esa evidencia; no se reemplazó por una estimación.')
p('La entrega final opera a 10 MHz (100 ns). La frecuencia máxima verificada corresponde al barrido de implementaciones; no implica usar ese reloj en el juego con las constantes de 10 MHz. Si cambia la frecuencia de operación, deben recalcularse las constantes temporales y regenerarse el programa.')

page('5. Ruta crítica, optimización y reloj del juego')
critical=base['critical_paths'][0]
tab([['Dato','Ruta crítica final de referencia'],['Corner',critical['corner']],['Inicio',critical['start']+' / Q: instr_rdata[1]'],['Fin',critical['end']+' / D: elapsed_q[18]'],['Slack',num(critical['slack_ns'],6)+' ns']], [120,390])
p('La ruta parte del registro de instrucción de fetch, pasa por decode, selección de operandos y ALU para formar lsu_addr[31], continúa por la selección MMIO y el control del periférico, y termina en el registro de captura de tiempo. Su tramo de Espino corresponde principalmente a decode/ejecución y generación de dirección de acceso a memoria. Los nombres de celda se obtienen de max_ss_125C_4v50/max.rpt y se relacionan con las señales mediante el JSON del netlist.')
fast=rows['rom_fast_100_40'];fa=area['rom_fast_100_40'];fm=fast['metrics']
tab([['Variante a 100 ns / 40 %','Área síntesis um2','WS setup peor','WS hold peor'],['Referencia',num(a['area_um2']),num(m['timing__setup__ws']),num(m['timing__hold__ws'])],['Carry-select de 8 bits',num(fa['area_um2']),num(fm.get('timing__setup__ws')),num(fm.get('timing__hold__ws'))]], [210,110,95,95])
p('ASIC_FAST_ADD calcula en paralelo sumas de 8 bits con acarreo 0 y 1 y selecciona por bloque. Busca reducir la propagación de acarreo hacia el bit 31 de la dirección, que sí aparece en la ruta crítica observada. Cambio de área: '+num((fa['area_um2']/a['area_um2']-1)*100,2)+' %. Cambio de slack setup global: '+num(fm['timing__setup__ws']-m['timing__setup__ws'])+' ns. ABC puede reestructurar la lógica y la ruta dominante puede cambiar; el resultado se evalúa globalmente, sin atribuir toda variación a una única puerta. La referencia rom_100_40 se mantiene como corrida final trazada y simulada; la variante queda como experimento comparativo.')
if fm['timing__setup__ws']<=m['timing__setup__ws']:
 p('La modificación no mejoró timing. El mapeo reduce ligeramente el área, pero la ruta completa incluye decode, selección de operandos, suma y control MMIO; duplicar sumas por bloque no elimina esas dependencias e introduce selección de acarreo. La biblioteca y ABC ya optimizan el sumador original. Las diferencias de buffering y ubicación también influyen: una mejora en la expresión RTL no garantiza una mejora física. Por ello se conserva la referencia, con mayor margen de setup, frente al ahorro mínimo de área de la candidata.')
if fm.get('design__die__area')==m['design__die__area']:
 p('El pequeño ahorro de celdas no cambia el área de die reportada: el floorplan se cuantiza a filas y sitios. En consecuencia, tampoco cambia el costo equivalente calculado con área de die.')
h('Constantes del programa para T=100 ns')
tab([['Constante','Cálculo','Valor final'],['WAIT_CYCLES','3 s / 100 ns','30000000'],['TENTH_CYCLES','0,1 s / 100 ns','1000000'],['HOLD_CYCLES','1 s / 100 ns','10000000'],['RELEASE_CYCLES','0,02 s / 100 ns','200000']], [185,175,150])
p('La imagen final se regeneró con estas constantes. El polling puede extender las esperas, por lo que la preparación es de al menos tres segundos. La captura de respuesta se hace en hardware y la conversión a décimas trunca; el display satura en 99. El contador de 32 bits desborda cada 429,50 s a 10 MHz y los intervalos deben ser menores que ese período.')

page('6. Floorplan, alimentación y costo')
floors=[]
for tag,r in rows.items():
 match=re.fullmatch(r'rom_100_(\d+)',tag)
 if match and 'design__die__area' in r['metrics']:floors.append((int(match[1]),tag,r))
floors.sort()
table=[['Core objetivo %','Ocupación lógica %','Die um2','DRC iter. 0','Cierre completo']]
for u,tag,r in floors:
 mm=r['metrics'];table.append([u,num(util(mm),2),num(mm['design__die__area'],0),mm.get('route__drc_errors__iter:0','-'),'Sí' if closed(r) else 'No'])
tab(table,[95,115,115,90,95])
figure(ROOT/'results/plots/utilizacion_congestion.png',maxheight=250)
p('La ocupación lógica excluye fill, tap y endcap del área total de instancias; incluye las celdas de señal, reloj y reparación. El área final de instancias con fillers puede llenar el core y no representa por sí sola la utilización lógica. La gráfica usa las violaciones reportadas en la primera iteración de la última invocación de ruteo detallado; el DRC final se comprueba aparte.')
p('Esta métrica no tiene por qué ser monótona con la utilización: cambia la geometría, la longitud de cables y el estado recibido de las reparaciones de antena. Sirve para comparar la última pasada del router de estas corridas, no para afirmar una ley general de congestión. Se conservan sus valores crudos y el DRC final limpio de las corridas aceptadas.')
clean=[r for _,_,r in floors if closed(r)];small=min(clean,key=lambda r:r['metrics']['design__die__area'])
p('Menor área observada con cierre entre los valores explorados: '+small['tag']+', '+num(small['metrics']['design__die__area'])+' um2. Es el mínimo encontrado en este barrido, no una prueba de óptimo global. La corrida final conserva 40 %, conforme al enunciado.')
p('Pines: reloj/reset al sur, SPI al oeste, LEDs/botones al este y displays al norte. Se agrupan funciones y distribuye acceso al borde. La PDN usa rails Metal1 de 0,6 um y straps Metal4/Metal5 de 1,6 um, con pitch vertical 153,6 um y horizontal 153,18 um. PDN_CORE_RING=False: se implementa una malla de macro, sin anillo de pads. La conectividad de alimentación se verifica en el flujo. No se usan pads ni se asume manejo directo de LEDs externos.')
p(f'Costo equivalente final = 23000 x {die/1e6:.6f} mm2 = US$ {die*0.023:,.2f}. Se usa área de die, no área de celdas. Se omiten máscaras, pads, encapsulado, test, costos fijos y rendimiento; el costo real no es necesariamente lineal. La elección ROM/FF es la decisión con mayor cambio de área de síntesis observado, por encima del pequeño contador de ciclos.')
ffdie=rows[FF_REF]['metrics'].get('design__die__area')
if ffdie is not None:p(f'Con los mismos 100 ns y 40 % de core objetivo, la referencia unificada {FF_REF} ocupa {ffdie/1e6:.6f} mm2 de die: US$ {ffdie*0.023:,.2f} en el mismo ejercicio lineal. Esta comparación explicita el efecto de conservar instrucciones en FF sobre el costo equivalente.')

page('7. Signoff e incidencia de antena')
tab([['Verificación final rom_100_40','Resultado'],['Magic DRC',m['magic__drc_error__count']],['Netgen LVS',m['design__lvs_error__count']],['Antena: nets / pins',str(m['antenna__violating__nets'])+' / '+str(m['antenna__violating__pins'])],['DRC de ruteo',m.get('route__drc_errors')],['Setup / hold en 9 corners','WNS=0 y TNS=0; WS mínimo no negativo']], [260,250])
p('El PDK no aporta un runset KLayout DRC en esta configuración: esa segunda comprobación se omite y LibreLane lo advierte. El DRC limpio acreditado aquí es Magic. KLayout sí realiza stream-out/render y la comparación XOR de las dos representaciones. Los reportes originales de signoff se adjuntan; no se presenta la omisión de KLayout DRC como una corrida ejecutada.')
p(f"Advertencias eléctricas conservadas: el flujo reporta {m.get('design__max_slew_violation__count')} incidencias de max slew y {m.get('design__max_cap_violation__count')} de max capacitance para la ROM, agregadas según las métricas multicorner de LibreLane. No son WNS/TNS ni errores DRC/LVS. El cierre aquí se limita a los criterios expresos del enunciado; estas advertencias requieren revisión adicional antes de usar el macro en una fabricación real.")
incident=json.loads((ROOT/'results/antenna_incident.json').read_text())
p(f"Ejemplo observado antes de reparar: pin {incident['victim']}, capa {incident['layer']}; razón parcial {incident['partial_ratio']:.2f}, límite {incident['required_ratio']:.2f} ({incident['multiplier']:.2f} veces). La carga acumulada durante fabricación podía dañar el óxido de la compuerta. LibreLane/OpenROAD insertó un diodo de antena conectado a la red para proporcionar una vía de descarga.")
figure(ROOT/'results/layout/antena_corregida.png',maxheight=260)
p('Rojo: celda que contiene el pin afectado. Verde: '+', '.join(d['name'] for d in incident['diodes'])+'. Ubicación final del pin/celda: '+str(incident['victim_box_um'])+' um. La imagen nativa de KLayout muestra las capas metálicas y las marcas derivadas de OpenDB; las capas auxiliares se ocultan para legibilidad. Fuente previa: 40-openroad-checkantennas/reports/antenna_summary.rpt; comprobación final: cero violaciones de antena.')

page('8. Layout anotado y localización de módulos')
p('Las capturas se generan con KLayout sobre el GDSII real. OpenROAD exporta los bounding boxes de instancias de la base OpenDB final; se seleccionan por sus nombres jerárquicos conservados. Las marcas de color son una superposición visual y no modifican el GDSII de entrega. Se ocultan capas auxiliares y se muestran metales atenuados para distinguir las celdas resaltadas.')
images=[]
for name in ['register_file','alu','contador']:
 img=Image(str(ROOT/'results/layout'/f'{name}.png'),width=214,height=221);images.append(img)
raw=Image(str(DATA/'rom_100_40/final/asic_top.png'),width=214,height=214)
t=Table([[images[0],images[1]],[images[2],raw]],colWidths=[255,255]);t.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')]));story.append(t)
tab([['Color / imagen','Nombre trazable'],['Amarillo / register file','u_soc.u_core.u_rf.*'],['Cian / ALU','u_soc.u_core.u_id.u_alu.*'],['Rosa / contador','u_soc.u_periph.u_cycle_counter.*'],['Inferior derecha','Vista global sin las marcas de selección']], [180,330])
p('layout_cells.json conserva nombre, tipo de celda y coordenadas; instance_areas.json conserva la atribución de área. Las imágenes originales de 1500 píxeles también se entregan para inspección ampliada. La dispersión de algunas celdas es consecuencia del placement y buffering, no significa que falte el módulo.')

page('9. Simulación funcional post-síntesis')
p('Se sintetizó una configuración de prueba con el mismo RTL y la biblioteca GF180 de la corrida final, deteniendo LibreLane después de Yosys.Synthesis. La simulación no anota SDF. Se compilan el netlist mapeado y los modelos gf180mcu_fd_sc_mcu7t5v0.v y primitives.v de la revisión instalada. El testbench aplica exactamente los mismos estímulos en flancos negativos tanto a RTL como a netlist.')
tab([['Comprobación','Resultado'],['Trazas de salidas ciclo a ciclo',str(proof['mapped_observed_cycles'])+' ciclos idénticos'],['Registro elapsed_q','Comprobado directamente en RTL y bits jerárquicos del netlist'],['Primer acierto','Objetivo ciclo 10754; pulsación 12254; captura 1503 ciclos en ambos'],['Pulsación incorrecta','Máscara 15: EE, LEDs apagados y repetición de la ronda'],['Partida completa','10 aciertos, promedio, variación y reinicio aprobados'],['Hash de ambas trazas',proof['mapped_sha256']]], [160,350])
p('El acceso de observación a elapsed_q no agrega lógica al diseño: el testbench lee los nombres preservados del netlist mediante gf180_elapsed.vh. El registro se contrasta con los ciclos esperados en cada ronda, además de comparar el comportamiento visible. La pulsación incorrecta no suma un acierto: la partida posterior requiere diez aciertos y mantiene el promedio correcto.')
tab([['Constante','Simulación RTL y netlist','Fabricación a 10 MHz'],['WAIT_CYCLES','3000','30000000'],['TENTH_CYCLES','1000','1000000'],['HOLD_CYCLES','2000','10000000'],['RELEASE_CYCLES','200','200000']], [180,165,165])
p('Se acortan las esperas únicamente en la imagen de simulación. Ambos niveles usan el mismo programa reducido y hash; no se compara una imagen final de tres segundos con otra reducida. También pasaron las pruebas de reset, byte enables, límites de dirección, protección ROM y escritura unificada, las cuatro pruebas del assembler y 32000 vectores por cada variante de ALU.')
h('Límites de la validación')
ff_proof=ROOT/'results/mapped_verification_ff.json'
if ff_proof.exists():
 fp=json.loads(ff_proof.read_text());assert fp['trace_equal'] and fp['direct_capture_register_asserted']
 p(f"Se repitió además la prueba completa para la memoria unificada con su propio netlist GF180: {fp['mapped_observed_cycles']} ciclos observados idénticos al RTL y captura elapsed_q comprobada directamente. Sus trazas, logs y netlist están en results/simulation_ff; la evidencia y hashes se registran en mapped_verification_ff.json.")
p('La validación requerida es funcional post-síntesis sin retardos. No se realizó simulación post-PnR con SDF. El cierre temporal se acredita mediante STA multicorner; el macro no es un chip completo listo para encapsular.')

page('10. Reproducibilidad y defensa')
tab([['Componente','Versión / revisión registrada'],['LibreLane','3.0.17; 64ef80802d3d189b476636d2a6b17888c03304ee'],['Yosys','0.62; 7326bb7d6641500ecb285c291a54a662cb1e76cf'],['OpenROAD','dcf36133a369abc8f3c5e5738cd4d82e4903c0e0'],['PDK gf180mcu','54435919abffb937387ec956209f9cf5fd2dfbee'],['Biblioteca','gf180mcu_fd_sc_mcu7t5v0'],['Entorno','Ubuntu WSL2; Nix 2.35.4; flake.lock adjunto']], [150,360])
p('Instalación: seguir la guía oficial de LibreLane para WSL2/Nix. En Ubuntu, tools/install_env_wsl.sh instala dependencias y Nix y clona la revisión exacta de LibreLane. tools/run_wsl.sh copia las fuentes a /opt/lab3/design y ejecuta comandos dentro del nix-shell fijado. Se evita copiar el repositorio de herramientas con finales de línea Windows: esa primera preparación falló y se sustituyó por un clone nativo Linux.')
for line in ['python3 tools/assembler.py sw/game.s sw/game.hex --asic-output rtl/generated','librelane --pdk gf180mcuD --run-tag final_repro config/rom_100_40.json','python3 tools/experiments.py --run --only rom_80_40,rom_63_40,rom_62_40 --jobs 2','bash tools/run_mapped_wsl.sh','python3 tools/collect_physical.py','python3 tools/analyze_synthesis.py']:
 p(line)
p('No actualizar LibreLane, el lock o el PDK entre comparaciones. Los JSON resueltos, reportes de timing por corner, estadísticas, netlists, GDSII, DEF, OpenDB y logs se conservan en results/physical. El README describe las rutas y cómo repetir la simulación y las corridas. Los experimentos rechazados permanecen visibles; Flow complete no se confunde con cumplimiento de los requisitos.')
h('Puntos para la defensa')
p('Cada integrante debe poder explicar por qué un .hex no inicializa silicio; la latencia del register file; cómo se cuentan las 99 palabras y los 0 datos usados; ROM frente a FF; atribución jerárquica del área; setup frente a hold y corners RC/PVT; causa y reparación de antena; terminales frente a pads; y por qué la frecuencia se obtiene de corridas que realmente cierran.')
h('Referencias')
for ref in ['Enunciado local Proyecto_3_arquitectura.pdf; correo del curso del 19/10/2026.','https://github.com/ABouchi05/Lab2-AdC','https://librelane.readthedocs.io/en/stable/','https://gf180mcu-pdk.readthedocs.io/en/latest/','https://openroad.readthedocs.io/en/latest/','https://www.klayout.de/doc/code/class_LayoutView.html']:
 p(ref)

def footer(canvas,doc):
 canvas.setFillColor(colors.HexColor('#526779'));canvas.setFont('Helvetica',8)
 canvas.drawString(40,24,'Proyecto 3 - Grupo 18 | Evidencia de corridas GF180MCU')
 if DRAFT:
  canvas.setFillColor(colors.HexColor('#ad3b35'));canvas.drawString(40,816,'BORRADOR DE REVISIÓN - comparaciones pendientes')
 canvas.drawRightString(555,24,str(doc.page))
dest=ROOT/('build/pdf/informe_preview.pdf' if DRAFT else 'Proyecto_3.pdf');dest.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(dest),pagesize=(595,842),leftMargin=40,rightMargin=40,topMargin=38,bottomMargin=42)
doc.build(story,onFirstPage=footer,onLaterPages=footer);print(dest)
