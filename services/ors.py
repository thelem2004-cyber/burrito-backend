# services/ors.py
# Integración con OpenRouteService para ETA y trazado de rutas.

import os
import httpx

ORS_API_KEY = os.getenv("ORS_API_KEY", "")
ORS_BASE = "https://api.openrouteservice.org/v2"


async def obtener_ruta(
    origen_lng: float, origen_lat: float,
    destino_lng: float, destino_lat: float
) -> dict:
    """
    Dado un origen y destino, devuelve:
    - duracion_segundos: tiempo estimado de viaje
    - distancia_metros: distancia total
    - puntos: lista de [lat, lng] de la ruta siguiendo calles reales
    """
    url = f"{ORS_BASE}/directions/driving-car/geojson"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "coordinates": [
            [origen_lng, origen_lat],
            [destino_lng, destino_lat],
        ]
    }

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.post(url, headers=headers, json=body)
        res.raise_for_status()
        data = res.json()

    feature = data["features"][0]
    segmento = feature["properties"]["segments"][0]
    coordenadas = feature["geometry"]["coordinates"]

    # ORS devuelve [lng, lat] — convertimos a [lat, lng]
    puntos = [[c[1], c[0]] for c in coordenadas]

    return {
        "duracion_segundos": segmento["duration"],
        "distancia_metros": segmento["distance"],
        "puntos": puntos,
    }


async def obtener_eta_segundos(
    origen_lng: float, origen_lat: float,
    destino_lng: float, destino_lat: float
) -> float:
    """Devuelve solo el tiempo estimado en segundos entre dos puntos."""
    ruta = await obtener_ruta(origen_lng, origen_lat, destino_lng, destino_lat)
    return ruta["duracion_segundos"]