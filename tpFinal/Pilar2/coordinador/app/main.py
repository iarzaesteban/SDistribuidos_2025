from fastapi import FastAPI
from app.routes import router as nct_router
from utils.logger import logger
from utils.redis_client import redis_client
from utils.result_listener import start_result_listener
from utils.transaction_pool import start_transaction_pool_manager

app = FastAPI(title="Nodo Coordinador (NCT)")

@app.on_event("startup")
def startup_event():
    logger.info("NCT Service started")

    try:
        redis_client.set("nombre", "Pilar")
        print("Nombre guardado en Redis con éxito")
    except Exception as e:
        print(f"Error al guardar nombre en Redis: {e}")

    start_result_listener()
    start_transaction_pool_manager()  # ⏱️ Inicia el pool manager

@app.on_event("shutdown")
def shutdown_event():
    logger.info("NCT Service stopped")

app.include_router(nct_router)
