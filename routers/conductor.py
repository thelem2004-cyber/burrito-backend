# routers/conductor.py
# Endpoints de la app del Conductor.
# Responsabilidad única: recibir la posición GPS del conductor.

from fastapi import APIRouter
from models.bus import PosicionBus
from services import tracking

router = APIRouter(prefix="/conductor", tags=["Conductor"])


@router.post("/posicion", summary="Registrar posición del bus")
def registrar_posicion(datos: PosicionBus):
    """
    Recibe la posición GPS del conductor cada 3 segundos (US05).
    La app del conductor llama a este endpoint automáticamente mientras
    está en servicio.
    """
    tracking.registrar_posicion(
        bus_id=datos.bus_id,
        ruta=datos.ruta,
        latitud=datos.latitud,
        longitud=datos.longitud,
    )
    return {"estado": "posición actualizada"}
