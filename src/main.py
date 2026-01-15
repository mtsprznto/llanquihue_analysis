# src\main.py
import os
import ee
import sys
import numpy as np
from pathlib import Path

from config import LLANQUIHUE_BBOX

from core_ee.collection import get_sentinel_data
from core_ee.connector import initialize_ee
from core_ee.exporter import save_grid_data
from core_ee.exporter_ai import export_to_ai_dataset
from core_ee.historical_processor import get_monthly_series
from core_ee.masks import apply_cloud_mask
from core_ee.water_quality import process_water_analytics

from ai.predictor import get_seasonal_alert, predict_next_months

from visualization.space_time_cube import render_historical_cube_3d
from visualization.predictive_plotter import plot_prediction_results
from visualization.viewer_3d import render_lake_3d

# 1. Configurar rutas
lib_folder = Path(__file__).parent / "engine_cpp" / "lib"
# RUTA CRÍTICA: Cambia esto a tu ruta real de binarios de g++ (donde está g++.exe)
compiler_bin_path = r"D:\msys64\ucrt64\bin" 

# 2. Agregar la ruta al PATH de Windows para que cargue las DLLs dependientes
if os.name == 'nt':
    os.add_dll_directory(compiler_bin_path)

# 3. Agregar la carpeta de la lib al path de búsqueda de Python
sys.path.append(str(lib_folder))

try:
    import engine_core # type: ignore
    print("Core C++ cargado exitosamente.")
except ImportError as e:
    print(f"⚠️ Error al cargar C++: {e}")
    engine_core = None



def run_professional_suite():
    try:
        initialize_ee()
        roi = ee.Geometry.Rectangle(LLANQUIHUE_BBOX)
        years_to_analyze = list(range(2019, 2026)) # Expandible a más años
        all_historical_data = {}
        all_grids = {}               # <--- NUEVO: Para guardar los mapas 2D de cada año


        # --- 1. PROCESAMIENTO INMEDIATO (PRESENTE) ---
        print("\n--- Fase 1: Análisis de Estado Actual ---")
        img_present = get_sentinel_data('2026-01-01', '2026-01-16')
        analyzed_present = process_water_analytics(apply_cloud_mask(img_present))
        grid = save_grid_data(analyzed_present, 'NDCI', roi, "present_state")
        
        # Ejecutamos C++ para el presente de inmediato
        if engine_core:
            rows, cols = grid.shape
            refined = engine_core.apply_spatial_filter(grid.flatten().tolist(), rows, cols, 3)
            hotspots = engine_core.detect_anomalies(refined, 0.1)
            
            # Guardamos el resultado para el render final
            final_grid_3d = np.array(refined).reshape(rows, cols)
            
            # Diagnóstico rápido en consola
            stress_percentage = (sum(hotspots) / grid.size) * 100
            print(f"Diagnóstico: {stress_percentage:.2f}% de superficie con estrés.")
            print(f"Diagnóstico Ene-2026: {(sum(hotspots)/grid.size)*100:.2f}% estrés.")
        
        # --- FASE 2: RECONSTRUCCIÓN MULTIANUAL ---
        print("\n--- Fase 2: Procesamiento de Series Temporales ---")
        for year in years_to_analyze:
            print(f"\n>> Analizando año {year}...")
            raw_series = get_monthly_series(year, roi)
            
            # B. Obtener MAPA ANUAL (para el detalle del Cubo 3D)
            # Esto extrae la imagen promedio de todo el año para ver los hotspots
            img_year = get_sentinel_data(f'{year}-01-01', f'{year}-12-31')
            analyzed_year = process_water_analytics(apply_cloud_mask(img_year))
            grid_year = save_grid_data(analyzed_year, 'NDCI', roi, f"grid_{year}")
            
            if engine_core:
                # Limpieza C++ para la serie
                all_historical_data[year] = engine_core.interpolate_time_series(raw_series)
                
                # Limpieza C++ para el MAPA (Filtro espacial)
                r, c = grid_year.shape
                refined_map = engine_core.apply_spatial_filter(grid_year.flatten().tolist(), r, c, 3)
                all_grids[year] = np.array(refined_map).reshape(r, c) # <--- Guardamos el mapa real


        # --- FASE 3: PREPARACIÓN DE DATASET PARA IA ---
        export_to_ai_dataset(all_historical_data)

        # --- FASE 3.5: INTELIGENCIA PREDICTIVA (NUEVO) ---
        dataset_path = Path("data/processed/llanquihue_water_quality_dataset.csv")
        if dataset_path.exists():
            get_seasonal_alert(str(dataset_path))
            # Obtenemos las predicciones
            predictions = predict_next_months(str(dataset_path), months_to_predict=12)
            # Graficar la predicción
            plot_prediction_results(str(dataset_path), predictions)
            render_historical_cube_3d(all_grids, predictions)
        else:
            print("⚠️ No se encontró el dataset para realizar predicciones.")


        # --- FASE 4: EXPLORACIÓN 3D ---
        render_lake_3d(final_grid_3d, title="Llanquihue: Análisis Final e Inteligencia Predictiva")
   
    except Exception as e:
        print(f"Error en el flujo principal: {e}")

if __name__ == "__main__":
    run_professional_suite()