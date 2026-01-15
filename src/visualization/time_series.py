# src\visualization\time_series.py

import matplotlib.pyplot as plt

def plot_historical_quality(months, original_data, interpolated_data, year):
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(12, 6))
    
    # Dibujar la serie interpolada (línea suave)
    plt.plot(months, interpolated_data, color='#008080', label='Tendencia Reconstruida (C++)', 
             linewidth=3, alpha=0.8)
    
    # Dibujar los puntos originales para transparencia científica
    plt.scatter(months, original_data, color='red', label='Datos Crutos (Satélite)', zorder=5)
    
    plt.fill_between(months, interpolated_data, color='#008080', alpha=0.15)
    plt.title(f"Análisis de Calidad de Agua - Lago Llanquihue {year}", fontsize=14)
    plt.ylabel("Intensidad NDCI (Clorofila)")
    plt.legend()
    
    output_path = f"data/reports/history_{year}.png"
    plt.savefig(output_path)
    print(f"Reporte gráfico guardado en: {output_path}")
    #plt.show() # descomentar para ver inmediatamente