# services/firebase.py
# Conexión con Firebase Realtime Database.
# Responsabilidad única: leer y escribir posiciones de buses en Firebase.

import firebase_admin
from firebase_admin import credentials, db

_inicializado = False

def inicializar():
    """Inicializa la conexión con Firebase (solo una vez)."""
    global _inicializado
    if _inicializado:
        return
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://burrito-backend-default-rtdb.firebaseio.com/"
    })
    _inicializado = True

def escribir_posicion(bus_id: str, datos: dict) -> None:
    """Escribe la posición de un bus en Firebase."""
    inicializar()
    ref = db.reference(f"buses/{bus_id}")
    ref.set(datos)

def leer_todos_los_buses() -> dict:
    """Lee la posición en vivo de todos los buses desde Firebase."""
    inicializar()
    ref = db.reference("buses")
    return ref.get() or {}