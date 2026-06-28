# models/pasajero.py
# Clases de datos que representan lo que la API recibe del pasajero.

from pydantic import BaseModel


class SolicitudRecomendacion(BaseModel):
    """Datos que envía la app del pasajero al pedir una recomendación."""
    paradero_destino_id: str  # ID del paradero al que quiere llegar (ej: "CN11")
    pasajero_lat: float       # ubicación actual del pasajero
    pasajero_lng: float


class Recomendacion(BaseModel):
    """Respuesta del sistema al pasajero."""
    bus_id: str
    ruta: str
    paradero_recomendado: str   # nombre del paradero donde debe esperar
    paradero_id: str
    eta_minutos: float          # tiempo estimado de llegada del bus al paradero
    caminar_minutos: float      # tiempo estimado caminando hasta el paradero
    tiempo_total: float         # eta + caminar
