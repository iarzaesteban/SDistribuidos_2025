from fastapi import FastAPI
from tpFinal.Pilar3.coordinador.app.routes import router as nct_router
from utils.logger import logger

app = FastAPI(title="Nodo Coordinador (NCT)")

@app.on_event("startup")
def startup_event():
    logger.info("NCT Service started")

    try:
        print("Nombre guardado en Redis con éxito")
    except Exception as e:
        print(f"Error al guardar nombre en Redis: {e}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("NCT Service stopped")

app.include_router(nct_router)
