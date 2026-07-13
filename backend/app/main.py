from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import detection

app = FastAPI(title="EcoSorter API", version="1.0.0")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detection.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoSorter API. Ready for Sprint 1!"}

@app.post("/classify")
def classify_waste(data: dict):
    # Endpoint base para el flujo de clasificación de residuos
    return {
        "status": "success",
        "label": "mock_plastic_bottle",
        "veredicto": "Contenedor Azul (Reciclables)",
        "preparacion": "Enjuagar, secar y aplastar antes de depositar."
    }
