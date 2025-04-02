from fastapi import FastAPI
from pydantic import BaseModel
from utils.json_logger import get_json_logger

app = FastAPI()

logger = get_json_logger("task_service", "logs/task_service.log.json")

class TareaRequest(BaseModel):
    parametros: dict
    calculo: str

@app.get("/status/")
def status():
    logger.info("Endpoint /status/ fue consultado")
    return {"status": "Its running", "status_code": "200"}

@app.post("/ejecutarTarea/")
def ejecutar_tarea(request: TareaRequest):
    parametros = request.parametros
    operacion = request.calculo.lower()

    logger.info(f"Tarea recibida: operación='{operacion}', parámetros={parametros}")

    try:
        resultado = None
        if operacion == "suma":
            resultado = sum(parametros.values())
        elif operacion == "multiplicacion":
            resultado = 1
            for val in parametros.values():
                resultado *= val
        elif operacion == "promedio":
            resultado = sum(parametros.values()) / len(parametros) if parametros else 0
        else:
            logger.error(f"Operación no soportada: {operacion}")
            return {"error": "Operación no soportada"}

        logger.info(f"Resultado calculado: {resultado}")
        return {"resultado": resultado}

    except Exception as e:
        logger.exception("Error procesando la tarea")
        return {"error": str(e)}
