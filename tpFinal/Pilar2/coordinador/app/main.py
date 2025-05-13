from fastapi import FastAPI
from app.routes import router as nct_router
from utils.logger import logger
from utils.redis_client import redis_client

app = FastAPI(title="Nodo Coordinador (NCT)")

@app.on_event("startup")
def startup_event():
    logger.info("NCT Service started")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("NCT Service stopped")

@app.on_event("startup")
def startup_event():
    try:
        redis_client.set("nombre", "Pilar")
        print("Nombre guardado en Redis con éxito")
    except Exception as e:
        print(f"Error al guardar nombre en Redis: {e}")

app.include_router(nct_router)
