# services/tracking.py
from datetime import datetime
from services.firebase import escribir_posicion, leer_todos_los_buses
from database.conexion import SessionLocal
from database.modelos import RegistroGPS

UMBRAL_SIN_SEÑAL_SEGUNDOS = 15  # RN3

# Contador por bus para guardar en SQLite cada 30 segundos
_contador_sqlite: dict = {}
INTERVALO_SQLITE = 10  # cada 10 llamadas × 3 segundos = 30 segundos


def registrar_posicion(bus_id: str, ruta: str, latitud: float, longitud: float) -> None:
    """
    Guarda la posición del bus:
    - Firebase: cada 3 segundos (tiempo real para el mapa)
    - SQLite: cada 30 segundos (historial para ML)
    """
    datos = {
        "bus_id":    bus_id,
        "ruta":      ruta,
        "latitud":   latitud,
        "longitud":  longitud,
        "timestamp": datetime.now().isoformat(),
        "con_señal": True
    }

    # 1. Firebase siempre (cada 3 segundos)
    escribir_posicion(bus_id, datos)

    # 2. SQLite cada 30 segundos
    _contador_sqlite[bus_id] = _contador_sqlite.get(bus_id, 0) + 1
    if _contador_sqlite[bus_id] >= INTERVALO_SQLITE:
        _contador_sqlite[bus_id] = 0
        _guardar_en_sqlite(bus_id, ruta, latitud, longitud)


def _guardar_en_sqlite(bus_id: str, ruta: str, latitud: float, longitud: float) -> None:
    """Guarda un registro GPS en SQLite para el historial de ML."""
    db = SessionLocal()
    try:
        registro = RegistroGPS(
            bus_id=bus_id,
            ruta=ruta,
            latitud=latitud,
            longitud=longitud
        )
        db.add(registro)
        db.commit()
    finally:
        db.close()


def _segundos_desde(timestamp_str: str) -> float:
    ultima = datetime.fromisoformat(timestamp_str)
    return (datetime.now() - ultima).total_seconds()


def obtener_todos_los_buses() -> list:
    """Lee buses desde Firebase y evalúa señal (RN3)."""
    buses_firebase = leer_todos_los_buses()
    resultado = []
    for bus in buses_firebase.values():
        b = dict(bus)
        sin_señal = _segundos_desde(b["timestamp"])
        b["con_señal"] = sin_señal < UMBRAL_SIN_SEÑAL_SEGUNDOS
        b["segundos_sin_actualizar"] = round(sin_señal, 1)
        resultado.append(b)
    return resultado


def obtener_buses_activos() -> list:
    return [b for b in obtener_todos_los_buses() if b["con_señal"]]