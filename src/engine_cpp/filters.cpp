// src\engine_cpp\filters.cpp
/*
Implementaremos un filtro de media móvil espacial para suavizar el ruido que se ve en tu imagen actual.
*/

#include <vector>
#include <numeric>

// Algoritmo de suavizado espacial para datos multiespectrales
std::vector<double> apply_spatial_filter(const std::vector<double> &data, int rows, int cols, int window_size)
{
    std::vector<double> result(data.size(), 0.0);
    int offset = window_size / 2;

    for (int i = offset; i < rows - offset; ++i)
    {
        for (int j = offset; j < cols - offset; ++j)
        {
            double sum = 0.0;
            int count = 0;
            for (int ki = -offset; ki <= offset; ++ki)
            {
                for (int kj = -offset; kj <= offset; ++kj)
                {
                    double val = data[(i + ki) * cols + (j + kj)];
                    if (val != 0)
                    { // Ignorar píxeles enmascarados
                        sum += val;
                        count++;
                    }
                }
            }
            result[i * cols + j] = (count > 0) ? sum / count : 0.0;
        }
    }
    return result;
}

std::vector<double> detect_anomalies(const std::vector<double> &data, double threshold)
{
    std::vector<double> anomalies(data.size(), 0.0);
    for (size_t i = 0; i < data.size(); ++i)
    {
        if (data[i] > threshold)
        {
            anomalies[i] = 1.0; // Marca como anomalía
        }
    }
    return anomalies;
}

std::vector<int> classify_risk(const std::vector<double>& ndci, const std::vector<double>& anomalies) {
    std::vector<int> risk_levels(ndci.size(), 0);
    for (size_t i = 0; i < ndci.size(); ++i) {
        if (anomalies[i] > 0) {
            if (ndci[i] > 0.25) risk_levels[i] = 3;      // CRÍTICO
            else if (ndci[i] > 0.15) risk_levels[i] = 2; // ALTO
            else risk_levels[i] = 1;                    // MODERADO
        }
    }
    return risk_levels;
}

// Interpola linealmente valores faltantes en una serie temporal (Gap Filling)
std::vector<double> interpolate_time_series(std::vector<double> series) {
    size_t n = series.size();
    if (n < 3) return series;

    for (size_t i = 0; i < n; ++i) {
        // Definimos un hueco si el valor es 0 (ajustar según el sensor)
        if (series[i] == 0.0) {
            size_t prev = (i > 0) ? i - 1 : i;
            size_t next = i + 1;
            
            // Buscar el siguiente valor válido
            while (next < n && series[next] == 0.0) {
                next++;
            }

            if (next < n) {
                // Interpolación lineal: y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
                double y0 = series[prev];
                double y1 = series[next];
                double steps = next - prev;
                double slope = (y1 - y0) / steps;
                
                for (size_t j = prev + 1; j < next; ++j) {
                    series[j] = y0 + slope * (j - prev);
                }
                i = next - 1;
            } else {
                // Si no hay más datos, mantener el último válido
                for (size_t j = i; j < n; ++j) series[j] = series[prev];
            }
        }
    }
    return series;
}