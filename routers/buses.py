# routers/buses.py
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
from services import tracking
from data.rutas import RUTAS

router = APIRouter(tags=["Buses y Rutas"])

BASE_DIR = Path(__file__).resolve().parent.parent


@router.get("/buses", summary="Estado de todos los buses")
def obtener_buses():
    return {"buses": tracking.obtener_todos_los_buses()}


@router.get("/rutas", summary="Catálogo de rutas y paraderos")
def obtener_rutas():
    return {"rutas": RUTAS}


@router.get("/admin", tags=["Admin"])
def panel_admin():
    """Panel de administración con mapa en tiempo real."""
    return FileResponse(BASE_DIR / "admin.html")