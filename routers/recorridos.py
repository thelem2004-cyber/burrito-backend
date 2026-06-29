# routers/recorridos.py
import json
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from database.conexion import get_db
from database.modelos import Recorrido, PuntoRecorrido

router = APIRouter(prefix="/recorridos", tags=["Recorridos"])

BASE_DIR = Path(__file__).resolve().parent.parent


@router.get("/", summary="Historial de recorridos")
def listar_recorridos(db: Session = Depends(get_db)):
    """Devuelve todos los recorridos registrados."""
    recorridos = db.query(Recorrido).order_by(Recorrido.id.desc()).all()
    return {"recorridos": [
        {
            "id": r.id,
            "bus_placa": r.bus_placa,
            "ruta": r.ruta,
            "hora_inicio": r.hora_inicio.isoformat() if r.hora_inicio else None,
            "hora_fin": r.hora_fin.isoformat() if r.hora_fin else None,
            "completado": r.completado,
        }
        for r in recorridos
    ]}


@router.get("/{recorrido_id}/puntos", summary="Puntos de un recorrido")
def obtener_puntos(recorrido_id: int, db: Session = Depends(get_db)):
    """Devuelve todos los puntos GPS de un recorrido."""
    puntos = db.query(PuntoRecorrido).filter(
        PuntoRecorrido.recorrido_id == recorrido_id
    ).order_by(PuntoRecorrido.id.asc()).all()
    return {"puntos": [
        {
            "lat": round(p.latitud, 4),
            "lng": round(p.longitud, 4),
            "timestamp": p.timestamp.isoformat() if p.timestamp else None,
        }
        for p in puntos
    ]}


@router.get("/pagina", summary="Página de historial de recorridos")
def pagina_recorridos():
    return FileResponse(BASE_DIR / "recorridos.html")