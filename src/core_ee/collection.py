# src\core_ee\collection.py
import ee
from config import SENTINEL_COLLECTION, LLANQUIHUE_BBOX

def get_sentinel_data(date_start: str, date_end: str):
    """
    Obtiene imágenes Sentinel-2 corregidas atmosféricamente (BOA)
    basado en la documentación oficial de ee.ImageCollection.
    Ref: https://developers.google.com/earth-engine/apidocs/ee-imagecollection-filterdate
    """
    roi = ee.Geometry.Rectangle(LLANQUIHUE_BBOX)
    
    # Filtro siguiendo guías de reflectancia de fondo de atmósfera
    collection = (ee.ImageCollection(SENTINEL_COLLECTION)
                  .filterBounds(roi)
                  .filterDate(date_start, date_end)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))) # Filtro de nubes
    
    # Reducción mediana para eliminar artefactos transitorios
    return collection.median().clip(roi)