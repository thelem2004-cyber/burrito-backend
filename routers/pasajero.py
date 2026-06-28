# routers/pasajero.py
# Endpoints de la app del Pasajero.
# Responsabilidad única: recibir el destino y devolver la recomendación.

from fastapi import APIRouter
from models.pasajero import SolicitudRecomendacion
from services.recomendacion import calcular_recomendacion

router = APIRouter(prefix="/pasajero", tags=["Pasajero"])


@router.post("/recomendar", summary="Recomendar bus, paradero y ETA")
def recomendar(solicitud: SolicitudRecomendacion):
    """
    Recibe el destino del pasajero y devuelve (US02 + US03 + US04):
    - El bus más conveniente
    - El paradero óptimo donde esperar
    - El tiempo estimado de llegada (ETA)

    Aplica RN1: si no hay incidente activo, el ETA es el calculado por el modelo.
    Aplica RN2: (pendiente) si hay incidente, ajusta el ETA.
    """
    resultado = calcular_recomendacion(
        paradero_destino_id=solicitud.paradero_destino_id,
        pasajero_lat=solicitud.pasajero_lat,
        pasajero_lng=solicitud.pasajero_lng,
    )
    return resultado
