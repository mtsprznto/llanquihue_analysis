# src\core_ee\exporter_ai.py

import pandas as pd
from pathlib import Path

def export_to_ai_dataset(data_dict):
    """
    Convierte el diccionario de años y series interpoladas en un CSV estructurado.
    """
    print("\n--- Fase 3: Generando Dataset para IA ---")
    
    # Crear carpeta si no existe
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Estructurar datos para Pandas
    df = pd.DataFrame(data_dict)
    df.index = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    # Guardar CSV
    file_path = output_dir / "llanquihue_water_quality_dataset.csv"
    df.to_csv(file_path)
    
    print(f"Dataset exportado exitosamente: {file_path}")
    print(df) # Mostrar tabla resumen en consola