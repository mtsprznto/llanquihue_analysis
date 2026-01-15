# src\core_ee\historical_processor.py

import ee
from datetime import datetime
from .collection import get_sentinel_data
from .masks import apply_cloud_mask
from .water_quality import process_water_analytics

def get_monthly_series(year, roi):
    """Obtiene el promedio de calidad de agua por mes para un año dado."""
    monthly_data = []
    
    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        # Manejo simple de fin de mes
        end_date = f"{year}-{month:02d}-28" 
        
        print(f"Procesando {start_date}...")
        
        img = get_sentinel_data(start_date, end_date)
        # --- NUEVA VALIDACIÓN DE BANDAS ---
        # Verificamos si la imagen tiene bandas antes de procesar
        band_names = img.bandNames().getInfo()
        
        if not band_names:
            print(f"⚠️ Sin imágenes disponibles para {start_date}. Saltando...")
            monthly_data.append(0.0) 
            continue
        try:
            clean_img = apply_cloud_mask(img)
            analyzed = process_water_analytics(clean_img)
            
            # Reducimos la imagen a un valor medio para todo el lago
            mean_value = analyzed.select('NDCI').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=300
            ).get('NDCI')

            res = mean_value.getInfo()
            monthly_data.append(res if res is not None else 0.0)

        except Exception as e:
            print(f"⚠️ Error procesando mes {month}: {e}")
            monthly_data.append(0.0)
       
        
    return monthly_data