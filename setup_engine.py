# setup_engine.py
import sys
import subprocess
import os
import sysconfig
from pathlib import Path

def compile_engine():
    # 1. Obtener las rutas de cabeceras de Python de forma robusta
    py_include = sysconfig.get_path('include')
    # En entornos virtuales, a veces necesitamos las cabeceras de la instalación base
    py_include_base = sysconfig.get_path('include', vars={'base': sys.base_prefix})
    
    py_libs = os.path.join(sys.base_prefix, "libs")
    py_ver = f"{sys.version_info.major}{sys.version_info.minor}"
    
    # 2. Ruta de pybind11 (usamos Path para que sea compatible con Windows/Linux)
    # Intentamos encontrarlo automáticamente a través de python
    try:
        import pybind11
        pybind_include = pybind11.get_include()
    except ImportError:
        # Fallback a ruta manual si no está instalado en el path de búsqueda
        pybind_include = Path(".venv/Lib/site-packages/pybind11/include")

    # 3. Construir el comando con ambas posibles rutas de inclusión
    cmd = [
        "g++", "-O3", "-Wall", "-shared", "-std=c++17",
        f"-I{py_include}",
        f"-I{py_include_base}",
        f"-I{pybind_include}",
        "src/engine_cpp/bindings.cpp",
        "-o", "src/engine_cpp/lib/engine_core.pyd",
        f"-L{py_libs}",
        f"-lpython{py_ver}"
    ]

    print(f"Compilando Motor C++...")
    print(f" Usando Include: {py_include}")
    
    try:
        # Ejecutamos el comando
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("¡Éxito! engine_core.pyd generado.")
    except subprocess.CalledProcessError as e:
        print("❌ Error durante la compilación:")
        print(e.stderr)

if __name__ == "__main__":
    compile_engine()