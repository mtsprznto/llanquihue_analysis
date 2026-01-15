# src\ai\predictor.py

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression

def predict_next_months(csv_path, months_to_predict=12):
    print(f"\n--- Fase 4: Motor de Predicción Inteligente ({months_to_predict} meses) ---")
    
    df = pd.read_csv(csv_path, index_col=0)
    full_series = []
    for col in df.columns:
        full_series.extend(df[col].values)
    
    X = np.array(range(len(full_series))).reshape(-1, 1)
    y = np.array(full_series)
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.array(range(len(full_series), len(full_series) + months_to_predict)).reshape(-1, 1)
    predictions = model.predict(future_X)
    
    # Lista extendida de meses
    meses_nombres = [
        "Ene", "Feb", "Mar", "Abr", "May", "Jun", 
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ]
    
    print(f"Proyección para el año 2026:")
    for i, pred in enumerate(predictions):
        status = "ESTABLE" if pred < 0.1 else "ALERTA PREVENTIVA"
        # Usamos i % 12 por si predices más de un año
        print(f"-> {meses_nombres[i % 12]} 2026: {pred:.4f} NDCI [{status}]")
        
    return predictions


def get_seasonal_alert(csv_path):
    df = pd.read_csv(csv_path, index_col=0)
    # Promedio de todos los Eneros registrados (2019-2025)
    jan_avg = df.loc['Ene'].mean()
    # El valor más reciente (Enero 2026 que procesamos en el análisis actual)
    # Nota: Tu CSV llega hasta Dic 2025, así que comparamos la tendencia
    print(f"\n Análisis de Estacionalidad:")
    print(f"-> Promedio histórico de Eneros: {jan_avg:.4f}")