import ee
import os

# Ruta relativa al archivo de credenciales en la raíz
KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

try:
    # Autenticación siguiendo buenas prácticas de la API
    credentials = ee.ServiceAccountCredentials('', key_file=KEY_PATH)
    ee.Initialize(credentials)
    
    print("--------------------------------------------------")
    print("CONEXIÓN EXITOSA: Google Earth Engine API")
    
    # Prueba de acceso a la colección Sentinel-2 mencionada en el plan 
    s2_collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    count = s2_collection.filterDate('2026-01-01', '2026-01-15').size().getInfo()
    
    print(f"Imágenes disponibles en la zona (Enero 2026): {count}")
    print("--------------------------------------------------")

except Exception as e:
    print(f"ERROR DE CONEXIÓN: {e}")