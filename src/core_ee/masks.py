# src\core_ee\masks.py
"""
Fase 1: Máscaras de Nubes y Calidad de Agua. Para que el análisis del 15 de enero de 2026 sea serio, debemos limpiar la imagen de nubes y sombras antes de calcular la contaminación.
"""

import ee
from config import CLOUD_PROB_COLLECTION

def apply_cloud_mask(image):
    """
    Aplica una máscara de nubes avanzada combinando QA60 y Probabilidad de nubes.
    Referencia: https://developers.google.com/earth-engine/guides/sentinel_2_cloud_masking
    """
    # 1. Usar QA60 para nubes cirrus y opacas
    qa = image.select('QA60').toInt16()
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    
    # 2. Refinar con el dataset de probabilidad (MSK_CLDPRB ya viene en L2A Harmonized)
    cloud_prob = image.select('MSK_CLDPRB')
    mask = mask.And(cloud_prob.lt(20)) # Solo píxeles con <20% de prob. de nube
    
    return image.updateMask(mask)