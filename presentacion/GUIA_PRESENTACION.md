# Guía Completa para la Presentación Presencial - Proyecto 3 (Pochoco SoC a ASIC)

**Ruta del proyecto (Windows):** `C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final`  
**Ruta equivalente dentro de Ubuntu (WSL):** `/mnt/c/Users/anton/OneDrive/Escritorio/Lab3AdC/output/proyecto3/proyecto3_final`

---

## 1. Preparación 5 minutos antes de entrar a presentar

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

## 2. Comandos para abrir herramientas "no comunes" (KLayout, OpenROAD GUI, reportes `.gz`)

Ahora que tu ruta (`C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final`) **no tiene espacios**, ningún comando fallará por comillas.

### A. Abrir el layout final (GDSII) en KLayout (Ventana Gráfica)

- **Si estás dentro de la pestaña de `nix-shell` en Ubuntu (Recomendado):**
  ```bash
  klayout -nn /opt/lab3/pdks/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyt -l /opt/lab3/pdks/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyp /mnt/c/Users/anton/OneDrive/Escritorio/Lab3AdC/output/proyecto3/proyecto3_final/results/physical/rom_100_40/final/asic_top.gds
  ```

- **O si prefieres lanzarlo directo desde PowerShell:**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- bash -lc '. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && cd /opt/lab3/librelane-linux && nix-shell --run "klayout -nn /opt/lab3/pdks/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyt -l /opt/lab3/pdks/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyp /mnt/c/Users/anton/OneDrive/Escritorio/Lab3AdC/output/proyecto3/proyecto3_final/results/physical/rom_100_40/final/asic_top.gds"'
  ```

#### Cómo manejar KLayout frente al profesor:
- **Zoom**: Rueda del ratón, o selecciona un área arrastrando con el **clic derecho**.
- **Ajustar todo el chip a la pantalla**: Presiona la tecla **`F`** (*Fit*).
- **Ver el interior de las celdas estándar (transistores y ruteo interno)**: Presiona **`Shift + F`** (o menú superior `Display` → `Full Hierarchy`). Si solo se ven cajas vacías, `Shift + F` muestra todo el contenido.
- **Prender/apagar capas de metal**: En el panel derecho (*Layers*), haz **doble clic** sobre cualquier capa para ocultarla o mostrarla (o clic derecho → *Hide All* y luego doble clic en la que quieras enseñar):
  - **`Metal1` (`34/0`)**: Rieles horizontales de alimentación (`VDD`/`VSS`) de las celdas estándar (`0.6 um`) y ruteo local.
  - **`Metal2` (`36/0`) y `Metal3` (`42/0`)**: Ruteo de señales intermedias y pines de entrada/salida en los bordes del die.
  - **`Metal4` (`46/0`, vertical) y `Metal5` (`81/0`, horizontal)**: *Straps* gruesos (`1.6 um`) de la red de distribución de potencia (PDN).

---

### B. Abrir OpenROAD GUI (para ver Placement, árbol de reloj CTS o congestión)

- **Desde tu pestaña de `nix-shell` en Ubuntu:**
  ```bash
  openroad -gui
  ```
- **Desde PowerShell:**
  ```powershell
  wsl -d Ubuntu -u root -- bash -lc '. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && cd /opt/lab3/librelane-linux && nix-shell --run "openroad -gui"'
  ```
- **Nota útil**: Las corridas completas originales (con todas las bases de datos `.odb` de cada etapa intermedia) están guardadas dentro de Ubuntu en `/opt/lab3/design/config/runs/`. Puedes listarlas dentro de Ubuntu con:
  ```bash
  ls -la /opt/lab3/design/config/runs/
  ```

---

### C. Abrir reportes de Timing comprimidos (`.rpt.gz`)

En `results/physical/rom_100_40/reports/` los reportes extensos de STA están comprimidos en `.rpt.gz`. Si el profesor pide abrir uno en vivo (por ejemplo, el camino crítico de setup en el corner nominal `nom_tt_025C_5v00` o en el corner lento `max_ss_125C_4v50`):

- **Ver las primeras 80 líneas directo en la terminal (PowerShell):**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- zcat results/physical/rom_100_40/reports/sta-rcx_nom/nom_tt_025C_5v00/max.rpt.gz | Select-Object -First 80
  ```
- **O descomprimirlo conservando el `.gz` (`-dk`) y abrirlo en VS Code:**
  ```powershell
  cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
  wsl -d Ubuntu -u root -- gzip -dk results/physical/rom_100_40/reports/sta-rcx_nom/nom_tt_025C_5v00/max.rpt.gz
  code results/physical/rom_100_40/reports/sta-rcx_nom/nom_tt_025C_5v00/max.rpt
  ```

---

## 3. ¿Qué nos van a pedir hacer o cambiar en vivo?

Según la sección 5 del enunciado (`Proyecto_3_arquitectura.pdf`):
> *"Durante la sesión de presentación se les pedirá mostrar los layouts generados y los reportes de las distintas etapas, junto con responder preguntas sobre las decisiones de diseño tomadas y los resultados obtenidos. También se les podrá pedir modificar parámetros de la configuración y ejecutar partes o la totalidad del flujo en vivo."*

Aquí tienes los **4 ejercicios en vivo** que te pueden pedir y cómo resolverlos al instante:

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
   *(El script `tools/run_wsl.sh` copia automáticamente tus carpetas `rtl`, `sw`, `tools`, `tests`, `config` desde Windows hacia `/opt/lab3/design` en Linux y lanza LibreLane dentro de `nix-shell`. La arquitectura ROM tarda solo ~3 a 4 minutos en completar las 63 etapas).*

---

### Ejercicio en vivo 2: "Cambien entre la estrategia de memoria ROM y la estrategia de Memoria Unificada con Flip-Flops"
1. Muestra en `config/rom_100_40.json` la línea 25:
   ```json
   "SYNTH_PARAMETERS": [
     "Unified=0"
   ],
   ```
   - Con `Unified=0` (`config/rom_100_40.json`), el módulo `rtl/generated/asic_memory.v` sintetiza las 99 palabras del programa como una **ROM combinacional** con salida registrada más **1 palabra de RAM** en `0x18c`.
   - Con `Unified=1` (`config/ffq_100_40.json`), sintetiza las **100 palabras completas de 32 bits como bancos de Flip-Flops** inicializados por reset (`rst_ni`) y escribibles por byte.
2. Si te piden lanzar la corrida de Flip-Flops en vivo:
   ```powershell
   wsl -d Ubuntu -u root -- bash tools/run_wsl.sh 'librelane --pdk gf180mcuD --run-tag demo_ff config/ffq_100_40.json'
   ```

---

### Ejercicio en vivo 3: "Cambien una constante o instrucción en el programa RISC-V (`sw/game.s`) y regeneren la memoria"
Si te preguntan cómo se traduce el programa assembler a hardware sin usar `$readmemh`:
1. Abre `sw/game.s` y muestra las constantes del juego (líneas iniciales: `WAIT`, `TENTH`, `HOLD`, `RELEASE`).
2. Ejecuta desde PowerShell el ensamblador y generador de hardware:
   ```powershell
   cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
   python tools/assembler.py sw/game.s sw/game.hex --asic-output rtl/generated
   ```
3. Abre `rtl/generated/asic_memory.v` para mostrar cómo se regeneró la tabla `case` de la ROM y los valores de reset de los Flip-Flops con el nuevo código máquina.
4. Puedes correr además los tests unitarios del ensamblador y del diseño:
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
Esto sintetiza el SoC con Yosys hacia celdas GF180, compila con `iverilog` junto a los modelos funcionales de `primitives.v` y `gf180mcu_fd_sc_mcu7t5v0.v`, y simula los **89,186 ciclos** completos del juego (error de botón, 10 rondas válidas, cálculo del promedio y reinicio), verificando equivalencia exacta con el RTL y comprobando que el primer tiempo de reacción capturado en `elapsed_q` es **1,503 ciclos** en ambos.

---

## 4. Mapa rápido de archivos para mostrar cuando te pidan evidencia

Cuando el profesor te pida ver un resultado específico, abre directamente estos archivos en VS Code:

| Qué te pide el profesor | Archivo exacto a abrir en `proyecto3_final` |
|---|---|
| **Métricas finales del chip ganador (`rom_100_40`)** | `results/physical/rom_100_40/metrics.json` |
| **Resumen comparativo de las 16 corridas (ROM vs FF, frecuencias, áreas)** | `results/physical/summary.json` |
| **Cantidad de celdas y área de síntesis (Yosys)** | `results/physical/rom_100_40/synthesis/stat.rpt` y `stat.json` |
| **Área desglosada por submódulo (`u_rf`, `u_alu`, `u_cycle_counter`, memoria)** | `results/synthesis_breakdown.json` |
| **Reporte Magic DRC (`0` violaciones)** | `results/physical/rom_100_40/reports/magic_drc.rpt` |
| **Reporte Netgen LVS (`Circuits match uniquely`, `0` errores)** | `results/physical/rom_100_40/reports/netgen_lvs.rpt` |
| **Evidencia de la violación de antena en `mosi_sync[0]` y su reparación** | `results/antenna_incident.json` y `results/layout/antenna_fix.png` |
| **Capturas del layout con bloques resaltados (RF, ALU, Contador, PDN)** | Carpeta `results/layout/` (`highlight_register_file.png`, `highlight_alu.png`, `highlight_cycle_counter.png`, `pdn_detail.png`) |
| **Verificación post-síntesis GF180 (ROM y FF)** | `results/mapped_verification.json` y `results/mapped_verification_ff.json` |
| **Comparación de arquitectura de ALU (Ripple-Carry vs Carry-Select)** | `results/alu_comparison.json` |

---

## 5. Preguntas y Respuestas Clave que debes dominar para la defensa

### 1. ¿Qué cambios de diseño hicieron para pasar del Proyecto 2 (FPGA) al Proyecto 3 (ASIC)?
- **Eliminación de divisor de reloj / PLL**: En FPGA entraba un reloj de 50 MHz y se dividía a 10 MHz. En ASIC (`rtl/asic_top.v`) entra directamente el reloj `clk_i` a **10 MHz (`100 ns`)**, lo que simplifica la síntesis del árbol de reloj (CTS) a un único dominio síncrono.
- **Reset explícito en todos los registros**: En FPGA los registros pueden iniciar con `initial`. En un ASIC los Flip-Flops encienden en estado indeterminado (`X`), por lo que todos los elementos secuenciales usan reset activo bajo (`rst_ni`).
- **Reemplazo de `$readmemh` por memoria sintetizable en celdas estándar**: Como no se usa OpenRAM ni bloques BRAM de FPGA, diseñamos un generador en `tools/assembler.py` que produce `rtl/generated/asic_memory.v` con dos modos seleccionables por parámetro `Unified`:
  - **`Unified=0` (ROM + RAM mínima)**: Las 99 instrucciones (396 bytes) se implementan como lógica combinacional constante con registro de salida, y 1 palabra de RAM en `0x18c`. Todas las variables del juego viven en registros de la CPU y las E/S se hacen por MMIO en `0x80000000`.
  - **`Unified=1` (Memoria Unificada FF)**: Las 100 palabras de 32 bits se sintetizan en Flip-Flops con escritura por byte y se cargan con las instrucciones del programa durante el pulso de reset (`rst_ni == 0`).

### 2. ¿Por qué eligieron la estrategia ROM (`rom_100_40`) sobre la de Flip-Flops (`ffq_100_40`)?
- **Área de síntesis 3.65x menor**:
  - `rom_100_40`: **`163,731.19 um²`** de área de celdas, **`13,205` celdas** en total y solo **`914` Flip-Flops**.
  - `ffq_100_40`: **`597,386.36 um²`** de área de celdas y **`4,083` Flip-Flops** (3,200 FFs adicionales solo para almacenar las 100 palabras de 32 bits, más una enorme red de multiplexores 100:1 de lectura y decodificadores de escritura).
- **Ruteabilidad y congestión**: En la memoria FF, el alto *fan-out* y *fan-in* de los 3,200 Flip-Flops hacía colapsar el ruteo global cuando OpenROAD usaba su densidad automática de placement (`73.15%`). Para que la versión FF lograra cerrar DRC/LVS hubo que agregar *cell padding* de 4 sitios (`GPL_CELL_PADDING = DPL_CELL_PADDING = 4`) y fijar `PL_TARGET_DENSITY_PCT = 60` (`ffq_100_40`), resultando en un die de **`1,605,636 um²`** frente a solo **`438,409 um²`** de la versión ROM.

### 3. ¿Cuánto mide el chip final y cuál es su costo estimado?
- **Corrida final**: `rom_100_40` (`CLOCK_PERIOD = 100 ns` = 10 MHz, `FP_CORE_UTIL = 40%`).
- **Área de celdas estándar (síntesis)**: `163,731.19 um²`.
- **Área total del die**: **`438,409 um²`** (`0.438409 mm²`, ~`662.12 um x 662.12 um`).
- **Costo estimado**: Usando la relación del enunciado ($\text{Área en mm}^2 \times \text{US\$ } 23,000/\text{mm}^2$), el costo equivalente de silicio es **$\text{US\$ } 10,083.41$** (mientras que el die de la versión FF costaría **$\text{US\$ } 36,929.63$**).

### 4. ¿Cuál es la frecuencia máxima verificada y cómo aseguraron el cierre de Timing en los 9 corners?
- Por defecto, la configuración base del PDK `gf180mcuD` en LibreLane solo revisaba violaciones de setup en los corners típicos (`*tt*`). Nosotros agregamos explícitamente en los JSON:
  ```json
  "TIMING_VIOLATION_CORNERS": ["*"],
  "SETUP_VIOLATION_CORNERS": ["*"],
  "HOLD_VIOLATION_CORNERS": ["*"]
  ```
  para exigir cierre simultáneo en los **9 corners** (`min/nom/max` de extracción RC parasítica cruzados con `tt_025C_5v00`, `ss_125C_4v50` y `ff_n40C_5v50`).
- En la corrida final `rom_100_40` (10 MHz):
  - **WNS = 0.0 ns** y **TNS = 0.0 ns** en setup y hold en los 9 corners.
  - **Peor slack de setup**: **`+37.342553 ns`** (ocurre en el corner más lento `max_ss_125C_4v50`, a 125 °C y 4.5 V).
  - **Peor slack de hold**: **`+0.171039 ns`** (ocurre en los corners rápidos `ff_n40C_5v50`, a -40 °C y 5.5 V).
- **Frecuencia máxima verificada en el barrido**: Probamos períodos decrecientes (`100, 80, 75, 70, 68, 66, 65, 63, 60 ns`). La menor corrida con flujo completo, DRC=0, LVS=0, Antena=0 y WNS=0 en **todos los 9 corners** es **`rom_63_40` (`63 ns` = `15.873 MHz`)**, con slack mínimo de setup de `+0.0445 ns` en `max_ss_125C_4v50`. A `60 ns` (`16.67 MHz`), el corner típico pasaba (`+12.70 ns`), pero el corner lento `ss_125C_4v50` fallaba con `-1.454 ns`, demostrando por qué no basta mirar solo el corner nominal ni extrapolar con $1/(T - \text{slack})$.

### 5. ¿Cuál es el camino crítico (Critical Path) del procesador?
- Parte del registro de instrucción / estado de la etapa IF (`u_soc.u_core.u_if.instr_rdata_q`) y lectura de operandos en el banco de registros (`u_rf`), atraviesa la decodificación y la cadena aritmética/comparación de la **ALU (`u_alu`)** para resolver saltos condicionales (`branch_taken_w`), actualiza la lógica de próximo PC (`pc_next`) y llega al registro de dirección/PC en la etapa de búsqueda.

### 6. ¿Qué pasó con las verificaciones físicas (DRC, LVS y Efecto Antena)?
- **Magic DRC**: **`0` violaciones** geométricas.
- **Netgen LVS**: **`0` errores** (*Circuits match uniquely* entre el layout extraído y el netlist Verilog).
- **Efecto Antena**: En el chequeo inicial de ruteo apareció **1 violación de antena** en la red de entrada `mosi_sync[0]` (ratio de área de metal a poli de **`460.48`** frente al máximo permitido de **`400`** por el PDK), causada por el trazo largo desde el pin `spi_mosi_i` hasta la compuerta del primer flip-flop sincronizador. El flujo reparó la red insertando automáticamente un diodo de protección `gf180mcu_fd_sc_mcu7t5v0__antenna` (`ANTENNA_1`) junto al flip-flop receptor, dejando el chequeo final en **`0` violaciones**.

### 7. ¿Cómo identificaron dónde quedaron el Register File, la ALU y el Contador de Ciclos en el layout?
- Configuramos `"SYNTH_HIERARCHY_MODE": "deferred_flatten"` en LibreLane. Así Yosys conserva los prefijos jerárquicos de cada instancia (`u_soc.u_core.u_rf.*`, `u_soc.u_core.u_id.u_alu.*`, `u_soc.u_periph.u_cycle_counter.*`) en el netlist y en la base de datos física OpenDB (`.odb`).
- Con `tools/analyze_synthesis.py` y `tools/render_layout.py` extrajimos las coordenadas exactas de cada instancia desde OpenDB (`results/layout/layout_cells.json`) y las superpusimos sobre el GDSII real en KLayout:
  - **Banco de registros (`u_rf`)**: `66,356.04 um²` (40.53% del área de celdas, el bloque más grande del núcleo).
  - **ALU (`u_alu`)**: `9,426.33 um²` (5.76% del área de celdas). Probamos también una variante Carry-Select (`results/alu_comparison.json`), pero como a 100 ns empeoraba levemente el slack global (`35.94 ns` vs `37.34 ns`), mantuvimos la ALU de referencia.
  - **Contador de ciclos (`u_cycle_counter`)**: `3,489.69 um²` (2.13% del área de celdas).

---

## 6. Nota rápida si modificas algo durante la presentación

Si durante la defensa el profesor te hace editar `config/rom_100_40.json` o descomprimir un reporte y al terminar quieres dejar la carpeta otra vez idéntica al repositorio entregado en GitHub, solo ejecuta:
```powershell
cd C:\Users\anton\OneDrive\Escritorio\Lab3AdC\output\proyecto3\proyecto3_final
git checkout -- .
```
