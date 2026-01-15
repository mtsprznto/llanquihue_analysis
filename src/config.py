# src\config.py
import ee

# 1. Definición del Proyecto y Región (ROI)
PROJECT_ID = "llanquihue-analysis"
# Coordenadas exactas del Lago Llanquihue (BBox)
LLANQUIHUE_BBOX = [
    -73.20, # Longitud Oeste (Cerca de Frutillar/Llanquihue)
    -41.35, # Latitud Sur (Bajo Puerto Varas)
    -72.30, # Longitud Este (Pasado Ensenada)
    -40.85  # Latitud Norte (Sobre Puerto Octay)
]
# 2. Identificadores de Colecciones Oficiales
SENTINEL_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED" # Reflectancia BOA
CLOUD_PROB_COLLECTION = "COPERNICUS/S2_CLOUD_PROBABILITY" # Para máscaras pro

# 3. Parámetros de Calidad de Agua (Bandas Sentinel-2)
# B4: Red, B5: Red Edge 1 (Vital para Clorofila/NDCI)
WATER_QUALITY_BANDS = ['B2', 'B3', 'B4', 'B5', 'B8', 'B11']



def get_llanquihue_roi():
    """
    Define el polígono del Lago Llanquihue utilizando ee.Geometry.Rectangle
    Referencia: https://developers.google.com/earth-engine/apidocs/ee-geometry-rectangle
    """
    # Coordenadas aproximadas [Oeste, Sur, Este, Norte]
    return ee.Geometry.Rectangle([-73.15, -41.20, -72.40, -40.80])














