# src\core_ee\water_quality.py


def calculate_ndci(image):
    """
    Calcula el Índice de Clorofila (NDCI) para detectar algas.
    Fórmula: (B5 - B4) / (B5 + B4)
    """
    ndci = image.normalizedDifference(['B5', 'B4']).rename('NDCI')
    return image.addBands(ndci)

def calculate_ndwi(image):
    """
    Calcula el Índice de Agua (NDWI) para segmentar el lago.
    Fórmula: (B3 - B8) / (B3 + B8)
    """
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    return image.addBands(ndwi)

def process_water_analytics(image):
    """
    Calcula NDWI y NDCI, usando el primero para enmascarar la tierra.
    """
    # NDWI: (Green - NIR) / (Green + NIR) -> Identifica Agua
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    
    # NDCI: (RedEdge1 - Red) / (RedEdge1 + Red) -> Identifica Clorofila
    ndci = image.normalizedDifference(['B5', 'B4']).rename('NDCI')
    
    # Creamos una máscara: Solo donde NDWI > 0 (es agua)
    water_mask = ndwi.gt(0)
    
    # Retornamos la imagen con las bandas nuevas y la tierra eliminada
    return image.addBands([ndwi, ndci]).updateMask(water_mask)

def add_thermal_layer(image_s2, date_range):
    """
    Opcional: Cruza datos de Sentinel-2 con Landsat 8 para obtener Temperatura 
    Superficial (LST) real sobre el ROI.
    """
    # Por ahora, usemos el NDTI (Turbidez) como proxy profesional adicional
    # NDTI = (Red - Green) / (Red + Green)
    ndti = image_s2.normalizedDifference(['B4', 'B3']).rename('NDTI')
    return image_s2.addBands(ndti)