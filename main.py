from fastapi import FastAPI
from routers import conductor, pasajero, buses, usuarios
from database.conexion import engine
from database import modelos

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

@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "Backend de El Burrito funcionando"}


# cd C:\Users\thele\Downloads\burrito-backend\burrito-backend
# venv\Scripts\activate
# uvicorn main:app --reload