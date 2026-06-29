# routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.conexion import get_db
from database.modelos import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


class RegistroUsuario(BaseModel):
    nombre: str
    correo: str
    password: str
    tipo: str  # "pasajero" o "conductor"


class LoginUsuario(BaseModel):
    correo: str
    password: str


@router.post("/registro", summary="Registrar nuevo usuario")
def registrar(datos: RegistroUsuario, db: Session = Depends(get_db)):
    """Registra un nuevo pasajero o conductor."""
    existe = db.query(Usuario).filter(Usuario.correo == datos.correo).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password=datos.password,
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


@router.put("/{usuario_id}", summary="Actualizar nombre de usuario")
def actualizar_nombre(usuario_id: int, datos: dict, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = datos.get("nombre", usuario.nombre)
    db.commit()
    return {"mensaje": "Nombre actualizado", "nombre": usuario.nombre}