# Proyecto 3 - Pochoco SoC a ASIC

Arquitectura de Computadores - Grupo 18. Derivado del [Proyecto 2 del grupo](https://github.com/ABouchi05/Lab2-AdC), commit `4a0a9128566306269fa97b195bb28ef2fa42885f`.

## Resultado final

La corrida elegida es **rom_100_40**, a 100 ns (10 MHz) y 40 % de core objetivo. Completó LibreLane con **Magic DRC=0, Netgen LVS=0 y antena=0**. En los nueve corners, setup y hold tienen WNS=0 y TNS=0. Slack mínimo de setup: 37.342553 ns; de hold: 0.171039 ns.

Área de celdas de síntesis: 163731.1872 um2. Die reportado: 438409 um2. Costo equivalente del ejercicio: US$ 10,083.41. La frecuencia máxima verificada de la arquitectura ROM en el barrido es 15.873 MHz; la operación final sigue siendo a 10 MHz.

- [Informe final](Proyecto_3.pdf)
- [GDSII final](results/physical/rom_100_40/final/asic_top.gds)
- [Resumen de métricas](results/physical/summary.json)
- [Prueba funcional GF180](results/mapped_verification.json)
- [Capturas anotadas](results/layout)

## Dos estrategias de memoria

| Estrategia | Corrida de referencia | Área síntesis (um2) | FF | Fmáx verificada (MHz) |
|---|---|---:|---:|---:|
| ROM + RAM reducida | rom_100_40 | 163731.1872 | 914 | 15.873 |
| Unificada FF | ffq_100_40 | 597386.3616 | 4083 | 10.000 |

El programa contiene 99 palabras (396 bytes). Usa 0 palabras RAM de datos: todas las cargas y stores se realizan a MMIO desde x2=0x80000000 y el estado queda en registros. Se reserva una palabra en 0x18c. Unified=0 genera ROM combinacional con respuesta registrada y RAM de una palabra; Unified=1 genera 100 palabras FF escribibles y cargadas por reset. No se usa readmemh, initial ni primitivas FPGA en el conjunto ASIC. El SPI es el periférico del SoC, no un bootloader.

Las corridas ffp usan la misma memoria FF con separación de cuatro sitios entre celdas (GPL_CELL_PADDING=DPL_CELL_PADDING=4). ffq fija además PL_TARGET_DENSITY_PCT=60: el ensayo con densidad automática de 73,15 % falló por congestión global. La densidad de placement no es FP_CORE_UTIL, que sigue en 40 %. Se conserva la configuración resuelta de cada corrida; las pruebas interrumpidas se identifican en results/interrupted_experiments.json y nunca se usan para afirmar cierre o Fmáx.

Advertencias eléctricas de la ROM: 2549 incidencias de max slew y 7 de max capacitance según las métricas agregadas del flujo. Se conservan en los logs; el cierre informado corresponde a los criterios expresos del enunciado y no sustituye una revisión para fabricación real.

## Versiones exactas

- LibreLane 3.0.17, commit `64ef80802d3d189b476636d2a6b17888c03304ee`.
- Yosys 0.62, commit `7326bb7d6641500ecb285c291a54a662cb1e76cf`.
- OpenROAD `dcf36133a369abc8f3c5e5738cd4d82e4903c0e0`.
- PDK gf180mcuD, paquete open_pdks `54435919abffb937387ec956209f9cf5fd2dfbee`.
- Biblioteca `gf180mcu_fd_sc_mcu7t5v0`.
- Ubuntu/WSL2 y Nix 2.35.4. El lock exacto está en results/toolchain_flake.lock; environment.txt y pdk_sources.txt registran la procedencia real.

## Regeneración del programa

```sh
python tools/assembler.py sw/game.s sw/game.hex --asic-output rtl/generated
python -m unittest discover -s tests -v
```

A 100 ns, game.s usa WAIT=30000000, TENTH=1000000, HOLD=10000000 y RELEASE=200000. El assembler genera también símbolos, cantidades y hash. Las esperas de simulación se generan aparte: WAIT=3000, TENTH=1000, HOLD=2000 y RELEASE=200; ambos niveles simulados usan exactamente esa imagen.

## Instalación y corrida final

En Windows se requiere WSL2 con Ubuntu. Seguir la [instalación oficial](https://librelane.readthedocs.io/en/stable/installation/nix_installation/installation_win.html). Desde PowerShell en la carpeta del proyecto:

```powershell
wsl -d Ubuntu -u root -- bash tools/install_env_wsl.sh
wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'librelane --pdk gf180mcuD --run-tag final_repro config/rom_100_40.json'
```

El instalador clona LibreLane dentro del sistema Linux y fija su commit. run_wsl.sh copia únicamente fuentes a /opt/lab3/design y entra al nix-shell fijado. CIEL descarga el PDK compatible si falta. No copiar el checkout de herramientas con finales CRLF: los scripts y parches de Nix requieren LF. .gitattributes conserva LF en scripts y fuentes.

En otro Linux, instalar Nix según la documentación oficial, clonar LibreLane en el commit indicado y entrar a nix-shell. Desde la raíz del proyecto, ejecutar `librelane --pdk gf180mcuD --run-tag final_repro config/rom_100_40.json`. No actualizar herramientas ni PDK entre comparaciones.

## Barridos y criterio de cierre

tools/experiments.py genera las configuraciones; --run ejecuta y conserva el retorno y duración de cada caso. Usar --only para seleccionar corridas y --jobs para limitar concurrencia. La matriz completa incluye intentos que no cierran y pruebas exploratorias largas; no todas son parte de la entrega final aceptada.

**Flow complete no basta.** Se comprueban los nueve corners RC min/nom/max cruzados con tt 25C/5V, ss 125C/4,5V y ff -40C/5,5V. El PDK limitaba setup a *tt* por defecto; se añadieron TIMING_VIOLATION_CORNERS, SETUP_VIOLATION_CORNERS y HOLD_VIOLATION_CORNERS con ["*"]. Se repitieron los verificadores de 100/80/60 ns: 100 y 80 pasan; 60 se rechaza. El mínimo se toma solo de corridas con flujo completo, DRC/LVS limpios, antena resuelta y WS>=0/TNS=0 de setup y hold.

Cada período puede cambiar optimización, buffering y placement. La frecuencia reportada es la mayor verificada entre los puntos ensayados, no una extrapolación 1/(T-slack) ni una demostración de óptimo continuo. El juego final sigue usando el reloj y constantes de 10 MHz.

## Simulación post-síntesis

```powershell
wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'bash tools/run_mapped_wsl.sh'
```

Se sintetiza la imagen reducida con GF180, se compilan los modelos de celdas y primitives.v y se ejecuta el mismo testbench sin SDF. Pasaron 89186 ciclos idénticos, una pulsación incorrecta, diez rondas, promedio y reinicio. El registro elapsed_q se verifica directamente tanto en RTL como en el netlist mediante los nombres preservados de cada bit. El primer acierto captura 1503 ciclos en ambos. Las trazas comprimidas, hash, programa y netlist de prueba están en results/simulation.

Las pruebas adicionales verifican memoria escribible, byte enables, reset, protección ROM y ausencia de alias de direcciones. Ambas variantes de ALU pasaron 32000 vectores. La candidata carry-select reduce marginalmente área pero empeora el slack global a 100 ns; se conserva la referencia.

## Trazabilidad, layout y alimentación

Register file: u_soc.u_core.u_rf; ALU: u_soc.u_core.u_id.u_alu; contador: u_soc.u_periph.u_cycle_counter. La síntesis usa deferred_flatten. analyze_synthesis.py suma áreas Liberty por instancia, guarda el detalle y coincide con stat.json. layout_cells.json relaciona nombres y coordenadas OpenDB. Las capturas se renderizan en KLayout sobre el GDSII real, con superposición de celdas por nombre; no alteran el GDSII de entrega.

El macro expone reloj, reset activo bajo, botones, LEDs, displays activos bajos y SPI. Son terminales lógicos, no pads con ESD/driver. Mantener reset activo al menos cinco ciclos y liberarlo sincronizado. La PDN usa rails Metal1 de 0,6 um y straps Metal4/Metal5 de 1,6 um; PDN_CORE_RING=False. Los reportes de conectividad se conservan.

Magic DRC y Netgen LVS son las verificaciones de signoff acreditadas. No hay runset KLayout DRC en este PDK y se registra su omisión; KLayout sí realiza stream-out, render y XOR. La incidencia de antena mosi_sync[0] (460,48 frente al límite 400) se corrigió con ANTENNA_1 y quedó en cero; ver antenna_incident.json y la captura anotada.

## Evidencia y tamaños

results/physical contiene configuraciones resueltas, estados, métricas, síntesis y reportes por corner. Los reportes grandes usan gzip sin pérdida (.rpt.gz); se pueden abrir con gzip -dk o Python gzip. Los archivos originales completos permanecen en Ubuntu, /opt/lab3/design/config/runs. Se entrega el conjunto de vistas físicas del macro elegido; las vistas voluminosas de alternativas se pueden regenerar y quedan fuera del paquete principal.

El costo equivalente usa área de die x US$23000/mm2. Omite pads, encapsulado, máscaras, test, rendimiento y costos fijos. No se realizó simulación post-PnR con SDF.

## Regenerar informe y paquete

Para regenerar el informe usando la evidencia incluida: instalar requirements-report.txt y ejecutar `python tools/plot_physical.py` y `python tools/final_report.py`. No es necesario repetir LibreLane. Para recalcular las áreas de las dos referencias, ejecutar `python tools/analyze_synthesis.py`. Para construir y validar nuevamente este ZIP, ejecutar `python tools/package_delivery.py`. Para recopilar corridas nuevas completas, ejecutar tools/collect_physical.py desde WSL con --runs y --out apuntando a las carpetas correspondientes. El índice [docs/ENTREGA.md](docs/ENTREGA.md) explica exactamente qué evidencia se conserva.

## Referencias

[Enunciado](Proyecto_3_arquitectura.pdf) y correo del curso del 19/10/2026; [LibreLane](https://librelane.readthedocs.io/en/stable/), [GF180MCU](https://gf180mcu-pdk.readthedocs.io/en/latest/), [OpenROAD](https://openroad.readthedocs.io/en/latest/).

La simulación adicional GF180 de la unificada también aprobó los 89186 ciclos y la captura directa; ver results/mapped_verification_ff.json y results/simulation_ff.

## Comprobación local de esta entrega

Ejecutar desde la carpeta descomprimida: `python tools/validate_delivery.py .`. Para repetir las pruebas del assembler: `python -m unittest discover -s tests -v`. Con Icarus Verilog y Yosys instalados, `python tools/verify.py` repite la regresión funcional de ambas memorias. Los comandos WSL anteriores repiten la simulación GF180 y la implementación física.

Para entregar en GitHub se debe publicar el contenido descomprimido, con README.md en la raíz. El ZIP no contiene credenciales, dependencias instaladas ni una carpeta .git. La defensa presencial corresponde a los integrantes.
