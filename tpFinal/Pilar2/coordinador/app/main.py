from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as coordinador_router
from utils.logger import logger
from utils.helper import generate_genesis_block

app = FastAPI(title="Nodo Coordinador (NCT)")

app.include_router(coordinador_router, prefix="/nct")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(coordinador_router)
