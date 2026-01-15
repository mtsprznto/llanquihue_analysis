# src\visualization\predictive_plotter.py

import locale
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator
import matplotlib.pyplot as plt
import pandas as pd

def plot_prediction_results(csv_path, predictions, year_target=2026):
    # Intentar configurar fechas en español si el sistema lo permite
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        try:
            locale.setlocale(locale.LC_TIME, "spanish")
        except:
            pass # Si falla, usará el idioma por defecto

    # 1. Cargar datos
    df = pd.read_csv(csv_path, index_col=0)
    full_history = []
    for col in df.columns:
        full_history.extend(df[col].values)
    
    # 2. CREAR LÍNEA DE TIEMPO REAL
    start_date = "2019-01-01"
    total_months = len(full_history) + len(predictions)
    date_range = pd.date_range(start=start_date, periods=total_months, freq='MS')
    
    dates_history = date_range[:len(full_history)]
    dates_pred = date_range[len(full_history):]
    
    # 3. Configurar Estética
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(16, 8))
    
    ax.plot(dates_history, full_history, color='#2c3e50', label='Histórico (2019-2025)', alpha=0.6, linewidth=1.5)
    ax.plot(dates_pred, predictions, color='#e74c3c', linestyle='--', marker='o', 
            label=f'Proyección IA {year_target}', linewidth=2, markersize=4)
    
    ax.fill_between(dates_pred, predictions, color='#e74c3c', alpha=0.1)
    ax.axhline(y=0.1, color='orange', linestyle=':', label='Umbral Alerta Algal (0.1 NDCI)')
    
    # 4. FORMATEAR EJE X (Años y Meses)
    # Localizador Principal: Cada año (muestra el año abajo)
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("\n%Y")) # El \n lo pone en una segunda línea
    
    # Localizador Secundario: Cada mes (muestra ene, feb...)
    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_minor_formatter(DateFormatter("%b")) # %b es el nombre abreviado del mes
    
    # Configurar visualización de los ticks
    ax.tick_params(axis='x', which='minor', labelsize=8, rotation=45)
    ax.tick_params(axis='x', which='major', labelsize=11, pad=15)

    # CORRECCIÓN PARA NEGRITA: Acceder a las etiquetas después de crearlas
    plt.setp(ax.get_xticklabels(minor=False), fontweight='bold')

    # Vista completa
    ax.set_xlim(dates_history[0], dates_pred[-1])
    
    # Títulos y etiquetas
    plt.title(f"Análisis Predictivo de Calidad de Agua: Lago Llanquihue {year_target}", fontsize=15, pad=25)
    plt.ylabel("Intensidad NDCI (Clorofila)", fontsize=12)
    plt.legend(loc='upper left', frameon=True)
    
    plt.tight_layout()
    
    # Guardar
    output_path = f"data/reports/prediction_full_{year_target}.png"
    plt.savefig(output_path)
    print(f"Gráfico completo con meses guardado en: {output_path}")
    
    plt.show()