# Evidencia conservada

- `physical/summary.json`: métricas de 13 estudios y tres controles exploratorios que explican la decisión física. Los intentos rechazados o interrumpidos conservan su estado real.
- Cada estudio contiene configuración resuelta, estado final disponible, log del flujo, estadísticas de síntesis y resumen original de timing de los nueve corners.
- Se conservan reportes detallados de setup/hold en tres corners representativos para las dos referencias, y en el corner lento para el límite ROM de 63/62 ns. El resto de métricas completas está también en latest_state.json.
- `physical/rom_100_40/final`: GDSII, DEF, OpenDB, LEF, netlist, SDC, SPICE y vista del macro final.
- Los subdirectorios signoff conservan los reportes originales finales de DRC, LVS, antena y manufacturabilidad. Las antenas previas relevantes se conservan como incidentes corregidos.
- `simulation` y `simulation_ff`: trazas completas y netlists GF180 de prueba, comprimidos sin pérdida, con sus hashes. Ambas estrategias aprobaron 89186 ciclos.
- `fpga_audit.log`: error real de primitivas del diseño FPGA original. `layout` y `plots`: figuras utilizadas en el PDF.
- `environment.txt`, `pdk_sources.txt`, `pdk_manifest.json`, `toolchain_flake.lock`: herramientas y PDK realmente utilizados.

Las rutas /opt/lab3 dentro de logs/estados son procedencia histórica. El README indica cómo reconstruir el entorno; no se requieren archivos temporales de otra máquina para leer la entrega o ejecutar las pruebas desde sus fuentes.
