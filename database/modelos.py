# database/modelos.py
# Tablas de la base de datos del sistema.

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


class Conductor(Base):
    __tablename__ = "conductores"

    id       = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    bus_id   = Column(String, nullable=False)
    ruta     = Column(String, nullable=False)
    activo   = Column(Boolean, default=True)


class RegistroGPS(Base):
    __tablename__ = "registros_gps"

    id        = Column(Integer, primary_key=True, index=True)
    bus_id    = Column(String, nullable=False, index=True)
    ruta      = Column(String, nullable=False)
    latitud   = Column(Float, nullable=False)
    longitud  = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())


class Viaje(Base):
    __tablename__ = "viajes"

    id                    = Column(Integer, primary_key=True, index=True)
    pasajero_id           = Column(Integer, nullable=True)
    destino_id            = Column(String, nullable=False)
    bus_recomendado_id    = Column(String, nullable=False)
    paradero_recomendado  = Column(String, nullable=False)
    eta_estimado          = Column(Float, nullable=False)
    eta_real              = Column(Float, nullable=True)  # se llena después
    timestamp             = Column(DateTime, server_default=func.now())


class Incidente(Base):
    __tablename__ = "incidentes"

    id          = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, nullable=False)
    ruta        = Column(String, nullable=False)
    activo      = Column(Boolean, default=True)
    creado_en   = Column(DateTime, server_default=func.now())

class RutaTrazada(Base):
    __tablename__ = "rutas_trazadas"

    id          = Column(Integer, primary_key=True, index=True)
    ruta        = Column(String, nullable=False)  # "cono_norte", etc.
    lapiz_index = Column(Integer, nullable=False)  # 0, 1, 2, 3
    color       = Column(String, nullable=False)   # "#e94560", etc.
    puntos      = Column(String, nullable=False)   # JSON: [[lat,lng], ...]
    creado_en   = Column(DateTime, server_default=func.now())