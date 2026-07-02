# database/modelos.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database.conexion import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id        = Column(Integer, primary_key=True, index=True)
    nombre    = Column(String, nullable=False)
    correo    = Column(String, unique=True, index=True, nullable=False)
    password  = Column(String, nullable=False)
    tipo      = Column(String, nullable=False)  # "pasajero" o "conductor"
    creado_en = Column(DateTime, server_default=func.now())


class Bus(Base):
    __tablename__ = "buses"

    id      = Column(Integer, primary_key=True, index=True)
    placa   = Column(String, unique=True, nullable=False)  # ej. "BFK-309"
    ruta    = Column(String, nullable=True)   # ruta actualmente asignada
    activo  = Column(Boolean, default=False)  # True cuando conductor lo usa


class RegistroGPS(Base):
    __tablename__ = "registros_gps"

    id        = Column(Integer, primary_key=True, index=True)
    bus_id    = Column(String, nullable=False, index=True)
    ruta      = Column(String, nullable=False)
    latitud   = Column(Float, nullable=False)
    longitud  = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())


class Recorrido(Base):
    __tablename__ = "recorridos"

    id           = Column(Integer, primary_key=True, index=True)
    bus_placa    = Column(String, nullable=False)
    ruta         = Column(String, nullable=False)
    hora_inicio  = Column(DateTime, server_default=func.now())
    hora_fin     = Column(DateTime, nullable=True)
    completado   = Column(Boolean, default=False)


class PuntoRecorrido(Base):
    __tablename__ = "puntos_recorrido"

    id           = Column(Integer, primary_key=True, index=True)
    recorrido_id = Column(Integer, nullable=False, index=True)
    latitud      = Column(Float, nullable=False)
    longitud     = Column(Float, nullable=False)
    timestamp    = Column(DateTime, server_default=func.now())


class Viaje(Base):
    __tablename__ = "viajes"

    id                   = Column(Integer, primary_key=True, index=True)
    pasajero_id          = Column(Integer, nullable=True)
    destino_id           = Column(String, nullable=False)
    bus_recomendado_id   = Column(String, nullable=False)
    paradero_recomendado = Column(String, nullable=False)
    eta_estimado         = Column(Float, nullable=False)
    eta_real             = Column(Float, nullable=True)
    timestamp            = Column(DateTime, server_default=func.now())


class Incidente(Base):
    __tablename__ = "incidentes"

    id          = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, nullable=False)
    ruta        = Column(String, nullable=False)
    activo      = Column(Boolean, default=True)
    creado_en   = Column(DateTime, server_default=func.now())

class RutaTrazadaAdmin(Base):
    __tablename__ = "rutas_trazadas_admin"

    id                = Column(Integer, primary_key=True, index=True)
    nombre            = Column(String, nullable=False)  # "Ruta Norte"
    ruta_clave        = Column(String, nullable=False)  # "cono_norte"
    puntos            = Column(String, nullable=False)  # JSON [[lat,lng],...]
    duracion_segundos = Column(Float, nullable=False)
    distancia_metros  = Column(Float, nullable=False)
    creado_en         = Column(DateTime, server_default=func.now())