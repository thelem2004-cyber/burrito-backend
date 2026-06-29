# routers/buses.py
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session
from database.conexion import get_db
from database.modelos import Bus
from services import tracking
from data.rutas import RUTAS

router = APIRouter(tags=["Buses y Rutas"])

BASE_DIR = Path(__file__).resolve().parent.parent


@router.get("/buses", summary="Estado de todos los buses")
def obtener_buses():
    """Devuelve la posición y estado de señal de todos los buses."""
    return {"buses": tracking.obtener_todos_los_buses()}


@router.get("/buses/disponibles", summary="Buses disponibles para conductores")
def obtener_buses_disponibles(db: Session = Depends(get_db)):
    """Devuelve los buses que no están activos (disponibles para asignar)."""
    buses = db.query(Bus).filter(Bus.activo == False).all()
    return {"buses": [{"id": b.id, "placa": b.placa} for b in buses]}


@router.get("/buses/todos", summary="Todos los buses registrados")
def obtener_todos_buses(db: Session = Depends(get_db)):
    """Devuelve todos los buses con su estado."""
    buses = db.query(Bus).all()
    return {"buses": [
        {"id": b.id, "placa": b.placa, "ruta": b.ruta, "activo": b.activo}
        for b in buses
    ]}


@router.get("/rutas", summary="Catálogo de rutas y paraderos")
def obtener_rutas():
    """Devuelve las 4 rutas con todos sus paraderos y coordenadas."""
    return {"rutas": RUTAS}


@router.get("/admin", tags=["Admin"])
def panel_admin():
    """Panel de administración con mapa en tiempo real."""
    return FileResponse(BASE_DIR / "admin.html")