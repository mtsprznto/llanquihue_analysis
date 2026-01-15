# src\visualization\space_time_cube.py

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from pathlib import Path

def render_historical_cube_3d(all_grids, predictions=None):
    """
    Crea un cubo interactivo con mapa base y filtros para la capa de IA.
    """
    print("\n--- 🧊 Generando Cubo Interactivo con Filtros de IA ---")
    
    fig = go.Figure()
    years = sorted(all_grids.keys())
    num_historical = len(years)
    
    # 1. CAPA BASE: REFERENCIA GEOGRÁFICA (Z = -1)
    first_year = years[0]
    rows, cols = all_grids[first_year].shape
    
    fig.add_trace(go.Surface(
        z=np.full((rows, cols), -1),
        surfacecolor=np.zeros((rows, cols)),
        colorscale=[[0, 'rgb(220,220,220)'], [1, 'rgb(220,220,220)']],
        showscale=False,
        name="Referencia Mapa",
        opacity=0.4,
        hoverinfo='skip'
    ))

    # 2. CAPAS HISTÓRICAS (Índices de traza: 1 a N)
    for i, year in enumerate(years):
        grid_data = all_grids[year]
        fig.add_trace(go.Surface(
            z=np.full(grid_data.shape, i),
            surfacecolor=grid_data,
            colorscale='Viridis',
            name=f"Año {year}",
            opacity=0.8,
            contours_z=dict(show=True, usecolormap=True, project_z=True)
        ))

    # 3. CAPA DE PREDICCIÓN (Última traza)
    has_predictions = predictions is not None
    if has_predictions:
        pred_height = len(years)
        # Reconstruimos la malla de predicción basada en la última geometría
        grid_pred = np.full(all_grids[years[-1]].shape, np.mean(predictions))
        fig.add_trace(go.Surface(
            z=np.full(grid_pred.shape, pred_height),
            surfacecolor=grid_pred,
            colorscale='Reds',
            name="Predicción 2026",
            opacity=0.7,
            visible=True # Visible por defecto
        ))

    # 4. BOTONES DE FILTRADO (Interactividad)
    # Calculamos cuántas trazas hay en total (Base + Históricos + IA)
    total_traces = 1 + num_historical + (1 if has_predictions else 0)
    
    # El filtro de IA afecta solo a la última traza
    visibility_show = [True] * total_traces
    visibility_hide = [True] * (total_traces - 1) + [False]

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5, xanchor="center", y=1.08, yanchor="top",
                buttons=[
                    dict(label="Analizar Histórico (Ocultar IA)",
                         method="update",
                         args=[{"visible": visibility_hide}]),
                    dict(label="Ver Todo (Mostrar IA)",
                         method="update",
                         args=[{"visible": visibility_show}])
                ],
                showactive=True,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#e74c3c"
            )
        ],
        title='Cubo Llanquihue: Control de Capas Predictivas',
        scene=dict(
            yaxis=dict(title='SUR <---> NORTE', tickvals=[0, rows-1], ticktext=['Pto. Octay', 'Pto. Varas']),
            xaxis=dict(title='OESTE <---> ESTE', tickvals=[0, cols-1], ticktext=['Llanquihue', 'Ensenada']),
            zaxis=dict(
                title='TIEMPO',
                tickvals=list(range(len(years) + 1)), 
                ticktext=[str(y) for y in years] + ["2026 (IA)"]
            ),
            aspectratio=dict(x=1, y=1, z=1.3)
        ),
        margin=dict(l=0, r=0, b=0, t=80)
    )

    fig.show()