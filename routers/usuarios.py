# routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.conexion import get_db
from database.modelos import Usuario, Conductor

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ─── Modelos de entrada ───────────────────────────────────────────────────────

class RegistroUsuario(BaseModel):
    nombre: str
    correo: str
    password: str
    tipo: str  # "pasajero" o "conductor"

class LoginUsuario(BaseModel):
    correo: str
    password: str

class RegistroConductor(BaseModel):
    usuario_id: int
    bus_id: str
    ruta: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/registro", summary="Registrar nuevo usuario")
def registrar(datos: RegistroUsuario, db: Session = Depends(get_db)):
    """Registra un nuevo pasajero o conductor."""
    existe = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password=datos.password,  # en producción se encriptaría con bcrypt
        tipo=datos.tipo
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"mensaje": "Usuario registrado", "id": usuario.id, "tipo": usuario.tipo}


@router.post("/login", summary="Iniciar sesión")
def login(datos: LoginUsuario, db: Session = Depends(get_db)):
    """Valida credenciales y devuelve los datos del usuario."""
    usuario = db.query(Usuario).filter(
        Usuario.correo == datos.correo,
        Usuario.password == datos.password
    ).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    return {
        "mensaje": "Login exitoso",
        "id": usuario.id,
        "nombre": usuario.nombre,
        "tipo": usuario.tipo
    }


@router.post("/conductor", summary="Registrar datos de conductor")
def registrar_conductor(datos: RegistroConductor, db: Session = Depends(get_db)):
    """Asocia un usuario tipo conductor con un bus y ruta."""
    conductor = Conductor(
        usuario_id=datos.usuario_id,
        bus_id=datos.bus_id,
        ruta=datos.ruta
    )
    db.add(conductor)
    db.commit()
    db.refresh(conductor)
    return {"mensaje": "Conductor registrado", "id": conductor.id}


@router.get("/conductores", summary="Lista de conductores")
def listar_conductores(db: Session = Depends(get_db)):
    """Devuelve todos los conductores registrados."""
    conductores = db.query(Conductor).all()
    return {"conductores": [
        {"id": c.id, "usuario_id": c.usuario_id, "bus_id": c.bus_id, "ruta": c.ruta}
        for c in conductores
    ]}

@router.put("/{usuario_id}", summary="Actualizar nombre de usuario")
def actualizar_nombre(usuario_id: int, datos: dict, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = datos.get("nombre", usuario.nombre)
    db.commit()
    return {"mensaje": "Nombre actualizado", "nombre": usuario.nombre}