# src\core_ee\exporter.py
import os
import ee
import numpy as np
import pandas as pd

def save_grid_data(image, band_name, roi, filename):
    """
    Exporta datos de banda a NumPy y CSV.
    Optimizado para cumplir con el límite de 262,144 píxeles de GEE.
    """
    try:
        # 1. Ajuste de escala a 150m para entrar en el límite de memoria de la API
        # 100m sobre el Llanquihue excedía los 262k píxeles. 150m es el "sweet spot".
        img_resampled = image.select(band_name).reproject(crs='EPSG:4326', scale=150)
        
        # Muestreo de la región
        data = img_resampled.sampleRectangle(region=roi, defaultValue=0)
        grid = np.array(data.get(band_name).getInfo())
        
        # 2. Validación de dimensiones
        if grid.size == 0:
            raise ValueError("La malla resultante está vacía.")

        # 3. Gestión de rutas
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/raw_grids'))
        os.makedirs(base_path, exist_ok=True)
        
        # 4. Exportación Binaria (Velocidad para C++ y PyVista)
        npy_path = os.path.join(base_path, f"{filename}.npy")
        np.save(npy_path, grid)
        
        # 5. Exportación Tabular (Portabilidad para ML)
        csv_path = os.path.join(base_path, f"{filename}.csv")
        # Optimizamos la creación del CSV para mallas grandes
        rows, cols = grid.shape
        r, c = np.indices((rows, cols))
        df = pd.DataFrame({
            'row': r.ravel(),
            'col': c.ravel(),
            'ndci_value': grid.ravel()
        })
        df.to_csv(csv_path, index=False)
        
        print(f"-> Archivos guardados en: {base_path}")
        print(f"-> Dimensiones finales: {grid.shape} ({grid.size} píxeles)")
        
        return grid

    except Exception as e:
        print(f"Error crítico en exportación: {e}")
        return np.array([[]])

def get_image_as_numpy(image, band_name, roi):
    """
    Convierte una banda de GEE a un arreglo de NumPy.
    Ajustamos para obtener una malla densa para PyVista.
    """
    # Obtenemos la URL de descarga para un array (getRegion es más robusto para mallas)
    # Reducimos a una escala de 500m para no saturar la memoria en el primer test 3D
    data = image.select(band_name).sampleRectangle(region=roi, defaultValue=0)
    
    # Extraer y convertir a array de numpy
    grid = np.array(data.get(band_name).getInfo())
    return grid