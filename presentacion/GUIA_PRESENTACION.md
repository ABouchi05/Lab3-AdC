# Guía Completa para la Presentación Presencial - Proyecto 3 (Pochoco SoC a ASIC)

**Ruta del proyecto (Windows):** `C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final`  
**Ruta equivalente dentro de Ubuntu (WSL):** `/mnt/c/Users/anton/OneDrive/Escritorio/Lab3AdC/output/proyecto3/proyecto3_final`

---

## 1. ¿Cuál es el "código principal" y cómo arrancar la presentación? (Sin FPGA)

En los proyectos anteriores lo primero que hacían era programar la FPGA y mostrar que el juego prendía. En este proyecto **no hay placa física** porque diseñaron un **chip real a medida (ASIC)** en tecnología de 180 nm (`gf180mcuD`). Aquí el equivalente a "correr el código principal y ver que funciona" se divide en **3 piezas clave**:

### A. El "código principal" del hardware (`rtl/asic_top.v`)
- **`rtl/asic_top.v`** es el módulo superior (el chip completo) sin primitivas de FPGA. Expone los pines lógicos (`clk_i`, `rst_ni`, `buttons_i[3:0]`, `leds_o[3:0]`, `segment1_o[6:0]`, `segment2_o[6:0]`, `spi_sclk_i`, `spi_mosi_i`, `spi_cs_ni`, `spi_miso_o`) e instancia adentro a **`rtl/pochoco_soc.v`**.
- **`rtl/pochoco_soc.v`** conecta las 3 partes del sistema:
  1. **El núcleo RISC-V (`rtl/espino_core/espino_core.v`)**: contiene la etapa Fetch (`espino_if_stage.v`), Decode (`espino_id_stage.v`, `espino_decoder.v`, `espino_controller.v`), la ALU (`espino_alu.v`), el banco de registros en Flip-Flops (`espino_register_file.v`) y la unidad Load/Store (`espino_load_store_unit.v`).
  2. **La memoria ASIC (`rtl/generated/asic_memory.v`)**: generada automáticamente desde el programa assembler **`sw/game.s`** con `tools/assembler.py`, donde el parámetro `Unified` elige entre la arquitectura **ROM + 1 palabra RAM (`Unified=0`)** y la **Memoria Unificada en Flip-Flops (`Unified=1`)**.
  3. **Los periféricos (`rtl/pochoco_periph.v`, `rtl/cycle_counter.v` y `rtl/pochoco_spi_slave.v`)**: controlan los displays de 7 segmentos, LEDs, botones, el contador de ciclos de 32 bits y el esclavo SPI.

### B. El "archivo principal" que fabrica el chip (`config/rom_100_40.json` + LibreLane)
- En vez de darle a *Generate Bitstream* en Vivado/iCEcube2, aquí le pasas **`config/rom_100_40.json`** a **LibreLane**:
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'librelane --pdk gf180mcuD --run-tag demo_vivo config/rom_100_40.json'
  ```
- Ese comando toma tus archivos `.v`, los sintetiza a compuertas reales de 180 nm, arma el *Floorplan*, posiciona las celdas (*Placement*), crea el árbol de reloj (*CTS*), cablea todas las pistas de metal (*Routing*) y verifica que no haya errores físicos (*DRC, LVS, Antena y Timing en los 9 corners*).
- **El resultado final** (el equivalente al `.bit` de la FPGA, pero para mandar a la fábrica de silicio) es el archivo **`results/physical/rom_100_40/final/asic_top.gds`**, que muestras abierto en **KLayout**.

### C. Cómo demostrar en vivo que el procesador ejecuta el juego de verdad (Simulación RTL y Post-Síntesis)
Como no hay FPGA en la mesa, demuestras que el chip ejecuta el juego corriendo los testbenches del sistema (`tests/tb_asic.v`, `tests/tb_memory.v`, `tests/tb_alu.v`):
- **Regresión completa con compuertas reales GF180 (`tools/run_mapped_wsl.sh`)**:
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'bash tools/run_mapped_wsl.sh'
  ```
  Sintetiza el chip con Yosys hacia celdas del PDK `gf180mcu_fd_sc_mcu7t5v0` y simula con `iverilog` los **89,186 ciclos** completos de una partida (incluyendo error de botón mostrando `EE`, 10 rondas válidas, promedio y reinicio), comprobando ciclo a ciclo que el netlist físico del chip responde idéntico al RTL (`PASS GF180 post-synthesis functional regression 89186 cycles`).
- **Regresión completa de ambas memorias (`ROM` vs `FF`) y ALU (`tools/verify.py`)**:
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'python3 tools/verify.py'
  ```
  Verifica `tb_memory.v`, `tb_alu.v` y la partida completa de 89,186 ciclos comparando `Unified=0` (ROM) contra `Unified=1` (FF) en RTL y post-síntesis (`PASS: both memories; RTL == generic post-synthesis each clock; full game regression`).

### Guion para tus primeros 60 segundos frente al profesor:
1. **Muestras KLayout ya abierto** con `asic_top.gds`: *"Acá tenemos el layout final GDSII de nuestro SoC completo (`asic_top.v`) integrado en 180 nm con la memoria de programa en ROM (`rom_100_40`), cerrado sin violaciones de DRC, LVS, Antena ni Timing en los 9 corners"*.
2. **Muestras en VS Code `rtl/asic_top.v`, `rtl/pochoco_soc.v` y `config/rom_100_40.json`**: *"Este es nuestro módulo top limpio de primitivas de FPGA y esta es la configuración con la que LibreLane genera el chip"*.
3. **Le preguntas al profesor**: *"¿Quiere que dejemos corriendo una corrida de LibreLane o la simulación post-síntesis del juego de fondo mientras le mostramos las métricas de área, frecuencia máxima, camino crítico y DRC/LVS/Antena?"*

---

## 2. Preparación 5 minutos antes de entrar a presentar

Antes de que empiece tu turno, deja preparadas **4 cosas** en tu computador:

1. **VS Code** abierto en la carpeta `C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final`.
2. **El PDF del informe** (`Proyecto_3.pdf`) abierto para mostrar tablas, gráficos o diagramas si te preguntan algo teórico.
3. **Una pestaña de PowerShell** parada en la carpeta del proyecto:
   ```powershell
   cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
   ```
4. **Una pestaña de Ubuntu con `nix-shell` ya iniciado** (y **KLayout** ya abierto con el chip en pantalla, porque tarda unos segundos en abrir).

### ¿Cómo dejar la pestaña de Ubuntu + `nix-shell` lista?
En una ventana de PowerShell ejecuta:
```powershell
cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
wsl -d Ubuntu -u root
```
Y una vez adentro de Ubuntu (`root@...#`), ejecuta:
```bash
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && cd /opt/lab3/librelane-linux && nix-shell
```
Cuando aparezca `[nix-shell:/opt/lab3/librelane-linux]#`, ya tienes todas las herramientas de diseño de chips (`librelane`, `klayout`, `openroad`, `yosys`, `magic`, `netgen`, `iverilog`) activadas y listas para usar sin esperas.

---

## 3. Comandos para abrir herramientas "no comunes" (KLayout, OpenROAD GUI, reportes `.gz`)

Ahora que tu ruta (`C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final`) **no tiene espacios**, ningún comando fallará por comillas.

### A. Abrir el layout final (GDSII) en KLayout (Ventana Gráfica)

- **Si estás dentro de la pestaña de `nix-shell` en Ubuntu (Recomendado):**
  ```bash
  klayout -nn /opt/lab3/pdks/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyt -l /opt/lab3/pdks/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyp /mnt/c/Users/anton/OneDrive/Escritorio/Lab3AdC/output/proyecto3/proyecto3_final/results/physical/rom_100_40/final/asic_top.gds
  ```

- **O si prefieres lanzarlo directo desde PowerShell:**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- bash -lc '. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && export NIX_BUILD_SHELL=/bin/bash && cd /opt/lab3/librelane-linux && nix-shell --run "klayout -nn /opt/lab3/pdks/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyt -l /opt/lab3/pdks/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyp /mnt/c/Users/anton/OneDrive/Escritorio/Lab3AdC/output/proyecto3/proyecto3_final/results/physical/rom_100_40/final/asic_top.gds"'
  ```

#### Cómo manejar KLayout frente al profesor:
- **Al abrir por primera vez**: Si sale el cartel preguntando por *Show full hierarchy mode*, dale a **Yes** (así dibuja todas las celdas internas de inmediato).
- **Zoom**: Rueda del ratón, o selecciona un área arrastrando con el **clic derecho**.
- **Ajustar todo el chip a la pantalla**: Presiona la tecla **`F`** (*Fit*).
- **Ver el interior de las celdas estándar (transistores y ruteo interno)**: Presiona **`Shift + F`** (o menú superior `Display` → `Full Hierarchy`). Si solo se ven cajas vacías, `Shift + F` muestra todo el contenido.
- **Prender/apagar capas de metal**: En el panel derecho (*Layers*), haz **doble clic** sobre cualquier capa para ocultarla o mostrarla (o clic derecho → *Hide All* y luego doble clic en la que quieras enseñar):
  - **`Metal1` (`34/0`)**: Rieles horizontales de alimentación (`VDD`/`VSS`) de las celdas estándar (`0.6 um`) y ruteo local.
  - **`Metal2` (`36/0`) y `Metal3` (`42/0`)**: Ruteo de señales intermedias y pines de entrada/salida en los bordes del die (`#N`: displays `segment1_o`/`segment2_o`, `#S`: `clk_i`/`rst_ni`, `#E`: `leds_o`/`buttons_i`, `#W`: interfaz SPI).
  - **`Metal4` (`46/0`, vertical) y `Metal5` (`81/0`, horizontal)**: *Straps* gruesos (`1.6 um`, pitch ~`153.6 um` / `153.18 um`) de la red de distribución de potencia (PDN), con `PDN_CORE_RING=False` (sin anillo de pads).

---

### B. Abrir OpenROAD GUI (para ver Placement, árbol de reloj CTS o congestión)

- **Desde tu pestaña de `nix-shell` en Ubuntu:**
  ```bash
  openroad -gui
  ```
- **Desde PowerShell:**
  ```powershell
  wsl -d Ubuntu -u root -- bash -lc '. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && export NIX_BUILD_SHELL=/bin/bash && cd /opt/lab3/librelane-linux && nix-shell --run "openroad -gui"'
  ```
- **Nota útil**: En `results/physical/rom_100_40/final/asic_top.odb` está la base de datos OpenDB final dentro de tu repositorio, y las corridas completas originales (con todas las bases de datos `.odb` de cada etapa intermedia) están guardadas dentro de Ubuntu en `/opt/lab3/design/config/runs/`. Puedes listarlas dentro de Ubuntu con:
  ```bash
  ls -la /opt/lab3/design/config/runs/
  ```

---

### C. Abrir reportes de Timing comprimidos (`.rpt.gz`)

En `results/physical/rom_100_40/timing/55-openroad-stapostpnr/` están el resumen general (`summary.rpt`), las rutas críticas (`critical_paths.json`) y los reportes detallados comprimidos en `.rpt.gz` para tres corners (`nom_tt_025C_5v00`, `max_ss_125C_4v50` y `min_ff_n40C_5v50`). Si el profesor pide abrir uno en vivo:

- **Ver las primeras 85 líneas directo en la terminal (PowerShell):**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- zcat results/physical/rom_100_40/timing/55-openroad-stapostpnr/max_ss_125C_4v50/max.rpt.gz | Select-Object -First 85
  ```
- **O para el corner nominal (`nom_tt_025C_5v00`):**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- zcat results/physical/rom_100_40/timing/55-openroad-stapostpnr/nom_tt_025C_5v00/max.rpt.gz | Select-Object -First 85
  ```
- **O descomprimirlo conservando el `.gz` (`-dk`) y abrirlo en VS Code:**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- gzip -dk results/physical/rom_100_40/timing/55-openroad-stapostpnr/max_ss_125C_4v50/max.rpt.gz
  code results/physical/rom_100_40/timing/55-openroad-stapostpnr/max_ss_125C_4v50/max.rpt
  ```
  *(Nota: recuerda borrar luego el archivo `.rpt` descomprimido con `Remove-Item results/physical/rom_100_40/timing/55-openroad-stapostpnr/max_ss_125C_4v50/max.rpt` para mantener limpio el árbol de entrega).*

---

## 4. ¿Qué nos van a pedir hacer o cambiar en vivo?

Según el enunciado (`Proyecto_3_arquitectura.pdf`):
> *"Durante la defensa se harán preguntas sobre cualquier parte del informe, del RTL y del assembler. Todos los integrantes deben poder responder."*

Aquí tienes los **5 ejercicios en vivo** que te pueden pedir y cómo resolverlos al instante:

### Ejercicio en vivo 1: "Modifiquen el período de reloj (`CLOCK_PERIOD`) o la utilización (`FP_CORE_UTIL`) y ejecuten LibreLane"
1. En VS Code, abre `config/rom_100_40.json`.
2. Ubica las líneas 20 y 21:
   ```json
   "CLOCK_PERIOD": 100,
   "FP_CORE_UTIL": 40,
   ```
   Cámbialas al valor que te pida el profesor (por ejemplo `"CLOCK_PERIOD": 80` o `"FP_CORE_UTIL": 50`) y guarda el archivo (`Ctrl + S`).
3. En PowerShell (parado en `C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final`), ejecuta:
   ```powershell
   wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'librelane --pdk gf180mcuD --run-tag demo_vivo config/rom_100_40.json'
   ```
   *(El script `tools/run_wsl.sh` copia automáticamente tus carpetas `rtl`, `sw`, `tools`, `tests`, `config` desde Windows hacia `/opt/lab3/design` en Linux y lanza LibreLane dentro de `nix-shell`. La arquitectura ROM tarda solo ~3 a 4 minutos en completar el flujo).*

---

### Ejercicio en vivo 2: "Cambien entre la estrategia de memoria ROM y la estrategia de Memoria Unificada con Flip-Flops"
1. Muestra en `config/rom_100_40.json` la línea 25:
   ```json
   "SYNTH_PARAMETERS": [
     "Unified=0"
   ],
   ```
   - Con `Unified=0` (`config/rom_100_40.json`), el módulo `rtl/generated/asic_memory.v` sintetiza las 99 palabras del programa como una **ROM combinacional** con salida registrada más **1 palabra de RAM** de reserva en `0x18c`.
   - Con `Unified=1` (`config/ffq_100_40.json`), sintetiza las **100 palabras completas de 32 bits como bancos de Flip-Flops** inicializados por reset (`rst_ni`) y escribibles por byte.
2. Si te piden lanzar la corrida de Flip-Flops en vivo:
   ```powershell
   wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'librelane --pdk gf180mcuD --run-tag demo_ff config/ffq_100_40.json'
   ```

---

### Ejercicio en vivo 3: "Cambien una constante o instrucción en el programa RISC-V (`sw/game.s`) y regeneren la memoria"
Si te preguntan cómo se traduce el programa assembler a hardware sin usar `$readmemh` o cómo se recalculan las constantes del juego para el reloj objetivo ($N = t / T$):
1. Abre `sw/game.s` y muestra las líneas 2 a 5:
   ```asm
   .equ WAIT_CYCLES, 30000000
   .equ TENTH_CYCLES, 1000000
   .equ HOLD_CYCLES, 10000000
   .equ RELEASE_CYCLES, 200000
   ```
   - Explica el cálculo para $T = 100\text{ ns}$ ($10\text{ MHz}$):
     - `WAIT_CYCLES` ($3\text{ s}$): $3\text{ s} / 100\text{ ns} = 30,000,000\text{ ciclos}$.
     - `TENTH_CYCLES` ($0.1\text{ s}$): $0.1\text{ s} / 100\text{ ns} = 1,000,000\text{ ciclos}$.
     - `HOLD_CYCLES` ($1\text{ s}$): $1\text{ s} / 100\text{ ns} = 10,000,000\text{ ciclos}$.
     - `RELEASE_CYCLES` ($0.02\text{ s}$): $0.02\text{ s} / 100\text{ ns} = 200,000\text{ ciclos}$.
   - *(Si el profesor te pide calcularlas para otro período $T$, por ejemplo $T = 80\text{ ns}$ ($12.5\text{ MHz}$), divides cada tiempo entre $80\text{ ns}$: `WAIT_CYCLES = 37500000`, `TENTH_CYCLES = 1250000`, `HOLD_CYCLES = 12500000`, `RELEASE_CYCLES = 250000`).*
2. Ejecuta desde PowerShell el ensamblador y generador de hardware:
   ```powershell
   cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
   python tools/assembler.py sw/game.s sw/game.hex --asic-output rtl/generated
   ```
3. Abre `rtl/generated/asic_memory.v` y `rtl/generated/program.json` para mostrar cómo se regeneró la tabla `case` de la ROM, los valores de reset de los Flip-Flops y el manifiesto con el conteo de palabras y hash SHA-256.
4. Corre además los tests unitarios del ensamblador:
   ```powershell
   python -m unittest discover -s tests -v
   ```

---

### Ejercicio en vivo 4: "Corran la simulación funcional post-síntesis (Gate-Level Simulation con celdas GF180)"
Para demostrar que el netlist sintetizado con compuertas reales del PDK `gf180mcu_fd_sc_mcu7t5v0` hace exactamente lo mismo que el RTL original:
```powershell
cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'bash tools/run_mapped_wsl.sh'
```
*(Y si piden la de memoria unificada FF: `wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'bash tools/run_mapped_ff_wsl.sh'`).*
Esto sintetiza el SoC con Yosys hacia celdas GF180 (usando constantes acortadas de simulación: `WAIT=3000`, `TENTH=1000`, `HOLD=2000`, `RELEASE=200`), compila con `iverilog` junto a `primitives.v` y `gf180mcu_fd_sc_mcu7t5v0.v`, y simula los **89,186 ciclos** completos del juego (error de botón con máscara 15 mostrando `EE` y repitiendo ronda, 10 rondas válidas, cálculo del promedio y reinicio), comprobando directamente el registro `elapsed_q` en RTL y en los bits preservados del netlist (`tests/gf180_elapsed.vh`), donde el primer acierto captura exactamente **1,503 ciclos** en ambos.

---

### Ejercicio en vivo 5: "Validen la integridad completa de la entrega"
Para verificar instantáneamente los 364 archivos del paquete, sus hashes SHA-256, los 9 corners de las corridas de referencia y las trazas de 89,186 ciclos:
```powershell
cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
python tools/validate_delivery.py .
```

---

## 5. Mapa rápido de archivos para mostrar cuando te pidan evidencia

Cuando el profesor te pida ver un resultado específico, abre directamente estos archivos en VS Code:

| Qué te pide el profesor | Archivo exacto a abrir en `proyecto3_final` |
|---|---|
| **Auditoría de dependencias FPGA (Act. 3.1)** | `results/fpga_audit.log` (líneas 10-14 y 26-30: `%Error-MODMISSING: SB_RAM40_4K`) |
| **Métricas finales del chip ganador (`rom_100_40`)** | `results/physical/rom_100_40/latest_state.json` |
| **Resumen comparativo de las 16 corridas (ROM vs FF, frecuencias, áreas)** | `results/physical/summary.json` |
| **Cantidad de celdas y área de síntesis (Yosys)** | `results/physical/rom_100_40/synthesis/stat.rpt` y `results/physical/rom_100_40/synthesis/stat.json` |
| **Área desglosada por submódulo y Top 5 celdas (`u_rf`, `u_alu`, `u_cycle_counter`, memoria)** | `results/physical/rom_100_40/synthesis/area_analysis.json` y `results/physical/ffq_100_40/synthesis/area_analysis.json` |
| **Resumen STA multicorner y ruta crítica post-PnR** | `results/physical/rom_100_40/timing/55-openroad-stapostpnr/summary.rpt` y `critical_paths.json` |
| **Reporte Magic DRC (`0` violaciones)** | `results/physical/rom_100_40/signoff/64-magic-drc/reports/drc.magic.rpt` (y `magic-drc.log`) |
| **Reporte Netgen LVS (`Circuits match uniquely`, `0` errores)** | `results/physical/rom_100_40/signoff/70-netgen-lvs/reports/lvs.netgen.rpt` (y `netgen-lvs.log`) |
| **Reportes de Antena (antes y después de reparar)** | `results/physical/rom_100_40/signoff/40-openroad-checkantennas/reports/antenna_summary.rpt` (antes) y `46-openroad-checkantennas-1/reports/antenna_summary.rpt` (después) |
| **Evidencia de la violación de antena en `mosi_sync[0]` y su reparación** | `results/antenna_incident.json` y `results/layout/antena_corregida.png` |
| **Capturas del layout con bloques resaltados (RF, ALU, Contador)** | Carpeta `results/layout/` (`register_file.png`, `alu.png`, `contador.png`) y `results/physical/rom_100_40/final/asic_top.png` |
| **Gráfico de utilización vs. congestión de ruteo** | `results/plots/utilizacion_congestion.png` y `results/plots/plot_data.json` |
| **Verificación post-síntesis GF180 (ROM y FF)** | `results/mapped_verification.json` y `results/mapped_verification_ff.json` (logs en `results/rtl_game.log` y `results/mapped_game.log`) |
| **Comparación de arquitectura de ALU (Referencia vs Carry-Select)** | `results/physical/rom_fast_100_40/synthesis/area_analysis.json`, `results/physical/rom_fast_100_40/latest_state.json`, `results/alu_False.log` y `results/alu_True.log` |

---

## 6. Preguntas y Respuestas Clave que debes dominar para la defensa

### 1. ¿Qué cambios de diseño hicieron para pasar del Proyecto 2 (FPGA) al Proyecto 3 (ASIC)? (Actividad 3.1)
- **Módulo superior `rtl/asic_top.v` sin primitivas de FPGA**: Expone solo las señales lógicas del juego (`clk_i`, `rst_ni`, `buttons_i[3:0]`, `leds_o[3:0]`, `segment1_o[6:0]`, `segment2_o[6:0]`, `spi_sclk_i`, `spi_mosi_i`, `spi_cs_ni`, `spi_miso_o`). Son terminales lógicos del macro digital, no pads de I/O con protección ESD ni buffers de potencia.
- **Primitiva `SB_RAM40_4K` en el Register File**: Al correr la auditoría del RTL original (`results/fpga_audit.log`, líneas 10-14 y 26-30), Verilator/LibreLane se detuvo en la etapa 1 (`Verilator.Lint`) con 2 errores `%Error-MODMISSING: Cannot find file containing module: 'SB_RAM40_4K'` (líneas 22 y 33 del register file original de iCE40). Se reemplazó en `rtl/espino_core/espino_register_file.v` por un banco de **15 registros de 32 bits en Flip-Flops** (`x1`..`x15`, con `x0` cableado a 0) y **dos puertos de lectura registrados** para mantener exactamente la latencia de 1 ciclo que espera el núcleo Espino.
- **Bloques `initial` y `$readmemh`**: No produjeron un mensaje separado en `fpga_audit.log` porque el flujo abortó antes en el lint por `SB_RAM40_4K`, pero en silicio real no existe un archivo `.hex` que cargue los flip-flops o SRAM al encender. Se reemplazaron generando hardware explícito en `rtl/generated/asic_memory.v` desde `tools/assembler.py`.
- **Power-On Reset (`por_cnt = 0`) y Reset explícito**: En FPGA un contador inicializado con `initial` generaba el reset interno; en ASIC los FFs despiertan en estado aleatorio (`X`), por lo que se eliminó `por_cnt` y se expuso `rst_ni` activo bajo para todos los FFs del diseño (manteniéndolo activo al menos 5 ciclos y liberándolo sincronizado).
- **Reloj y constantes del software**: En el Proyecto 2 el reloj efectivo del SoC era de 25 MHz; para el objetivo ASIC de `CLOCK_PERIOD = 100 ns` (**10 MHz**), no es un error de LibreLane sino un supuesto temporal del software, por lo que recalculamos las constantes en `sw/game.s`.

### 2. ¿Cómo determinaron cuántas palabras de instrucciones y datos usa el juego, y por qué eligieron ROM sobre Flip-Flops? (Actividad 3.2)
- **Conteo real de palabras (`99` de instrucciones y `0` de RAM de datos usadas)**:
  - Al ensamblar `sw/game.s`, `tools/assembler.py` genera exactamente **99 instrucciones de 32 bits** (396 bytes, cumpliendo ampliamente el límite recomendado de 256 palabras).
  - En `sw/game.s` (línea 8), el registro `x2` se carga una sola vez con `lui x2, 0x80000` (`0x80000000`) y todos los `lw`/`sw` del programa usan desplazamientos sobre `x2` (`0(x2)` displays, `4(x2)` LEDs, `8(x2)` botones, `12(x2)` contador de ciclos, `16(x2)` inicio, `20(x2)` `elapsed_q`, `24(x2)` captura de evento). No existe stack (`sp`) ni variables en RAM; todo el estado vive en los registros `x1`..`x15`. Por tanto, el juego usa **0 palabras de RAM de datos**, y reservamos **1 palabra de RAM en `0x18c`** (dentro del límite de 64 palabras) para ejercitar y verificar el camino de lectura/escritura a memoria.
- **Comparación ROM (`rom_100_40`, `Unified=0`) vs. Memoria Unificada FF (`ffq_100_40`, `Unified=1`)**:
  - **Área de síntesis 3.65x menor**:
    - `rom_100_40`: **`163,731.19 um²`** de área de celdas mapeadas, **`5,938` celdas** en síntesis (`22,709` instancias físicas finales en el die incluyendo fillers/taps/buffers) y solo **`914` Flip-Flops** (`95` FFs en `u_ram` + `819` FFs en el resto del SoC).
    - `ffq_100_40`: **`597,386.36 um²`** de área de celdas mapeadas, **`17,490` celdas** en síntesis y **`4,083` Flip-Flops** (`3,264` FFs en `u_ram`: 3,200 bits de almacenamiento para las 100 palabras + 64 bits de respuesta registrada).
  - **Utilización lógica y Fmáx verificada**:
    - `rom_100_40`: **47.79 %** de ocupación lógica final y **15.873 MHz** (`63 ns`) de frecuencia máxima verificada en los 9 corners.
    - `ffq_100_40`: **50.64 %** de ocupación lógica final y **10.000 MHz** (`100 ns`) de frecuencia máxima verificada.
  - **Ruteabilidad y congestión en FF**: En la memoria FF sin padding (`ff_100_40`) hubo conflictos persistentes de ruteo detallado; con padding de 4 sitios (`ffp_100_40`, `GPL_CELL_PADDING = DPL_CELL_PADDING = 4`), la densidad automática de placement subió a `73.15 %` y falló por congestión global. En `ffq_100_40` fijamos además `PL_TARGET_DENSITY_PCT = 60` (distinto de `FP_CORE_UTIL = 40%`), logrando cerrar DRC=0, LVS=0 y Antena=0 en un die de **`1,548,640 um²`** frente a solo **`438,409 um²`** de la versión ROM.

### 3. ¿Cuáles son las 5 celdas más usadas en síntesis y cómo se distribuye el área por módulo? (Actividad 3.3)
- **Top 5 celdas estándar en `rom_100_40`** (`results/physical/rom_100_40/synthesis/area_analysis.json`):
  1. **`dffrnq_1` (`911` instancias)**: Flip-Flops D con reset asíncrono activo bajo; implementan los 15 registros del `register_file` (`480`), registros del periférico (`216`), memoria/lectura (`95`), etapa IF (`66`), SPI (`51`) y control (`3`). *(Además hay `3` celdas `dffsnq_1` con set activo bajo, sumando los `914` FFs totales).*
  2. **`nand2_1` (`902` instancias)**: Compuertas NAND de 2 entradas; dominan en la decodificación combinacional de la ROM y RAM (`u_ram`: `476`), banco de registros (`144`) y periférico (`119`).
  3. **`mux2_2` (`710` instancias)**: Multiplexores 2:1; concentrados masivamente en `u_rf` (`650` de `710`) para los árboles de lectura de los dos puertos del banco de registros y habilitación de escritura.
  4. **`aoi22_1` (`553` instancias)**: Celdas complejas AND-OR-Invert; usadas en la selección de lectura/escritura del `register_file` (`345`), ALU (`67`) y memoria (`57`).
  5. **`nor2_1` (`352` instancias)**: Compuertas NOR de 2 entradas; usadas en decodificación de direcciones y comparaciones en `u_ram` (`121`), periférico (`76`) y ALU (`72`).
- **Desglose jerárquico de área en síntesis (`163,731.19 um²` total)**:
  - **Core completo (`u_soc.u_core`)**: **`105,600.10 um²`** (**64.50 %** del total).
  - **Register File (`u_soc.u_core.u_rf`)**: **`71,587.67 um²`** (**43.72 %** del total) — es el submódulo individual que aporta más área en la arquitectura ROM porque almacena 15x32 bits en FFs con doble puerto de lectura registrado.
  - **Memoria (`u_soc.u_ram`)**: **`25,815.55 um²`** (**15.77 %** del total).
  - **Periférico completo (`u_soc.u_periph`)**: **`23,242.78 um²`** (**14.20 %** del total).
  - **ALU (`u_soc.u_core.u_id.u_alu`)**: **`10,152.80 um²`** (**6.20 %** del total).
  - **Contador de ciclos (`u_soc.u_periph.u_cycle_counter`)**: **`3,942.58 um²`**, lo que representa apenas el **2.41 %** (`2.408 %`) del área total de síntesis (solo 32 FFs y su sumador `+1`, sin dominar el área del chip).

### 4. ¿Cuál es la frecuencia máxima verificada, cómo cerraron los 9 corners y cuál es la ruta crítica? (Actividad 3.4)
- **Cierre en los 9 corners**: Por defecto el PDK `gf180mcuD` en LibreLane solo verificaba setup en `*tt*`. Añadimos `"TIMING_VIOLATION_CORNERS": ["*"]`, `"SETUP_VIOLATION_CORNERS": ["*"]` y `"HOLD_VIOLATION_CORNERS": ["*"]` para exigir `WNS >= 0` y `TNS = 0` en los **9 corners** (`min/nom/max` RC cruzados con `tt_025C_5v00`, `ss_125C_4v50` y `ff_n40C_5v50`).
- **Resultados de `rom_100_40` (10 MHz)**:
  - **Corner típico (`nom_tt_025C_5v00`)**: Setup WS = **`+67.130 ns`** (`WNS = 0`, `TNS = 0`); Hold WS = **`+0.437 ns`** (`WNS = 0`, `TNS = 0`).
  - **Corner lento (`max_ss_125C_4v50`, 125 °C y 4.5 V)**: Setup WS = **`+37.343 ns`** (`37.342553 ns`, el peor setup de los 9 corners, `WNS = 0`, `TNS = 0`); Hold WS = **`+1.060 ns`**.
  - **Peor Hold global (`min_ff_n40C_5v50`, -40 °C y 5.5 V)**: Hold WS = **`+0.171 ns`** (`0.171039 ns`, `WNS = 0`, `TNS = 0`).
- **Barrido de `CLOCK_PERIOD` y Fmáx verificada**:
  - Probamos `100, 80, 63, 62, 60, 40, 30 ns` en ROM.
  - A **`63 ns` (`rom_63_40` = `15.873 MHz`)** el diseño cierra completamente en los 9 corners con Setup WS = **`+0.343 ns`** (`0.342560 ns`) en `max_ss_125C_4v50` y `+30.130 ns` en `nom_tt_025C_5v00`.
  - A **`62 ns` (`rom_62_40` = `16.129 MHz`)** el corner típico pasa holgado (`+29.130 ns`), pero el corner lento `max_ss_125C_4v50` falla con **`WNS = -0.657 ns`** y **`TNS = -4.349 ns`** (y a `60 ns` falla con `WNS = -2.657 ns`, `TNS = -48.638 ns`). Cada período dispara una nueva optimización, buffering y placement en OpenROAD.
- **Ruta crítica exacta en `rom_100_40` (`max_ss_125C_4v50`)**:
  - **Celda de inicio**: `u_soc.u_ram._2300_` (`dffrnq_1`, pin `Q`, señal de instrucción registrada `u_soc.instr_rdata[1]`, etapa **fetch**).
  - **Recorrido microarquitectónico**: Pasa por **decode** (`u_soc.u_core.u_id.u_decoder`), selección de operandos en `u_id` (`operand_a[1]`), **ejecución en la ALU** (`u_soc.u_core.u_id.u_alu`) donde propaga el acarreo hasta formar el bit 31 de la dirección de **acceso a memoria** (`lsu_addr[31]`), atraviesa la decodificación MMIO y control del periférico (`u_soc.u_periph`), y llega a la captura de tiempo.
  - **Celda de fin**: `u_soc.u_periph._1280_` (`dffrnq_1`, pin `D`, correspondiente al registro `elapsed_q[18]`), con slack **`+37.342553 ns`**.
- **Cambio al RTL propuesto y evaluado (`rom_fast_100_40`)**:
  - Implementamos en `rtl/espino_core/espino_alu.v` una suma **Carry-Select por bloques de 8 bits** (`ASIC_FAST_ADD=1`) para acelerar la propagación de acarreo hacia `lsu_addr[31]`.
  - **Resultado**: El área de síntesis bajó levemente de `163,731.19 um²` a **`163,671.92 um²`** (`-0.04 %`, mismo die de `438,256` / `438,409 um²`), pero el peor slack de setup en `max_ss_125C_4v50` pasó de **`37.343 ns` a `35.564 ns`** (`-1.778 ns`). Como la ruta crítica incluye decode, selección de operandos y lógica MMIO, y ABC ya optimiza bien el sumador de 32 bits, duplicar bloques con muxes de selección agregó carga y empeoró el slack global. Por eso conservamos la ALU de referencia.

### 5. ¿Cómo exploraron el Floorplan (`FP_CORE_UTIL`), los pines, la PDN y el costo del chip? (Actividad 3.5)
- **Barrido de utilización (`rom_100_30`, `rom_100_40`, `rom_100_50`, `rom_100_60`)**:
  - `30 %`: Ocupación lógica `35.90 %`, área de die **`579,292 um²`**, `191` violaciones DRC en iteración 0 del ruteo detallado, cierre final **Sí** (DRC final = 0).
  - `40 %` (**elegida por enunciado**): Ocupación lógica `47.79 %`, área de die **`438,409 um²`** (`0.438409 mm²`, bbox `653.225 um x 671.145 um`), `95` violaciones DRC en iteración 0, cierre final **Sí**.
  - `50 %`: Ocupación lógica `59.98 %`, área de die **`353,522 um²`**, `46` violaciones DRC en iteración 0, cierre final **Sí**.
  - `60 %`: Ocupación lógica `71.53 %`, área de die **`296,710 um²`** (**menor área con cierre completo en el barrido**), pero las violaciones DRC iniciales en la iteración 0 del ruteador detallado se disparan a **`3,618`** (ver gráfica `results/plots/utilizacion_congestion.png`), evidenciando el fuerte aumento de congestión inicial aunque el ruteador logre resolverlas en iteraciones posteriores.
- **Ubicación de terminales (`config/pins.cfg`)**:
  - **Sur (`#S`)**: `clk_i` y `rst_ni` (entradas globales de sincronía y reset).
  - **Oeste (`#W`)**: `spi_sclk_i`, `spi_mosi_i`, `spi_cs_ni`, `spi_miso_o` (bus serial agrupado hacia el maestro externo).
  - **Este (`#E`)**: `leds_o[3:0]` y `buttons_i[3:0]` (interfaz de estímulo/respuesta rápida de rondas).
  - **Norte (`#N`)**: `segment1_o[6:0]` y `segment2_o[6:0]` (14 líneas de salida hacia los dos displays de 7 segmentos).
- **Costo estimado y sus limitaciones**:
  - Usando el área de die final (`0.438409 mm²`) y la relación lineal del ejercicio ($\text{US\$ } 23,000/\text{mm}^2$):
    $$\text{Costo ROM} = 0.438409\text{ mm}^2 \times \text{US\$ } 23,000/\text{mm}^2 = \text{US\$ } 10,083.41$$
  - En cambio, la versión de memoria unificada con Flip-Flops (`ffq_100_40`, die de `1,548,640 um²` = `1.548640 mm²`) tendría un costo equivalente de **$\text{US\$ } 35,618.72$** ($3.53\times$ más caro).
  - **Limitaciones**: En fabricación real el costo no escala solo con el área del macro lógico; faltan el anillo de pads de I/O (que a menudo domina en diseños pequeños *pad-limited*), encapsulado, pruebas (testing), costos fijos de máscaras/shuttle MPW y el rendimiento (*yield*, que cae exponencialmente en dies grandes). La decisión con mayor impacto en el área y costo fue elegir **ROM sobre memoria unificada en Flip-Flops**.

### 6. ¿Qué pasó con las verificaciones físicas (DRC, LVS y Efecto Antena)? (Actividad 3.6)
- **Magic DRC**: **`0` violaciones** (`results/physical/rom_100_40/signoff/64-magic-drc/reports/drc.magic.rpt`). *(Nota: el PDK no incluye un runset de KLayout DRC en esta configuración, por lo que el signoff DRC acreditado es Magic, mientras KLayout realiza stream-out, render y XOR=0).*
- **Netgen LVS**: **`0` errores** (*Circuits match uniquely* en `results/physical/rom_100_40/signoff/70-netgen-lvs/reports/lvs.netgen.rpt`).
- **Efecto Antena**: En el chequeo previo a la reparación (`40-openroad-checkantennas/reports/antenna_summary.rpt`) apareció **1 violación de antena** en la red `u_soc.g_spi.u_spi.mosi_sync[0]` conectada al pin de compuerta `u_soc.g_spi.u_spi._275_/D` en la capa **`Metal5`**, con razón parcial de área de **`460.48`** frente al límite de **`400.0`** (`1.15x`). Durante el grabado por plasma en fabricación, ese tramo largo de `Metal5` acumularía carga capaz de dañar el óxido de compuerta del flip-flop sincronizador. OpenROAD insertó automáticamente el diodo de protección **`ANTENNA_1`** (`gf180mcu_fd_sc_mcu7t5v0__antenna`) junto a la celda víctima (`586.32, 497.84 um`), dejando la verificación final (`46-openroad-checkantennas-1`) en **`0` violaciones** (documentado en `results/antenna_incident.json` y `results/layout/antena_corregida.png`).

---

## 7. Nota rápida si modificas algo durante la presentación

Si durante la defensa el profesor te hace editar `config/rom_100_40.json`, `sw/game.s` o descomprimir un reporte y al terminar quieres dejar la carpeta otra vez idéntica al repositorio entregado en GitHub, solo ejecuta:
```powershell
cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
git checkout -- .
```
