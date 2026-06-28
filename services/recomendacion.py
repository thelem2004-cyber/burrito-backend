# services/recomendacion.py
# Lógica de negocio para recomendar bus, paradero y calcular ETA.
# Responsabilidad única: tomar los buses activos y el destino del pasajero
# y devolver la mejor opción.
#
# NOTA: el cálculo de ETA actual es el BASELINE (distancia / velocidad promedio).
# Cuando haya datos reales de viajes, este módulo llamará al modelo de ML
# en lugar de usar eta_baseline().

from data.rutas import RUTAS
from services.distancia import (
    distancia_km,
    eta_baseline,
    tiempo_caminando,
    paradero_mas_cercano,
)
from services.tracking import obtener_buses_activos


def buscar_paradero_por_id(paradero_id: str) -> dict | None:
    """Busca un paradero en todas las rutas por su ID."""
    for ruta in RUTAS.values():
        for p in ruta["paraderos"]:
            if p["id"] == paradero_id:
                return p
    return None


def calcular_recomendacion(
    paradero_destino_id: str,
    pasajero_lat: float,
    pasajero_lng: float,
) -> dict:
    """
    Calcula la mejor recomendación de bus y paradero para el pasajero.

    Retorna un dict con:
    - recomendacion: el mejor bus encontrado
    - nota: advertencia si el ETA es baseline (sin ML aún)
    - error: mensaje de error si no se pudo calcular
    """
    # 1. Verificar que el paradero destino existe
    destino = buscar_paradero_por_id(paradero_destino_id)
    if not destino:
        return {"error": f"Paradero destino '{paradero_destino_id}' no encontrado"}

    # 2. Obtener buses activos con señal
    buses_activos = obtener_buses_activos()
    if not buses_activos:
        return {"error": "No hay buses activos con señal en este momento"}

    # 3. Calcular opciones para cada bus activo
    opciones = []
    for bus in buses_activos:
        ruta_bus = RUTAS.get(bus["ruta"])
        if not ruta_bus:
            continue

        # Distancia del bus al paradero destino → ETA
        dist_bus_a_destino = distancia_km(
            bus["latitud"], bus["longitud"],
            destino["lat"], destino["lng"]
        )
        eta = eta_baseline(dist_bus_a_destino)

        # Paradero más cercano al pasajero en la ruta de este bus
        mejor_paradero = paradero_mas_cercano(
            pasajero_lat, pasajero_lng,
            ruta_bus["paraderos"]
        )
        dist_pasajero_a_paradero = distancia_km(
            pasajero_lat, pasajero_lng,
            mejor_paradero["lat"], mejor_paradero["lng"]
        )
        caminar = tiempo_caminando(dist_pasajero_a_paradero)

        opciones.append({
            "bus_id":               bus["bus_id"],
            "ruta":                 bus["ruta"],
            "paradero_recomendado": mejor_paradero["nombre"],
            "paradero_id":          mejor_paradero["id"],
            "eta_minutos":          eta,
            "caminar_minutos":      caminar,
            "tiempo_total":         round(eta + caminar, 1),
        })

    if not opciones:
        return {"error": "No se pudo calcular ninguna recomendación"}

    # 4. Elegir el bus con menor tiempo total (bus + caminata)
    mejor = min(opciones, key=lambda x: x["tiempo_total"])
    return {
        "recomendacion": mejor,
        "nota": "ETA calculado con velocidad promedio (baseline — modelo ML pendiente de entrenamiento)"
    }
