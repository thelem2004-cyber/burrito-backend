# routers/pasajero.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.pasajero import SolicitudRecomendacion
from services.recomendacion import calcular_recomendacion
from services import tracking
from services.ors import obtener_ruta
import json

router = APIRouter(prefix="/pasajero", tags=["Pasajero"])


class SolicitudETA(BaseModel):
    bus_id: str           # placa del bus que sigue el pasajero
    paradero_lat: float   # paradero donde esperará el pasajero
    paradero_lng: float


class SolicitudETADestino(BaseModel):
    bus_id: str           # placa del bus en el que va el pasajero
    destino_lat: float    # paradero destino del pasajero
    destino_lng: float


@router.post("/recomendar", summary="Recomendar bus, paradero y ETA")
def recomendar(solicitud: SolicitudRecomendacion):
    resultado = calcular_recomendacion(
        paradero_destino_id=solicitud.paradero_destino_id,
        pasajero_lat=solicitud.pasajero_lat,
        pasajero_lng=solicitud.pasajero_lng,
    )
    return resultado


@router.post("/eta/paradero", summary="ETA del bus hasta el paradero del pasajero")
async def eta_hasta_paradero(solicitud: SolicitudETA):
    """
    Calcula cuánto tardará el bus en llegar al paradero donde espera el pasajero.
    Usa la posición actual del bus desde Firebase y ORS para el cálculo.
    """
    buses = tracking.obtener_todos_los_buses()
    bus = next((b for b in buses if b["bus_id"] == solicitud.bus_id), None)

    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado o sin señal")
    if not bus["con_señal"]:
        raise HTTPException(status_code=400, detail="El bus no tiene señal activa")

    try:
        resultado = await obtener_ruta(
            origen_lng=bus["longitud"],
            origen_lat=bus["latitud"],
            destino_lng=solicitud.paradero_lng,
            destino_lat=solicitud.paradero_lat,
        )
        return {
            "bus_id": solicitud.bus_id,
            "eta_segundos": round(resultado["duracion_segundos"]),
            "eta_minutos": round(resultado["duracion_segundos"] / 60, 1),
            "distancia_metros": round(resultado["distancia_metros"]),
            "bus_lat": bus["latitud"],
            "bus_lng": bus["longitud"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular ETA: {str(e)}")


@router.post("/eta/destino", summary="ETA del bus hasta el paradero destino del pasajero")
async def eta_hasta_destino(solicitud: SolicitudETADestino):
    """
    Cuando el pasajero ya está en el bus, calcula cuánto falta para llegar
    a su paradero destino usando la posición actual del bus.
    """
    buses = tracking.obtener_todos_los_buses()
    bus = next((b for b in buses if b["bus_id"] == solicitud.bus_id), None)

    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado o sin señal")

    try:
        resultado = await obtener_ruta(
            origen_lng=bus["longitud"],
            origen_lat=bus["latitud"],
            destino_lng=solicitud.destino_lng,
            destino_lat=solicitud.destino_lat,
        )
        return {
            "bus_id": solicitud.bus_id,
            "eta_segundos": round(resultado["duracion_segundos"]),
            "eta_minutos": round(resultado["duracion_segundos"] / 60, 1),
            "distancia_metros": round(resultado["distancia_metros"]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular ETA: {str(e)}")