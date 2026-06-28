# services/firebase.py
import os
import json
import firebase_admin
from firebase_admin import credentials, db

_inicializado = False

def inicializar():
    global _inicializado
    if _inicializado:
        return

    firebase_creds = os.environ.get("FIREBASE_CREDENTIALS")
    if firebase_creds:
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("firebase_credentials.json")

    firebase_admin.initialize_app(cred, {
        "databaseURL": os.environ.get(
            "FIREBASE_DATABASE_URL",
            "https://burrito-backend-default-rtdb.firebaseio.com/"
        )
    })
    _inicializado = True

def escribir_posicion(bus_id: str, datos: dict) -> None:
    inicializar()
    ref = db.reference(f"buses/{bus_id}")
    ref.set(datos)

def leer_todos_los_buses() -> dict:
    inicializar()
    ref = db.reference("buses")
    return ref.get() or {}