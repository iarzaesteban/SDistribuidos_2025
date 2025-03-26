import requests
import time
import json
from pathlib import Path
import pytest
pytestmark = pytest.mark.localtest

BASE_URL = "http://localhost:8000/getRemoteTask/"
RESULTADOS_JSON = Path("tests/resultados_real.json")

def medir_tiempo(operacion, parametros, esperado):
    payload = {
        "imagen_docker": "tasks_image:latest",
        "calculo": operacion,
        "parametros": parametros,
        "datos_adicionales": {"descripcion": f"{operacion} real"}
    }

    start = time.perf_counter()
    response = requests.post(BASE_URL, json=payload)
    duration_ms = (time.perf_counter() - start) * 1000

    print(f"\n🧪 Operación: {operacion}")
    print(f"⏱ Tiempo real de respuesta: {duration_ms:.2f} ms")
    print(f"📦 Respuesta: {response.status_code} - {response.text}")

    assert response.status_code == 200
    assert response.json().get("resultado") == esperado

    return {
        "operacion": operacion,
        "parametros": parametros,
        "resultado_esperado": esperado,
        "respuesta": response.json(),
        "status_code": response.status_code,
        "tiempo_ms": round(duration_ms, 2)
    }


def test_tiempo_real():
    resultados = []

    resultados.append(medir_tiempo("suma", {"a": 10, "b": 20, "c": 5}, 35))
    resultados.append(medir_tiempo("multiplicacion", {"a": 2, "b": 3, "c": 4}, 24))
    resultados.append(medir_tiempo("promedio", {"a": 10, "b": 20}, 15))

    with open(RESULTADOS_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Resultados guardados en {RESULTADOS_JSON.resolve()}")

if __name__ == "__main__":
    test_tiempo_real()
