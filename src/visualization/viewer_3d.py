# src\visualization\viewer_3d.py

import pyvista as pv
import numpy as np

def render_lake_3d(data_grid, title="Calidad de Agua: Lago Llanquihue (15/01/2026)"):
    """
    Renderiza la malla NDCI en 3D de forma profesional.
    """
    # 1. Limpieza de datos: Convertir NaNs (nubes/tierra) a un valor base para evitar huecos feos
    # En teledetección, el 0 suele ser el valor de máscara.
    data_grid = np.nan_to_num(data_grid, nan=0.0)
    
    rows, cols = data_grid.shape
    
    # 2. Crear coordenadas escaladas (Aspect Ratio correcto)
    x = np.linspace(0, cols, cols)
    y = np.linspace(0, rows, rows)
    x, y = np.meshgrid(x, y)
    
    # 3. Z: Exageración vertical para notar los cambios de clorofila
    # Si NDCI es alto (0.2+), habrá un "relieve" alto.
    z = data_grid * 50 

    # 4. Crear malla estructurada
    grid = pv.StructuredGrid(x, y, z)
    grid["NDCI_Intensity"] = data_grid.flatten()

    # 5. Configuración del Plotter
    p = pv.Plotter(window_size=[1200, 800])
    p.set_background("black", top="navy") # Gradiente profesional
    
    # Añadir la malla
    # Cambiamos 'bispectral' por 'linear' o simplemente lo quitamos para ver píxeles reales
    p.add_mesh(grid, 
               scalars="NDCI_Intensity", 
               cmap="viridis", 
               lighting=True, 
               show_edges=False,
               smooth_shading=True) # Reemplaza la interpolación problemática
    
    p.add_scalar_bar("Índice de Clorofila (NDCI)", label_font_size=10)
    p.add_text(title, font_size=12, color="white")
    
    # Añadir ejes para orientación geográfica
    p.add_axes()
    
    print("Abriendo ventana de visualización 3D...")
    p.show()