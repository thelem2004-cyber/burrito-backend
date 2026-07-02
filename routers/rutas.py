# routers/rutas.py
# Endpoints para trazado de rutas con OpenRouteService.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database.conexion import get_db
from database.modelos import RutaTrazadaAdmin
from services.ors import obtener_ruta

router = APIRouter(prefix="/rutas-admin", tags=["Rutas Admin"])


class PuntoRuta(BaseModel):
    lat: float
    lng: float


class CrearRuta(BaseModel):
    nombre: str
    ruta_clave: str  # "cono_norte", "cono_sur", etc.
    puntos: List[PuntoRuta]


class RutaResponse(BaseModel):
    id: int
    nombre: str
    ruta_clave: str
    duracion_segundos: float
    distancia_metros: float
    puntos: List[List[float]]


@router.post("/trazar", summary="Trazar ruta con OpenRouteService")
async def trazar_ruta(datos: CrearRuta, db: Session = Depends(get_db)):
    """
    El admin envía puntos clave de la ruta.
    ORS genera la ruta real siguiendo calles de Lima.
    """
    if len(datos.puntos) < 2:
        raise HTTPException(status_code=400,
            detail="Se necesitan al menos 2 puntos para trazar una ruta")

    # Llamar a ORS tramo por tramo y unir los puntos
    todos_los_puntos = []
    duracion_total = 0
    distancia_total = 0

    for i in range(len(datos.puntos) - 1):
        origen = datos.puntos[i]
        destino = datos.puntos[i + 1]
        try:
            resultado = await obtener_ruta(
                origen.lng, origen.lat,
                destino.lng, destino.lat
            )
            todos_los_puntos.extend(resultado["puntos"])
            duracion_total += resultado["duracion_segundos"]
            distancia_total += resultado["distancia_metros"]
        except Exception as e:
            raise HTTPException(status_code=500,
                detail=f"Error al trazar tramo {i+1}: {str(e)}")

    # Guardar en base de datos
    import json
    ruta = RutaTrazadaAdmin(
        nombre=datos.nombre,
        ruta_clave=datos.ruta_clave,
        puntos=json.dumps(todos_los_puntos),
        duracion_segundos=duracion_total,
        distancia_metros=distancia_total,
    )
    db.add(ruta)
    db.commit()
    db.refresh(ruta)

    return {
        "mensaje": "Ruta trazada correctamente",
        "id": ruta.id,
        "nombre": ruta.nombre,
        "duracion_minutos": round(duracion_total / 60, 1),
        "distancia_km": round(distancia_total / 1000, 2),
        "puntos": todos_los_puntos,
    }


@router.get("/", summary="Listar todas las rutas trazadas")
def listar_rutas(db: Session = Depends(get_db)):
    import json
    rutas = db.query(RutaTrazadaAdmin).all()
    return {"rutas": [
        {
            "id": r.id,
            "nombre": r.nombre,
            "ruta_clave": r.ruta_clave,
            "duracion_minutos": round(r.duracion_segundos / 60, 1),
            "distancia_km": round(r.distancia_metros / 1000, 2),
            "puntos": json.loads(r.puntos),
        }
        for r in rutas
    ]}


@router.get("/{ruta_id}", summary="Obtener una ruta trazada")
def obtener_ruta_admin(ruta_id: int, db: Session = Depends(get_db)):
    import json
    ruta = db.query(RutaTrazadaAdmin).filter(
        RutaTrazadaAdmin.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {
        "id": ruta.id,
        "nombre": ruta.nombre,
        "ruta_clave": ruta.ruta_clave,
        "duracion_minutos": round(ruta.duracion_segundos / 60, 1),
        "distancia_km": round(ruta.distancia_metros / 1000, 2),
        "puntos": json.loads(ruta.puntos),
    }


@router.delete("/{ruta_id}", summary="Eliminar una ruta trazada")
def eliminar_ruta(ruta_id: int, db: Session = Depends(get_db)):
    ruta = db.query(RutaTrazadaAdmin).filter(
        RutaTrazadaAdmin.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    db.delete(ruta)
    db.commit()
    return {"mensaje": "Ruta eliminada"}