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


class EditarUsuario(BaseModel):
    nombre: str
    tipo: str


@router.get("/", summary="Listar todos los usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return {"usuarios": [
        {"id": u.id, "nombre": u.nombre, "correo": u.correo, "tipo": u.tipo}
        for u in usuarios
    ]}


@router.post("/registro", summary="Registrar nuevo usuario")
def registrar(datos: RegistroUsuario, db: Session = Depends(get_db)):
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


@router.put("/{usuario_id}", summary="Editar usuario")
def editar_usuario(usuario_id: int, datos: EditarUsuario, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = datos.nombre
    usuario.tipo = datos.tipo
    db.commit()
    return {"mensaje": "Usuario actualizado", "nombre": usuario.nombre, "tipo": usuario.tipo}


@router.delete("/{usuario_id}", summary="Eliminar usuario")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado"}