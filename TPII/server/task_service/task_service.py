from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TareaRequest(BaseModel):
    parametros: dict
    calculo: str

@app.get("/status/")
def status():
    return {"status": "Its running","status_code": "200"}

@app.post("/ejecutarTarea/")
def ejecutar_tarea(request: TareaRequest):
    """
    Procesa la tarea solicitada.
    """
    parametros = request.parametros
    operacion = request.calculo.lower()

    resultado = None
    if operacion == "suma":
        resultado = sum(parametros.values())
        return {"resultado": resultado}
    elif operacion == "multiplicacion":
        resultado = 1
        for val in parametros.values():
            resultado *= val
        return {"resultado": resultado}
    elif operacion == "promedio":
        resultado = sum(parametros.values()) / len(parametros) if parametros else 0
        return {"resultado": resultado}
    else:
        return {"error": "Operación no soportada"}

