from fastapi import FastAPI
from app.routes import router as nct_router
from utils.logger import logger
from utils.result_listener import start_result_listener
from utils.transaction_pool import start_transaction_pool_manager

app = FastAPI(title="Nodo Coordinador (NCT)")

@app.on_event("startup")
def startup_event():
    logger.info("NCT Service started")
    try:
        start_result_listener()
        start_transaction_pool_manager()
        logger.info("NCT Service started sussefully")
    except Exception as e:
        logger.error(f"Error al correr el coordinado: {e}")

    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("NCT Service stopped")

app.include_router(nct_router)
