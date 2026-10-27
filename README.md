# Llanquihue-AI: Sistema de Vigilancia y Predicción de Calidad de Aguas

![alt text](lagollanquihue.png)

Sistema avanzado de monitoreo ambiental que utiliza imágenes satelitales Sentinel-2 (BOA) para el seguimiento del Índice de Clorofila (NDCI) en el Lago Llanquihue, Chile. El proyecto combina Big Data geoespacial, un motor de procesamiento optimizado en C++ e Inteligencia Artificial para predecir la salud del ecosistema lacustre.

## Fundamentos Científicos: ¿Qué es el NDCI?

El Normalized Difference Chlorophyll Index (NDCI) es un algoritmo espectral diseñado para estimar la concentración de clorofila-a en aguas ópticamente complejas (aguas continentales y costeras).

La FórmulaEl sistema calcula el NDCI utilizando las bandas del sensor Sentinel-2:

$$NDCI = \frac{RedEdge (B5) - Red (B4)}{RedEdge (B5) + Red (B4)}$$

Este índice es superior al NDVI tradicional en entornos acuáticos, ya que la banda RedEdge (705nm) captura con precisión la reflectancia del fitoplancton, eliminando el "ruido" del agua pura.

## Visualización Científica: Cubo Espacio-Temporal

Para el análisis de hotspots geográficos, el proyecto implementa un Space-Time Cube 3D interactivo. Esta herramienta permite:

- Eje Z (Tiempo): Apilamiento vertical de las capas anuales 2019–2025, más la capa de proyección 2026 (superficie plana; ver *Limitaciones conocidas del modelo predictivo*).

- Filtros de IA: Botones interactivos para aislar el histórico o comparar con la predicción roja de 2026.

- Referencia Geográfica: Basemap orientado (Norte-Sur / Este-Oeste) con puntos de control en Puerto Varas, Ensenada y Puerto Octay.

## Arquitectura del Proyecto

El sistema opera en cuatro fases críticas sincronizadas:

1. Extracción Geoespacial (Python & GEE): Captura de datos espectrales Sentinel-2 (bandas nativas de 10–20 m) filtrando interferencias atmosféricas y nubosidad; la grilla se muestrea a 150 m por el límite de 262.144 px de `sampleRectangle`.

2. Motor de Alto Rendimiento (C++ Core): Filtrado espacial mediante kernels 3x3 e interpolación temporal para resolver vacíos de datos (gap-filling).

3. Análisis de Series Temporales (Pandas): Construcción de un dataset histórico (2019-2025) con resolución mensual.

4. Inteligencia Predictiva: Regresión lineal sobre el índice temporal de la serie mensual (sin variables estacionales) que proyecta el estado del lago a 12 meses vista. La estacionalidad se reporta aparte, como promedio histórico de eneros.


## Resultados de la Fase de Procesamiento (2019-2025)

El sistema ha procesado exitosamente 248,868 píxeles por capa temporal. A continuación, se muestra la matriz de intensidad NDCI recuperada, donde se observan los ciclos anuales de estrés hídrico:

![alt text](data/reports/history_2019.png)

![alt text](data/reports/history_2020.png)

![alt text](data/reports/history_2021.png)

![alt text](data/reports/history_2022.png)

![alt text](data/reports/history_2023.png)

![alt text](data/reports/history_2024.png)

![alt text](data/reports/history_2025.png)

![alt text](data/reports/history_2026.png)

> Nota sobre las imágenes: los `history_*.png` los genera `plot_historical_quality` (`src/visualization/time_series.py`), una función **no invocada** por `main.py`; se conservan como material histórico. El pipeline actual produce `prediction_full_2026.png`.

> Nota Teórica: Los valores negativos indican aguas claras (baja clorofila), mientras que valores cercanos o superiores a 0.1 NDCI activan protocolos de alerta por posible proliferación de algas.



## Análisis de la Visualización 3D
El **Cubo Espacio-Temporal** no solo es una pieza estética; es una herramienta de diagnóstico:

**1. Eje Vertical (Z):** Permite detectar la resiliencia del lago. Si cada año las manchas de color (hotspots) son más extensas, el lago está perdiendo su capacidad de autolimpieza.

**2. Variación Geográfica (X, Y):** Ayuda a localizar el origen del estrés. Si los picos de clorofila siempre nacen cerca de Puerto Varas o zonas urbanas, sugiere un impacto antrópico (humano).

**3. Tendencia IA (Capa Roja):** Extrapolación lineal de los 84 meses previos. La capa roja es una superficie plana con el valor medio proyectado: sirve como referencia de nivel, no como predicción espacial.

![alt text](data/reports/newplot.png)

## Interpretación de Niveles y Umbrales

El gráfico y el cubo 3D representan la salud del lago según los siguientes rangos de valor:

**Dinámica de Valores:**

- **¿Qué pasa si el NDCI sube?** Indica una proliferación de algas (eutrofización). Esto suele ocurrir por el aumento de la temperatura del agua en verano o el vertido de nutrientes (fósforo/nitrógeno). Un NDCI alto sostenido puede llevar a la hipoxia (muerte de peces).

- **¿Qué pasa si el NDCI baja?** Significa que el agua está recuperando su transparencia. En invierno, es normal ver valores muy bajos (incluso negativos) debido a la menor radiación solar y menor actividad biológica.




## Proyección IA 2026

Proyección de la corrida verificada del 27-10-2026 (regresión sobre los 84 valores mensuales de 2019–2025):

- **Rango proyectado:** −0.0513 NDCI (Ene-2026) → −0.0458 NDCI (Dic-2026).

- **Diagnóstico:** tendencia estable; los 12 meses quedan bajo el umbral de alerta de 0.1.

- **Forma de la curva:** recta de pendiente constante (+0.0005 NDCI/mes). El modelo no tiene términos estacionales; ver *Limitaciones conocidas del modelo predictivo*.

![alt text](data/reports/prediction_2026.png)

![alt text](data/reports/prediction_full_2026.png)

> Nota: `prediction_2026.png`, `prediction_zoom_2026.png` y `newplot.png` no los genera el código actual (artefactos de una versión anterior); solo `prediction_full_2026.png` sale de `plot_prediction_results`.


## Instalación y Requisitos

> Entorno verificado el **27-10-2026** en Windows 11 + PowerShell 7, con Python 3.12.7 (python.org) y MSYS2 en `D:\msys64`. Todos los comandos se ejecutan **desde la raíz del repositorio**.

### 0. Requisitos previos

| Componente | Versión | Por qué |
|---|---|---|
| Windows + PowerShell | 10/11 | el pipeline abre ventanas nativas: Matplotlib, Plotly (navegador) y PyVista |
| Python | **3.12 desde python.org** | `setup_engine.py` enlaza contra `libs\python312.lib`, que el Python de Microsoft Store no incluye |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.9 | resuelve e instala el entorno (`.venv`) |
| MSYS2 + `mingw-w64-ucrt-x86_64-gcc` | GCC ≥ 11 | compila `engine_core`; `src\main.py:27` fija `D:\msys64\ucrt64\bin` |
| Service Account GEE | `credentials.json` | autenticación no interactiva con `ee.ServiceAccountCredentials` |

`credentials.json` **no se versiona** (está en `.gitignore`). Debe ser la clave JSON de una service account con acceso al proyecto `llanquihue-analysis` (`src/config.py`).

### 1. MSYS2 y el compilador C++ (solo la primera vez)

```powershell
# Instalación limpia en la ruta exacta que el código espera
$dst = "$env:TEMP\msys2-x86_64-latest.exe"
Invoke-WebRequest -Uri "https://github.com/msys2/msys2-installer/releases/latest/download/msys2-x86_64-latest.exe" -OutFile $dst
& $dst in --confirm-command --accept-messages --root D:/msys64
```

Si `mirror.msys2.org` (primer `Server` de la lista) no responde — síntoma: `error: Operation too slow. Less than 1 bytes/sec transferred the last 10 seconds` — se cambia el primary por un Tier 1 que funcione:

```powershell
& D:\msys64\usr\bin\bash.exe -lc "sed -i 's|https://mirror.msys2.org/mingw|https://mirrors.dotsrc.org/msys2/mingw|' /etc/pacman.d/mirrorlist.mingw"
& D:\msys64\usr\bin\bash.exe -lc "sed -i 's|https://mirror.msys2.org/msys|https://mirrors.dotsrc.org/msys2/msys|' /etc/pacman.d/mirrorlist.msys"
```

Luego el toolchain (~470 MB instalados):

```powershell
& D:\msys64\usr\bin\bash.exe -lc "pacman -Syu --noconfirm"
& D:\msys64\usr\bin\bash.exe -lc "pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-gcc"
& D:\msys64\ucrt64\bin\g++.exe --version
# esperado: g++ (Rev..., Built by MSYS2 project) 1x.x.x
```

### 2. Entorno Python

```powershell
uv sync --python "C:\Users\<usuario>\AppData\Local\Programs\Python\Python312\python.exe"
```

Se fija explícitamente el intérprete del sistema porque `setup_engine.py` toma `sys.base_prefix\libs` para enlazar `-lpython312`. Con un CPython administrado por uv esa carpeta puede no existir y el linkeo aborta con `cannot find -lpython312`.

### 3. Compilar el motor C++

```powershell
$env:PATH = "D:\msys64\ucrt64\bin;" + $env:PATH                    # setup_engine.py invoca "g++" sin ruta absoluta
New-Item -ItemType Directory -Force src\engine_cpp\lib | Out-Null  # setup_engine.py NO crea el directorio
uv run setup_engine.py
# esperado: "¡Éxito! engine_core.pyd generado."
```

Verificación (con carga explícita de las DLLs de MinGW):

```powershell
Get-Item src\engine_cpp\lib\engine_core.pyd | Select-Object Name,Length
uv run python -c "import os,sys; os.add_dll_directory(r'D:\msys64\ucrt64\bin'); sys.path.append('src/engine_cpp/lib'); import engine_core as e; print(e.detect_anomalies([0.0,0.2],0.1)); print(e.classify_risk([0.3],[1.0]))"
# esperado: [0.0, 1.0]  y  [3]
```

`engine_core.pyd` depende de `libstdc++-6.dll`, `libgcc_s_seh-1.dll` y `libwinpthread-1.dll`. En Python 3.8+ el cargador **no** busca dependencias en `PATH`: hay que registrar el directorio con `os.add_dll_directory`. Eso es exactamente lo que hace `src/main.py:31`.

### 4. Variables de entorno de la sesión (obligatorio)

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8:replace"
chcp 65001 | Out-Null
```

Sin esto, el `print` del `⚠️` en `historical_processor.py:26` lanza `UnicodeEncodeError: 'charmap' codec can't encode characters` en cuanto un mes no tiene imágenes válidas, y la excepción aborta la corrida completa. La consola de Windows usa cp1252 por defecto y el código imprime emojis. Las variables viven en la sesión: hay que repetirlas en cada ventana nueva.

### 5. Google Earth Engine

```powershell
uv run python -c "import sys; sys.path.insert(0,'src'); from core_ee.connector import initialize_ee; import ee; initialize_ee(); print('OK:', ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2026-01-01','2026-01-15').size().getInfo())"
```

No se usa `earthengine authenticate`: la autenticación es por service account (`credentials.json` + proyecto `llanquihue-analysis`).

---
## Uso del Sistema

```powershell
uv run src/main.py
```

- **Debe ejecutarse desde la raíz del repositorio.** Todas las rutas de salida son relativas al directorio de trabajo (`data/raw_grids`, `data/processed`, `data/reports`); desde otro directorio se crea un `data/` en el lugar equivocado.
- `uv run main.py` **falla**: `main.py` está en `src/`.

Secuencia esperada (20–45 min la primera vez):

| Fase | Qué hace | Salida |
|---|---|---|
| 1 | estado actual (Ene-2026) | `present_state.npy/.csv` + `% de superficie con estrés` |
| 2 | 2019–2025: 12 medias mensuales + 1 mapa anual por año | `grid_2019…2025.npy/.csv` |
| 3 | dataset mensual para el modelo | `data/processed/llanquihue_water_quality_dataset.csv` (12×7) |
| 3.5 | alerta estacional + proyección + PNG + cubo | `data/reports/prediction_full_2026.png`, navegador, ventana Matplotlib |
| 4 | malla 3D del estado actual | ventana PyVista |

Las ventanas de Matplotlib y PyVista **bloquean** el proceso hasta que se cierran.

## Solución de problemas

| Síntoma | Causa | Arreglo |
|---|---|---|
| `'charmap' codec can't encode characters` | consola en cp1252, código con emojis | §4 (`PYTHONUTF8=1`) |
| `DLL load failed while importing engine_core` | faltan las DLLs de MinGW en la búsqueda | `os.add_dll_directory(r"D:\msys64\ucrt64\bin")` |
| `FileNotFoundError: [WinError 2] 'g++'` | MSYS2 no está en `PATH` | `$env:PATH = "D:\msys64\ucrt64\bin;" + $env:PATH` |
| `cannot find -lpython312` al compilar | el `.venv` no usa el Python de python.org | recrear con `uv sync --python <ruta>\Python312\python.exe` |
| `No such file or directory` al compilar | falta el directorio `src\engine_cpp\lib\` | `New-Item -ItemType Directory -Force src\engine_cpp\lib` |
| `NameError: name 'final_grid_3d' is not defined` al final | `engine_core` no cargó (ver `⚠️ Error al cargar C++`) | resolver la carga del `.pyd`; sin motor C++, `main.py:113` falla |
| `pacman`: `Operation too slow. Less than 1 bytes/sec` | `mirror.msys2.org` no responde | §1, cambiar el primary a `mirrors.dotsrc.org` |
| `uv run main.py` → archivo no encontrado | ruta incorrecta | `uv run src/main.py` |

El `try/except` de `main.py:115` imprime `Error en el flujo principal: …` y **termina con código 0**. Un exit code 0 no garantiza que la corrida haya sido exitosa: hay que revisar la última línea.

## Limitaciones conocidas del modelo predictivo

- `predict_next_months` (`src/ai/predictor.py`) ajusta una `LinearRegression` sobre el **índice temporal** de los 84 valores mensuales: sin variables estacionales, sin separación train/test y sin métricas (RMSE/R²). La proyección 2026 es, por construcción, una recta de 12 puntos.
- `get_monthly_series` cierra cada mes en el **día 28** (`f"{year}-{month:02d}-28"`), por lo que pierde los días 29–31.
- `0.0` funciona como centinela de "sin dato" en `sampleRectangle`, en `apply_spatial_filter` y en `interpolate_time_series`: un NDCI real de 0 es indistinguible de una celda vacía.
- La capa de predicción del cubo 3D es una superficie plana con la media proyectada, no una predicción espacial.

## Última corrida verificada (27-10-2026)

- 7 años × 12 meses = 84 llamadas `reduceRegion`; **8 meses sin imágenes válidas** bajo `CLOUDY_PIXEL_PERCENTAGE < 15`: 2019-05, 2019-07, 2020-07, 2020-08, 2022-07, 2023-05, 2024-06 y 2025-05 (quedan en `0.0`).
- Ene-2026: **0.42 %** de la superficie con estrés (NDCI > 0.1).
- Proyección 2026: −0.0513 → −0.0458 NDCI, los 12 meses `ESTABLE` (recta; ver limitaciones).
- Grillas de 372×669 px = 248.868 píxeles por capa temporal.
