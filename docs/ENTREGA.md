# Índice de entrega del Proyecto 3

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
