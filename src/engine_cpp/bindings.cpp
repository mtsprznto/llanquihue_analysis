// src\engine_cpp\bindings.cpp
/*
Este archivo "expone" la función de C++ para que la llames desde tu main.py.
*/


#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "filters.cpp"

namespace py = pybind11;

PYBIND11_MODULE(engine_core, m) {
    m.doc() = "Llanquihue Engine Core: Procesamiento C++ de alto rendimiento";
    
    // 1. Suavizado espacial (Fase 2)
    m.def("apply_spatial_filter", &apply_spatial_filter, "Aplica un filtro de media móvil para reducir ruido espectral");
    
    // 2. Detección de Anomalías (Fase 3)
    m.def("detect_anomalies", &detect_anomalies, "Identifica píxeles que superan un umbral estadístico");
    // 3. Clasificación de Riesgo (Fase 4)
    m.def("classify_risk", &classify_risk, "Clasifica el nivel de riesgo ambiental (0-3) basado en intensidad de NDCI");

    m.def("interpolate_time_series", &interpolate_time_series, "Reconstruye datos faltantes en series temporales usando interpolación lineal");
}
