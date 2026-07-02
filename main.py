from fastapi import FastAPI
from routers import conductor, pasajero, buses, usuarios, recorridos
from database.conexion import engine
from database import modelos
from database.conexion import SessionLocal
from database.modelos import Bus

modelos.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="El Burrito en Tiempo Real — Backend",
    description="API del sistema de localización y recomendación de buses de UNMSM.",
    version="0.1.0",
)

app.include_router(conductor.router)
app.include_router(pasajero.router)
app.include_router(buses.router)
app.include_router(usuarios.router)
app.include_router(recorridos.router)


def poblar_buses():
    db = SessionLocal()
    try:
        buses_iniciales = [
            {"placa": "BUS-001", "ruta": None},
            {"placa": "BUS-002", "ruta": None},
            {"placa": "BUS-003", "ruta": None},
            {"placa": "BUS-004", "ruta": None},
        ]
        for b in buses_iniciales:
            existe = db.query(Bus).filter(Bus.placa == b["placa"]).first()
            if not existe:
                db.add(Bus(placa=b["placa"], ruta=b["ruta"], activo=False))
        db.commit()
    finally:
        db.close()


poblar_buses()


@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "Backend de El Burrito funcionando"}


# cd C:\Users\thele\Downloads\burrito-backend\burrito-backend
# venv\Scripts\activate
# uvicorn main:app --reload