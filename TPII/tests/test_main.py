# test_main.py

from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'server_app')))

from main import app


client = TestClient(app)

def test_suma_correcta():
    response = client.post("/getRemoteTask/", json={
        "imagen_docker": "tasks_image:latest",
        "calculo": "suma",
        "parametros": {"a": 10, "b": 20, "c": 5},
        "datos_adicionales": {"descripcion": "Suma de 3 valores"}
    })
    assert response.status_code == 200
    assert "resultado" in response.json()
    assert response.json()["resultado"] == 35

def test_operacion_no_valida():
    response = client.post("/getRemoteTask/", json={
        "imagen_docker": "tasks_image:latest",
        "calculo": "no_existe",
        "parametros": {"a": 10, "b": 20},
    })
    assert response.status_code == 200
    assert "error" in response.json()
    assert "no soportada" in response.json()["error"]

def test_faltan_parametros():
    response = client.post("/getRemoteTask/", json={
        "imagen_docker": "tasks_image:latest",
        "calculo": "suma"
        # falta 'parametros'
    })
    assert response.status_code == 422  # Error de validación
