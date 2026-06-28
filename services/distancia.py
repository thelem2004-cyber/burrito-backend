# services/distancia.py
# Utilidades de cálculo geográfico.
# Responsabilidad única: operaciones matemáticas sobre coordenadas GPS.

import math


def distancia_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcula la distancia en kilómetros entre dos puntos GPS
    usando la fórmula de Haversine.
    """
    R = 6371  # radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def eta_baseline(distancia: float, velocidad_kmh: float = 25.0) -> float:
    """
    Calcula el tiempo estimado de llegada (ETA) en minutos.
    Baseline simple: distancia / velocidad promedio.
    Velocidad default: 25 km/h (promedio del Burrito en Lima con tráfico).
    Este valor será reemplazado por el modelo de ML cuando haya datos reales.
    """
    return round((distancia / velocidad_kmh) * 60, 1)


def tiempo_caminando(distancia: float, velocidad_kmh: float = 5.0) -> float:
    """
    Calcula el tiempo en minutos caminando hasta un paradero.
    Velocidad default: 5 km/h (paso normal de una persona).
    """
    return round((distancia / velocidad_kmh) * 60, 1)


def paradero_mas_cercano(lat: float, lng: float, paraderos: list) -> dict:
    """
    Devuelve el paradero más cercano a una coordenada dada.
    paraderos: lista de dicts con campos 'lat' y 'lng'.
    """
    return min(
        paraderos,
        key=lambda p: distancia_km(lat, lng, p["lat"], p["lng"])
    )
