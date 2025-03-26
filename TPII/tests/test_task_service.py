from fastapi.testclient import TestClient

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'task_service')))

from task_service import app

client = TestClient(app)


def test_status():
    response = client.get("/status/")
    assert response.status_code == 200
    assert response.json()["status"] == "Its running"

def test_suma():
    response = client.post("/ejecutarTarea/", json={
        "calculo": "suma",
        "parametros": {"a": 2, "b": 3, "c": 5}
    })
    assert response.status_code == 200
    assert response.json()["resultado"] == 10

def test_multiplicacion():
    response = client.post("/ejecutarTarea/", json={
        "calculo": "multiplicacion",
        "parametros": {"a": 2, "b": 3, "c": 4}
    })
    assert response.status_code == 200
    assert response.json()["resultado"] == 24

def test_promedio():
    response = client.post("/ejecutarTarea/", json={
        "calculo": "promedio",
        "parametros": {"a": 10, "b": 20}
    })
    assert response.status_code == 200
    assert response.json()["resultado"] == 15

def test_operacion_no_valida():
    response = client.post("/ejecutarTarea/", json={
        "calculo": "dividir",
        "parametros": {"a": 10, "b": 2}
    })
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"] == "Operación no soportada"
