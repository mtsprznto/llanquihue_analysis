# src\core_ee\connector.py
import ee
import os
from config import PROJECT_ID

def initialize_ee():
    """
    Inicializa la API de Earth Engine usando la Service Account.
    """
    key_path = os.path.join(os.path.dirname(__file__), '../../credentials.json')
    
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en {key_path}")
        
    credentials = ee.ServiceAccountCredentials('', key_file=key_path)
    ee.Initialize(credentials, project=PROJECT_ID)
    print(f"Sesión GEE iniciada para el proyecto: {PROJECT_ID}")