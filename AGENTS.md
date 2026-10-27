# AGENTS.md — Llanquihue Analysis

Índice operativo del repositorio para agentes. **Fuente de verdad: el código y el grafo MCP, no este archivo.** Si hay contradicción entre este documento y el código, gana el código y se corrige el índice.

- Repo: `mtsprznto/llanquihue_analysis` (GitHub), rama `master`, HEAD verificado `6e4fda0` ("Cambio de README").
- Ruta WSL: `/mnt/d/LLLIT/Code-W11/llanquihue_analysis` — Ruta Windows: `D:\LLLIT\Code-W11\llanquihue_analysis`.
- Stack: Python 3.12 + Google Earth Engine + C++17 (pybind11) + NumPy/Pandas/Scikit-learn + Plotly/PyVista/Matplotlib.
- Tamaño: 19 `.py` + 2 `.cpp` + 1 `.hpp` = **881 líneas**. Datos versionados ≈ 65 MB.
- No hay tests, CI, linter ni type-checker configurados.

---

## 0. MANDATO MCP — obligatorio en TODA búsqueda

**Ninguna búsqueda de código empieza por `grep`, `glob` o lectura a ciegas.** El orden es siempre:

```
1. index_status(project="llanquihue-analysis")
2. search_graph(project="llanquihue-analysis", ...)        # descubrir símbolos
3. trace_path(project="llanquihue-analysis", ...)          # callers/callees
4. get_code_snippet(project="llanquihue-analysis", ...)    # leer implementación
5. query_graph(project="llanquihue-analysis", ...)         # agregaciones multi-hop
6. get_architecture(project="llanquihue-analysis", ...)    # panorama/estructura
7. search_code(project="llanquihue-analysis", ...)         # texto/regex (docs, CSV, configs)
8. SOLO si 1-7 fallan: grep / glob / read
```

Reglas duras:

- `project` es **siempre** el nombre corto `llanquihue-analysis`. Nunca una ruta del filesystem.
- Los `qualified_name` llevan el prefijo `llanquihue-analysis.` (ej. `llanquihue-analysis.src.core_ee.water_quality.process_water_analytics`).
- Si `index_status` devuelve `project not found` → indexar. Si `head_sha` no coincide con `git rev-parse HEAD` → reindexar. Si hay cambios sin commitear sustanciales → reindexar igualmente.
- Registrar en la respuesta qué consulta MCP se usó cuando la conclusión dependa de ella.
- `search_graph` trunca: verificar `has_more` y paginar con `offset`; acotar con `label`, `file_pattern` o `name_pattern` antes de subir `limit`.

### Reindexado

```
index_repository(
  repo_path="/mnt/d/LLLIT/Code-W11/llanquihue_analysis",
  name="llanquihue-analysis",
  mode="fast"        # "full" en la primera indexación o tras cambios estructurales grandes
)
```

Estado actual del índice (2026-10-27, tras indexar `README.md` y este archivo): **179 nodos / 463 aristas**, `status=ready`, `head_sha=6e4fda0`. La base de código sola son 138/423; el delta corresponde a las secciones de `AGENTS.md`. En la primera indexación se omitió `data/raw_grids/grid_2023.csv` (`parse timeout`, 4 MB, es dato no código); `mode="fast"` ya no recorre CSV. Si se necesita su contenido, usar `search_code` con `path_filter` o leer por tramos; no reindexar en loop por esto.

### Recetas verificadas

| Objetivo | Llamada |
|---|---|
| Inventario de funciones con líneas | `query_graph("MATCH (f:Function) RETURN f.qualified_name, f.file_path, f.start_line, f.end_line ORDER BY f.file_path, f.start_line")` |
| Quién llama a una función | `trace_path(function_name="save_grid_data", direction="inbound")` → `run_professional_suite` (hop 1), `src/main.py` (hop 2) |
| Código muerto | `trace_path(function_name="<fn>", direction="inbound")` con `callers=[]` |
| Cadena de datos | `trace_path(function_name="run_professional_suite", direction="outbound", depth=3)` |
| Buscar texto en docs/CSV | `search_code(pattern="NDCI", file_pattern="*.md", mode="compact")` |
| Buscar en este índice | `search_code(pattern="QA60", file_pattern="*.md", path_filter="AGENTS.md")` |
| Hot paths (schema documentado) | `query_graph("MATCH (f:Function) WHERE f.transitive_loop_depth >= 2 RETURN f.qualified_name, f.transitive_loop_depth")` |
| Impacto antes de refactor | `detect_changes(project="llanquihue-analysis", scope="all")` |

Muertas confirmadas por `trace_path` (inbound vacío): `plot_historical_quality`, `get_image_as_numpy`, `calculate_ndci`, `add_thermal_layer`, `get_llanquihue_roi`, `classify_risk` (exportada en pybind11 pero nunca invocada desde Python).

---

## 1. Entorno: WSL (agente) ↔ Windows (usuario)

El repositorio vive en un filesystem compartido. El agente corre en WSL; el usuario ejecuta en Windows/PowerShell.

### Prohibiciones absolutas

- **NUNCA** ejecutar `uv`, `uv run`, `uv sync`, `uv add`, `uv lock`, `uv venv`, `uv pip install`. Un `.venv` creado desde WSL corrompe el `.venv` de Windows (`lib64`, `pyvenv.cfg`), y el siguiente `uv run` en Windows falla con `Acceso denegado (os error 5)`.
- **NUNCA** `pip install`, `python -m venv`, `npm/pnpm install`, ni agregar dependencias sin aprobación explícita.
- **NUNCA** ejecutar el pipeline completo (`main.py`), `auth_test.py` ni nada que llame a Earth Engine: consume cuota, requiere credenciales y abre ventanas interactivas (PyVista/Plotly).
- **NUNCA** leer, imprimir, copiar ni mover `credentials.json` (service account de Google Cloud; está en disco, gitignoreado y nunca fue commiteado).
- **NUNCA** `git add -A`, `git add .`, `git commit`, `git checkout -- .`, `git reset --hard`, `git clean`, ni normalización masiva de finales de línea.

### Protocolo de handoff

Todo comando se entrega al usuario, no se ejecuta:

```
[WINDOWS · PowerShell · CWD D:\LLLIT\Code-W11\llanquihue_analysis]
<comando>

[QUÉ ESPERO] <salida esperada / código de salida>
[SI FALLA] <qué copiar: stdout, stderr, traceback completo>
```

El agente espera el resultado del usuario antes de asumir que el paso funcionó. No se encadenan pasos que dependan de un comando no confirmado.

### Finales de línea (bomba de tiempo)

HEAD usa **LF**; el working tree tiene **CRLF mezclado** (algunos archivos convertidos por herramientas de Windows). `git status` muestra **37 entradas** (2026-10-27) y `git diff` puede reportar millones de líneas por CSV regenerados. No hay `.gitattributes`.

- Preservar los bytes del archivo que se edita (la herramienta de edición conserva CRLF/LF).
- Antes de proponer un commit: `git diff --numstat` y `git diff --ignore-all-space --stat`.
- La decisión de normalizar EOL (crear `.gitattributes`, renormalizar) es del usuario, en un commit dedicado.

---

## 2. Mapa de directorios

```
llanquihue_analysis/
├── setup_engine.py              # compila C++ → src/engine_cpp/lib/engine_core.pyd
├── pyproject.toml               # deps (uv); requires-python >=3.12
├── uv.lock                      # trackeado; regenerado 2026-10-27 (128 paquetes)
├── credentials.json             # SECRETO service account (gitignored)
├── llms.txt                     # prompt/arquitectura original (gitignored, no versionado)
├── src/
│   ├── main.py                  # entry point E2E (5 fases)
│   ├── config.py                # ROI, colecciones GEE, bandas
│   ├── auth_test.py             # smoke test de autenticación GEE
│   ├── ai/predictor.py          # regresión lineal + alerta estacional (sin __init__.py)
│   ├── core_ee/                 # adaptador Earth Engine
│   │   ├── connector.py         # ee.Initialize con service account
│   │   ├── collection.py        # Sentinel-2 SR armonizado + mediana + clip
│   │   ├── masks.py             # QA60 + MSK_CLDPRB
│   │   ├── water_quality.py     # NDWI / NDCI / NDTI
│   │   ├── exporter.py          # GEE → .npy + .csv (150 m)
│   │   ├── exporter_ai.py       # serie mensual → dataset CSV
│   │   └── historical_processor.py  # 12 meses × reduceRegion
│   ├── engine_cpp/              # C++17 + pybind11 (módulo `engine_core`)
│   │   ├── bindings.cpp         # PYBIND11_MODULE + 4 exports
│   │   ├── filters.cpp          # 4 algoritmos (incluido por bindings.cpp)
│   │   ├── filters.hpp          # vacío (solo comentario)
│   │   └── lib/engine_core.pyd  # artefacto compilado (trackeado en git)
│   └── visualization/
│       ├── predictive_plotter.py# Matplotlib: histórico + predicción
│       ├── space_time_cube.py   # Plotly: cubo espacio-temporal
│       ├── viewer_3d.py         # PyVista: malla 3D
│       └── time_series.py       # Matplotlib: serie histórica (MUERTO)
├── data/
│   ├── raw_grids/               # .npy + .csv por año (372×669) + artefactos huérfanos
│   ├── processed/               # dataset mensual para IA (12×7)
│   └── reports/                 # PNG generados + huérfanos
└── build/                       # vacío (resto de build MSYS2)
```

`src/`, `src/core_ee/` y `src/visualization/` tienen `__init__.py` vacío; **`src/ai/` no** (namespace package). Los imports internos son **planos** (`from config import ...`), no relativos, salvo dentro de `core_ee` (`from .collection import ...`).

---

## 3. Índice de símbolos

### Python — activos

| Símbolo | Ubicación | Líneas | Rol | Llamado por |
|---|---|---|---|---|
| `run_professional_suite` | `src/main.py` | 45-116 | Orquestador E2E | `__main__` |
| `initialize_ee` | `src/core_ee/connector.py` | 6-17 | Auth service account | `run_professional_suite` |
| `get_sentinel_data` | `src/core_ee/collection.py` | 5-20 | Colección S2 filtrada → mediana clip | main, `get_monthly_series` |
| `apply_cloud_mask` | `src/core_ee/masks.py` | 9-26 | Máscara QA60 + `MSK_CLDPRB<20` | main, `get_monthly_series` |
| `process_water_analytics` | `src/core_ee/water_quality.py` | 20-34 | NDWI + NDCI, máscara de agua | main, `get_monthly_series` |
| `save_grid_data` | `src/core_ee/exporter.py` | 7-52 | Raster → `.npy` + `.csv` a 150 m | main (2×) |
| `get_monthly_series` | `src/core_ee/historical_processor.py` | 9-48 | 12 medias mensuales NDCI | main |
| `export_to_ai_dataset` | `src/core_ee/exporter_ai.py` | 6-25 | dict años → CSV 12×N | main |
| `predict_next_months` | `src/ai/predictor.py` | 8-37 | `LinearRegression` sobre índice temporal | main |
| `get_seasonal_alert` | `src/ai/predictor.py` | 40-47 | Imprime promedio de eneros | main |
| `plot_prediction_results` | `src/visualization/predictive_plotter.py` | 8-74 | PNG histórico + predicción | main |
| `render_historical_cube_3d` | `src/visualization/space_time_cube.py` | 8-100 | Cubo Plotly con capas y botones | main |
| `render_lake_3d` | `src/visualization/viewer_3d.py` | 6-49 | Malla PyVista interactiva | main |
| `compile_engine` | `setup_engine.py` | 8-47 | Invoca `g++` y genera `.pyd` | `__main__` |

### Python — muertos / no usados (verificado con `trace_path` inbound)

| Símbolo | Ubicación | Nota |
|---|---|---|
| `get_llanquihue_roi` | `src/config.py:23-29` | ROI duplicado y distinto de `LLANQUIHUE_BBOX`; no se usa |
| `calculate_ndci` | `src/core_ee/water_quality.py:4-10` | Reemplazada por `process_water_analytics` |
| `calculate_ndwi` | `src/core_ee/water_quality.py:12-18` | Ídem |
| `add_thermal_layer` | `src/core_ee/water_quality.py:36-44` | Añade NDTI; nunca invocada |
| `get_image_as_numpy` | `src/core_ee/exporter.py:54-65` | Sin `reproject`; candidata a eliminar |
| `plot_historical_quality` | `src/visualization/time_series.py:5-24` | Genera `history_{year}.png`, pero nadie la llama; los PNG del README son huérfanos |
| `classify_risk` | `src/engine_cpp/filters.cpp:52-62` | Exportada en `engine_core`, sin caller Python |

### C++ — módulo `engine_core`

| Export | Líneas | Firma | Uso |
|---|---|---|---|
| `apply_spatial_filter` | `filters.cpp:10-37` | `(vector<double>, rows, cols, window_size)` | main: suaviza grid presente y mapas anuales |
| `detect_anomalies` | `filters.cpp:39-50` | `(vector<double>, threshold)` → 0/1 | main: `threshold=0.1` |
| `classify_risk` | `filters.cpp:52-62` | `(ndci, anomalies)` → 0-3 | Sin uso |
| `interpolate_time_series` | `filters.cpp:65-98` | `(vector<double>)` → serie rellenada | main: gap-filling mensual |
| `PYBIND11_MODULE` | `bindings.cpp:13-25` | — | nombre del módulo: `engine_core` |

`bindings.cpp` incluye `filters.cpp` directamente (`#include "filters.cpp"`), no compila `filters.cpp` por separado. `filters.hpp` está vacío: no agregar declaraciones ahí sin cambiar el esquema de compilación.

---

## 4. Flujo de ejecución (lo que realmente hace)

```
run_professional_suite()                                  src/main.py:45
├─ initialize_ee()                                        connector.py:6
├─ ROI = ee.Geometry.Rectangle(LLANQUIHUE_BBOX)            main.py:48
├─ FASE 1 — presente
│   ├─ get_sentinel_data('2026-01-01','2026-01-16')        collection.py
│   ├─ apply_cloud_mask → process_water_analytics          masks.py → water_quality.py
│   ├─ save_grid_data(..., "present_state")                exporter.py → data/raw_grids/
│   └─ C++ apply_spatial_filter + detect_anomalies         (% de estrés en consola)
├─ FASE 2 — 2019..2025
│   ├─ get_monthly_series(year, roi)  → 12 medias NDCI     historical_processor.py
│   ├─ get_sentinel_data(year) → mask → analytics → save   "grid_{year}"
│   ├─ C++ interpolate_time_series(serie)                  gap-filling
│   └─ C++ apply_spatial_filter(grid)                      suavizado espacial
├─ FASE 3 — export_to_ai_dataset(...)                      exporter_ai.py
├─ FASE 3.5 — predictor + plotter + cubo
│   ├─ get_seasonal_alert(dataset)                         imprime
│   ├─ predict_next_months(dataset, 12)                    LinearRegression
│   ├─ plot_prediction_results(...)                        data/reports/prediction_full_2026.png
│   └─ render_historical_cube_3d(all_grids, predictions)   Plotly (navegador)
└─ FASE 4 — render_lake_3d(final_grid_3d)                  PyVista (ventana)
```

Hechos verificados del flujo:

- Se procesan **7 años** (`range(2019, 2026)`), no 10; 2026 solo se analiza como “presente” y **no se agrega al dataset**.
- El dataset resultante tiene **12 filas × 7 columnas** (`Ene..Dic` × `2019..2025`), primera celda vacía.
- La predicción usa 84 puntos (7×12) y extrapola 12 meses; el modelo **no tiene estacionalidad** pese a lo que afirma el README: es una recta sobre el índice temporal.
- `present_state` se usa solo para el diagnóstico y el render final; no entra al CSV.

---

## 5. Contratos de datos

### Grillas (`data/raw_grids/`)

- Formato: `{nombre}.npy` (`float64`, `shape=(372,669)`) + `{nombre}.csv` (`row,col,ndci_value`).
- Tamaño actual: **248.868 píxeles** por grilla (`372×669`), 1.991.072 B por `.npy`, ~4 MB por `.csv`.
- Proyección/escala de muestreo: `EPSG:4326`, `scale=150` m. El comentario de `exporter.py:13-15` explica el motivo: 100 m excedía el límite de 262.144 px de `sampleRectangle`.
- `defaultValue=0` en `sampleRectangle`: **0 significa “sin dato”**, no “NDCI cero”. Esto condiciona máscaras, filtro C++ e interpolación.
- Grillas activas: `grid_2019..grid_2025`, `present_state`.
- Huérfanas (no las produce el código actual): `debug_llanquihue_shape.*`, `llanquihue_ndci_final.*`, `llanquihue_2026_01_15.*` (esta última es `298×557` = 165.986 px, ROI/escala antigua).

### Dataset IA (`data/processed/llanquihue_water_quality_dataset.csv`)

- `12×7`: índice `Ene..Dic`, columnas `2019..2025`, valores = media NDCI del lago.
- Índice sin nombre (primera celda vacía): `pd.read_csv(path, index_col=0)`.
- Se regenera completo en cada corrida; es un artefacto derivado, no fuente.

### Reportes (`data/reports/`)

| Archivo | Productor |
|---|---|
| `prediction_full_2026.png` | `plot_prediction_results` (código actual) |
| `history_2019..2026.png` | `plot_historical_quality` (código muerto) |
| `prediction_2026.png`, `prediction_zoom_2026.png`, `newplot.png` | Sin productor en el código; solo referenciados en README |

### Umbrales (coherencia entre módulos)

| Umbral NDCI | Significado | Dónde |
|---|---|---|
| `> 0.1` | alerta algal / anomalía | `main.py:64` (llamada), `filters.cpp:44` (comparación), `predictor.py:33`, `predictive_plotter.py:41` |
| `> 0.15` | riesgo alto | `filters.cpp:57` |
| `> 0.25` | riesgo crítico | `filters.cpp:56` |

Cambiar un umbral exige tocar los tres módulos y este documento.

### Parámetros GEE (`src/config.py`)

- `PROJECT_ID = "llanquihue-analysis"`.
- `SENTINEL_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"`, `CLOUD_PROB_COLLECTION = "COPERNICUS/S2_CLOUD_PROBABILITY"`.
- `LLANQUIHUE_BBOX = [-73.20, -41.35, -72.30, -40.85]` (O,S,E,N).
- Bandas declaradas: `B2,B3,B4,B5,B8,B11`; usadas realmente: `B3,B4,B5,B8` (+ `QA60`, `MSK_CLDPRB`).
- Filtros: `CLOUDY_PIXEL_PERCENTAGE < 15`, composición por **mediana**, `clip(roi)`.

---

## 6. Build C++ y ejecución

### Estado actual (importante)

- `src/engine_cpp/lib/engine_core.pyd` **existe** (296 KB, compilado 2026-10-27 con g++ 16.2.0 de MSYS2 UCRT64) y está trackeado en git. `main.py` imprime `Core C++ cargado exitosamente.`; si imprime `⚠️ Error al cargar C++`, queda `engine_core = None` y la corrida revienta en fase 4 (trampa #1).
- `uv.lock` **existe** y fue regenerado el 2026-10-27: 128 paquetes resueltos / 123 instalados (antes 93). Saltos mayores: `pandas 2.3.3 → 3.1.0`, `pyvista 0.46.5 → 0.49.1`, `geemap 0.36.6 → 0.38.9`, `earthengine-api 1.7.4 → 1.7.50`. `pyproject.toml` no cambió, así que el lock de HEAD sigue siendo válido: `git restore uv.lock; uv sync --locked` revierte el salto.
- `.venv` es Windows nativo (CPython 3.12.7 de python.org, `home = C:\Users\litio\AppData\Local\Programs\Python\Python312`, sin `lib64` ni `bin`). Recrearlo desde WSL lo corrompe.
- `setup_engine.py` **no crea** `src/engine_cpp/lib`, así que `g++ -o src/engine_cpp/lib/engine_core.pyd` falla si el directorio no existe.
- `setup_engine.py:33` fija la salida a `.pyd` (Windows) y enlaza `-lpython{major}{minor}` desde `sys.base_prefix/libs`.
- `src/main.py:27` fija `D:\msys64\ucrt64\bin` para `os.add_dll_directory` (DLLs de libstdc++/libgcc). Si MSYS2 está en otra ruta, hay que ajustarla; es la causa típica de `DLL load failed`.

### Comandos (los ejecuta el usuario en Windows)

```powershell
# 0. MSYS2 en el PATH de la sesión (setup_engine.py invoca "g++" sin ruta absoluta)
$env:PATH = "D:\msys64\ucrt64\bin;" + $env:PATH

# 1. Crear el directorio de salida del binario (setup_engine.py NO lo crea)
New-Item -ItemType Directory -Force src\engine_cpp\lib | Out-Null

# 2. Compilar el motor
uv run setup_engine.py

# 3. Verificar artefacto
Get-Item src\engine_cpp\lib\engine_core.pyd | Select-Object Name,Length

# 4. Smoke test del binding (sin GEE) — el .pyd necesita las DLLs de MinGW en la búsqueda
uv run python -c "import os,sys; os.add_dll_directory(r'D:\msys64\ucrt64\bin'); sys.path.append('src/engine_cpp/lib'); import engine_core as e; print(e.detect_anomalies([0.0, 0.2], 0.1)); print(e.classify_risk([0.3],[1.0]))"
```

Salida esperada: `.pyd` de ~296 KB; el paso 4 imprime `[0.0, 1.0]` y `[3]`.

Sin `os.add_dll_directory` el import falla con `DLL load failed while importing engine_core`: desde Python 3.8 en Windows el cargador ya **no** busca dependencias en `PATH`, y este `.pyd` depende de `libstdc++-6.dll`, `libgcc_s_seh-1.dll` y `libwinpthread-1.dll`.

### Ejecución del pipeline

Antes de correr, fijar la codificación de la sesión (obligatorio; ver trampa #16):

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8:replace"
chcp 65001 | Out-Null
```

Invocación correcta **desde la raíz del repo** (los imports planos requieren `src/` en `sys.path`, y todas las rutas de salida son relativas al CWD):

```powershell
uv run src/main.py
```

- `uv run main.py` **falla** (`main.py` no está en la raíz).
- `cd src; uv run main.py` **funciona en imports pero escribe en `src/data/...`** (rutas relativas al CWD). No usarlo.
- `uv run python src/auth_test.py` para validar credenciales/GEE antes de una corrida larga.
- La corrida completa hace ~84 llamadas mensuales a GEE + 7 grillas + render 3D; abre ventanas (Matplotlib y PyVista bloquean hasta cerrarlas). No lanzarla sin pedido explícito. Medición real 2026-10-27: **~14 min** de punta a punta, con 8 meses sin imágenes.

---

## 7. Trampas conocidas (verificadas en código)

1. **`final_grid_3d` puede no existir** — se asigna solo dentro de `if engine_core:` (`main.py:61-67`) y se usa en `main.py:113`. Con el `.pyd` ausente, la corrida termina en `NameError` capturado por el `except` general (`main.py:115-116`) y se reporta como “Error en el flujo principal”. No confundir con un fallo de GEE.
2. **`setup_engine.py` no crea `lib/`** — falla el linkeo con “No such file or directory”.
3. **Dependencia no declarada: `plotly`** — `space_time_cube.py:3` lo importa, pero no está en `pyproject.toml`. Puede resolverse transitivamente vía `geemap`, pero no está garantizado en una instalación limpia: declararlo explícitamente (requiere aprobación + `uv lock` del usuario).
4. **`get_monthly_series` corta en el día 28** — `historical_processor.py:16` (`f"{year}-{month:02d}-28"`): pierde 29-31. No cambia el signo de la serie, pero subestima cobertura.
5. **`QA60` en Sentinel-2 L2A reciente** — `masks.py:15` selecciona `QA60`, banda deprecada/ausente en muchas escenas posteriores a 2024. Si falta, la excepción se silencia en `historical_processor.py:43-45` y el mes queda en `0.0`. **[VERIFICAR]** contra la guía de enmascarado de GEE antes de tocar la lógica. Ref: https://developers.google.com/earth-engine/guides/sentinel_2_cloud_masking
6. **`0.0` como centinela** — `apply_spatial_filter` ignora ceros (`filters.cpp:26`), `interpolate_time_series` trata `0.0` como hueco (`filters.cpp:71`) y `sampleRectangle` rellena con 0. Un NDCI real de 0 es indistinguible de “sin dato”.
7. **Borde del filtro espacial** — el resultado deja el marco de `offset` píxeles en 0 (`filters.cpp:15-35`) y promedia solo vecinos distintos de cero (sesgo en bordes de máscara).
8. **`interpolate_time_series` con `i=0`** — `prev = i` (`filters.cpp:72`), la pendiente se calcula con `x1-x0` correcto pero `y0` es el propio hueco; el tramo inicial queda mal si empieza en 0. Además, los huecos finales se rellenan repitiendo el último válido (holding, no interpolación).
9. **Predicción presentada como “IA”** — `LinearRegression` sobre el índice (`predictor.py:16-23`), sin features estacionales, sin métricas (RMSE/R²), sin split. El README afirma estacionalidad y validación que el código no implementa.
10. **Etiquetas de año fijas** — `predictor.py:31-35` imprime “2026” para los 12 meses sin importar `months_to_predict`; `predictive_plotter.py:25` fija `start_date="2019-01-01"`. Si cambia el rango de años, el eje miente.
11. **Rutas relativas al CWD** — `exporter_ai.py:13`, `predictive_plotter.py:70`, `exporter.py:26`. Ejecutar desde otro directorio crea `data/` en el lugar equivocado.
12. **`plt.show()` bloqueante** — `predictive_plotter.py:74`; `viewer_3d` y Plotly abren ventanas. En corridas headless hay que desactivarlo (no hacerlo sin pedido).
13. **`render_historical_cube_3d` no guarda HTML** — solo `fig.show()` (`space_time_cube.py:100`); la capa de predicción es una superficie plana con la media (`space_time_cube.py:49`), no una predicción espacial.
14. **`get_seasonal_alert` no devuelve nada** — solo imprime (`predictor.py:40-47`); `df.loc['Ene']` lanza `KeyError` si el índice cambia.
15. **Datos versionados y regenerables** — cada corrida reescribe `.npy`/`.csv` (≈4 MB cada uno) y produce diffs gigantes. No commitear datos sin pedido explícito del usuario. Dato empírico: los `.npy` de 2022-2025 salieron byte-idénticos (la mediana de GEE es determinista); solo 2019-2021 cambiaron, por reprocesamiento de la colección en el servidor.
16. **Encoding de consola (cp1252) vs emojis** — `historical_processor.py:26,44`, `main.py:40,109` y `space_time_cube.py:12` imprimen `⚠️`/`🧊`, que no existen en cp1252. Sin `PYTHONUTF8=1` la corrida aborta en el primer mes sin imágenes con `UnicodeEncodeError: 'charmap' codec can't encode characters`, que se reporta como "Error en el flujo principal". Los acentos **sí** existen en cp1252: no son el problema.
17. **`g++` no está en el `PATH`** — `setup_engine.py:28` ejecuta `subprocess.run(["g++", ...])`; el instalador de MSYS2 no modifica el `PATH` del sistema. Sin prefijar `D:\msys64\ucrt64\bin` el fallo es `FileNotFoundError: [WinError 2]`, que **no** captura el `except subprocess.CalledProcessError` (sale como traceback crudo).
18. **`mirror.msys2.org` puede estar caído** — es el primer `Server` de `mirrorlist.mingw` y `mirrorlist.msys`, y es un geo-redirector. Si no responde, `pacman -Syu` aborta con "Operation too slow. Less than 1 bytes/sec" aunque el resto de la lista funcione. Cambiar el primary a un Tier 1 (`mirrors.dotsrc.org` fue el más rápido medido: 873 KB/s frente a 797 de `mirror.umd.edu`).
19. **Meses sin imágenes → `0.0`** — `CLOUDY_PIXEL_PERCENTAGE < 15` sobre una ventana de 28 días puede dejar la colección vacía; `historical_processor.py:25-28` apendea `0.0` y continúa. En la corrida del 2026-10-27 quedaron vacíos 2019-05, 2019-07, 2020-07, 2020-08, 2022-07, 2023-05, 2024-06 y 2025-05. Por la trampa #6, ese `0.0` es indistinguible de un NDCI real de 0.

---

## 8. Convenciones de código

- **Comentarios, docstrings y mensajes en español**; identificadores en inglés (`get_sentinel_data`, `apply_cloud_mask`).
- Cabecera de archivo con ruta estilo Windows: `# src\core_ee\masks.py` / `// src\engine_cpp\filters.cpp`. Mantenerla al crear archivos nuevos.
- Imports internos **planos** desde `src/` (`from config import ...`, `from core_ee.x import y`) y **relativos** dentro de `core_ee` (`from .collection import ...`). No mezclar estilos nuevos sin migrar todo el paquete.
- Sin type hints en el código existente; añadirlos solo en funciones nuevas o al refactorizar una función completa, sin barridos masivos.
- `print()` es el mecanismo de logging del proyecto. No introducir `logging` sin aprobación.
- C++: C++17, `std::vector<double>`, sin dependencias externas salvo pybind11; `-O3 -Wall`. Un solo translation unit (`bindings.cpp` incluye `filters.cpp`).
- No reformatear archivos completos: los diffs deben ser quirúrgicos (el repo ya arrastra churn de EOL).

---

## 9. Reglas de cambio y definición de terminado

Antes de editar:

1. `index_status` + `search_graph`/`get_code_snippet` para el símbolo exacto.
2. Verificar callers con `trace_path` (inbound) y salidas con `search_code` (`np.save`, `to_csv`, `savefig`).
3. Confirmar si el símbolo es activo o muerto (tabla §3). No “arreglar” código muerto sin autorización.

Después de editar:

1. `git diff --numstat` — confirmar que el diff es del tamaño esperado.
2. Reindexar: `index_repository(..., mode="fast")` y verificar que `index_status` quede `ready`.
3. Actualizar este AGENTS.md si cambió el inventario de símbolos, artefactos o contratos de datos.
4. Entregar al usuario el comando de verificación (compile/smoke/run) y esperar su salida.

Definición de terminado para cambios de código:

- [ ] El diff no incluye reformateos ni cambios de EOL ajenos.
- [ ] Imports coherentes con el estilo plano/relativo descrito.
- [ ] Si tocó C++: compila con el comando de §6 y el smoke test devuelve lo esperado.
- [ ] Si tocó umbrales: los tres módulos y §5 están alineados.
- [ ] Si tocó salidas: rutas siguen siendo relativas a la raíz del repo.
- [ ] Índice MCP reindexado y `AGENTS.md` actualizado.

---

## 10. Deuda técnica priorizada (no ejecutar sin pedido)

| Prioridad | Problema | Arreglo propuesto |
|---|---|---|
| P0 | `.pyd` ausente → pipeline no ejecuta C++ y termina en `NameError` | Recompilar (§6) y usar `engine_core is not None` antes de `render_lake_3d`; inicializar `final_grid_3d` con `None` y degradar con mensaje |
| P1 | `plotly` no declarado | Agregar a `pyproject.toml` (requiere aprobación + `uv lock` del usuario) |
| P1 | `setup_engine.py` no crea `lib/` ni maneja rutas MSYS2 | `Path(...).mkdir(parents=True, exist_ok=True)` y ruta de DLL por variable de entorno |
| P2 | Rango mensual truncado al día 28 | Usar inicio del mes siguiente (`relativedelta`/`pd.Timestamp`) |
| P2 | `QA60` posiblemente ausente | Fallback a `MSK_CLASSI_CLOUD`/`MSK_CLDPRB` con verificación de bandas |
| P2 | Código muerto (7 símbolos) | Eliminar en un commit dedicado, tras confirmar con el usuario |
| P3 | Predicción sin validación ni estacionalidad | Split temporal, RMSE/R², baseline estacional; documentar límites |
| P3 | Sin tests | `pytest` para funciones puras (C++ vía binding, `predictor` con CSV fixture) |
| P3 | Sin `.gitattributes` | `* text=auto eol=lf` + renormalización en commit aparte (decisión del usuario) |

---

## 11. Referencias

- Google Earth Engine API: https://developers.google.com/earth-engine/apidocs
- Enmascarado de nubes Sentinel-2: https://developers.google.com/earth-engine/guides/sentinel_2_cloud_masking
- NDCI: Mishra & Mishra (2012), `(B5-B4)/(B5+B4)` para clorofila-a en aguas continentales.
- `llms.txt`: contexto original del proyecto (arquitectura planeada, fases 1-5). Describe un layout (`src/models/`, `include/`, `src/src/`) que **no** coincide con el real; no usarlo como mapa.
