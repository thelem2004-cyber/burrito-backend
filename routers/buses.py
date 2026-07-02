# routers/buses.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.conexion import get_db
from database.modelos import Bus
from services import tracking
from data.rutas import RUTAS

router = APIRouter(tags=["Buses y Rutas"])

BASE_DIR = Path(__file__).resolve().parent.parent


class NuevoBus(BaseModel):
    placa: str


class EditarBus(BaseModel):
    placa: str


@router.get("/buses", summary="Estado de todos los buses en tiempo real")
def obtener_buses():
    return {"buses": tracking.obtener_todos_los_buses()}


@router.get("/buses/disponibles", summary="Buses disponibles para conductores")
def obtener_buses_disponibles(db: Session = Depends(get_db)):
    buses = db.query(Bus).filter(Bus.activo == False).all()
    return {"buses": [{"id": b.id, "placa": b.placa} for b in buses]}


@router.get("/buses/todos", summary="Todos los buses registrados")
def obtener_todos_buses(db: Session = Depends(get_db)):
    buses = db.query(Bus).all()
    return {"buses": [
        {"id": b.id, "placa": b.placa, "ruta": b.ruta, "activo": b.activo}
        for b in buses
    ]}


@router.post("/buses/nuevo", summary="Crear nuevo bus")
def crear_bus(datos: NuevoBus, db: Session = Depends(get_db)):
    existe = db.query(Bus).filter(Bus.placa == datos.placa).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un bus con esa placa")
    bus = Bus(placa=datos.placa, activo=False)
    db.add(bus)
    db.commit()
    db.refresh(bus)
    return {"mensaje": "Bus creado", "id": bus.id, "placa": bus.placa}


@router.put("/buses/{bus_id}", summary="Editar placa de un bus")
def editar_bus(bus_id: int, datos: EditarBus, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    if bus.activo:
        raise HTTPException(status_code=400, detail="No se puede editar un bus activo")
    bus.placa = datos.placa
    db.commit()
    return {"mensaje": "Bus actualizado", "placa": bus.placa}


@router.delete("/buses/{bus_id}", summary="Eliminar un bus")
def eliminar_bus(bus_id: int, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    if bus.activo:
        raise HTTPException(status_code=400, detail="No se puede eliminar un bus activo")
    db.delete(bus)
    db.commit()
    return {"mensaje": "Bus eliminado"}


@router.post("/buses/{bus_id}/liberar", summary="Liberar un bus atascado")
def liberar_bus(bus_id: int, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    bus.activo = False
    db.commit()
    return {"mensaje": "Bus liberado", "placa": bus.placa}


@router.get("/rutas", summary="Catálogo de rutas y paraderos")
def obtener_rutas():
    return {"rutas": RUTAS}


@router.get("/admin", tags=["Admin"])
def panel_admin():
    return FileResponse(BASE_DIR / "admin.html")