from fastapi import FastAPI
from app.routes import router as nct_router
from utils.logger import logger
from utils.main import start_move_transactions_into_queues

app = FastAPI(title="Nodo Coordinador (NCT)")

@app.on_event("startup")
def startup_event():
    logger.info("NCT Service started")
    try:
        start_move_transactions_into_queues()
        logger.info("NCT Service started sussefully")
    except Exception as e:
        logger.error(f"Error al correr el coordinado: {e}")

    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("NCT Service stopped")

app.include_router(nct_router)
