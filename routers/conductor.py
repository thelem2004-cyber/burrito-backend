# routers/conductor.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.conexion import get_db
from database.modelos import Bus, Recorrido, PuntoRecorrido
from models.bus import PosicionBus
from services import tracking
from datetime import datetime, timezone

router = APIRouter(prefix="/conductor", tags=["Conductor"])


class IniciarTurno(BaseModel):
    placa: str
    ruta: str
    usuario_id: int


class DetenerTurno(BaseModel):
    placa: str


@router.post("/iniciar_turno", summary="Iniciar turno del conductor")
def iniciar_turno(datos: IniciarTurno, db: Session = Depends(get_db)):
    """
    El conductor selecciona su unidad y ruta.
    Marca el bus como activo e inicia un nuevo recorrido.
    """
    bus = db.query(Bus).filter(Bus.placa == datos.placa).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    if bus.activo:
        raise HTTPException(status_code=400,
            detail="Este bus ya está en uso por otro conductor")

    # Marcar bus como activo
    bus.activo = True
    bus.ruta = datos.ruta
    db.commit()

    from datetime import datetime, timezone

    recorrido = Recorrido(
        bus_placa=datos.placa,
        ruta=datos.ruta,
        hora_inicio=datetime.now(timezone.utc),
    )
    db.add(recorrido)
    db.commit()
    db.refresh(recorrido)

    return {
        "mensaje": "Turno iniciado",
        "bus_id": datos.placa,
        "recorrido_id": recorrido.id
    }


@router.post("/posicion", summary="Registrar posición del bus")
def registrar_posicion(datos: PosicionBus, db: Session = Depends(get_db)):
    """
    Recibe la posición GPS del conductor cada 3 segundos.
    Guarda en Firebase, SQLite y registra el punto en el recorrido activo.
    """
    tracking.registrar_posicion(
        bus_id=datos.bus_id,
        ruta=datos.ruta,
        latitud=datos.latitud,
        longitud=datos.longitud,
    )

    # Guardar punto en el recorrido activo
    recorrido = db.query(Recorrido).filter(
        Recorrido.bus_placa == datos.bus_id,
        Recorrido.completado == False
    ).order_by(Recorrido.id.desc()).first()

    if recorrido:
        punto = PuntoRecorrido(
            recorrido_id=recorrido.id,
            latitud=datos.latitud,
            longitud=datos.longitud,
        )
        db.add(punto)
        db.commit()

    return {"estado": "posición actualizada"}


@router.post("/detener_turno", summary="Detener turno del conductor")
def detener_turno(datos: DetenerTurno, db: Session = Depends(get_db)):
    """
    El conductor apaga el GPS.
    Marca el bus como inactivo y cierra el recorrido activo.
    """
    bus = db.query(Bus).filter(Bus.placa == datos.placa).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    # Marcar bus como inactivo
    bus.activo = False
    db.commit()

    # Cerrar recorrido activo
    recorrido = db.query(Recorrido).filter(
        Recorrido.bus_placa == datos.placa,
        Recorrido.completado == False
    ).order_by(Recorrido.id.desc()).first()

    if recorrido:
        recorrido.hora_fin = datetime.now(timezone.utc)
        recorrido.completado = True
        db.commit()

    return {"mensaje": "Turno finalizado"}