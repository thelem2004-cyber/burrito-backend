# models/bus.py
from pydantic import BaseModel


class PosicionBus(BaseModel):
    """Datos que envía la app del conductor cada 3 segundos."""
    bus_id: str
    ruta: str
    latitud: float
    longitud: float


class EstadoBus(BaseModel):
    """Estado completo de un bus, incluyendo si tiene señal activa."""
    bus_id: str
    ruta: str
    latitud: float
    longitud: float
    timestamp: str
    con_señal: bool
    segundos_sin_actualizar: float