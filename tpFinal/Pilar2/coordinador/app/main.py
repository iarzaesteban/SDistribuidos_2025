from fastapi import FastAPI
from app.routes import router as nct_router
from utils.logger import logger
from utils.helper import generate_genesis_block

app = FastAPI(title="Nodo Coordinador (NCT)")

app.include_router(coordinador_router, prefix="/nct")
@app.on_event("startup")
def startup_event():
    logger.info("NCT Service started")
    try:
        generate_genesis_block()
        logger.info("NCT Service started sussefully")
    except Exception as e:
        logger.error(f"Error al correr el coordinado: {e}")

    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("NCT Service stopped")

app.include_router(nct_router)
