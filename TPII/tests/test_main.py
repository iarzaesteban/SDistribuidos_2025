from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys, os, time

# Agregar el path para importar main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'server_app')))
from main import app

client = TestClient(app)

@patch('main.client')
def test_suma_correcta(mock_docker_client):
    mock_image = MagicMock()
    mock_container = MagicMock()
    mock_container.attrs = {
        'NetworkSettings': {
            'Networks': {
                'app_network': {
                    'IPAddress': '127.0.0.1'
                }
            }
        }
    }

    mock_docker_client.images.get.return_value = mock_image
    mock_docker_client.containers.run.return_value = mock_container

    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"resultado": 35}

        response = client.post("/getRemoteTask/", json={
            "imagen_docker": "tasks_image:latest",
            "calculo": "suma",
            "parametros": {"a": 10, "b": 20, "c": 5},
            "datos_adicionales": {"descripcion": "Suma de 3 valores"}
        })
        assert response.status_code == 200
        assert response.json()["resultado"] == 35

@patch('main.client')
def test_operacion_no_valida(mock_docker_client):
    mock_image = MagicMock()
    mock_container = MagicMock()
    mock_container.attrs = {
        'NetworkSettings': {
            'Networks': {
                'app_network': {
                    'IPAddress': '127.0.0.1'
                }
            }
        }
    }

    mock_docker_client.images.get.return_value = mock_image
    mock_docker_client.containers.run.return_value = mock_container

    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"error": "Operación no soportada"}

        response = client.post("/getRemoteTask/", json={
            "imagen_docker": "tasks_image:latest",
            "calculo": "no_existe",
            "parametros": {"a": 10, "b": 20}
        })
        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Operación no soportada"

def test_faltan_parametros():
    response = client.post("/getRemoteTask/", json={
        "imagen_docker": "tasks_image:latest",
        "calculo": "suma"
        # Falta el campo 'parametros'
    })
    assert response.status_code == 422  # Error de validación

@patch('main.client')
def test_tiempos_operaciones(mock_docker_client):
    mock_image = MagicMock()
    mock_container = MagicMock()
    mock_container.attrs = {
        'NetworkSettings': {
            'Networks': {
                'app_network': {
                    'IPAddress': '127.0.0.1'
                }
            }
        }
    }

    mock_docker_client.images.get.return_value = mock_image
    mock_docker_client.containers.run.return_value = mock_container

    operaciones = [
        ("suma", {"a": 10, "b": 20, "c": 5}, {"resultado": 35}),
        ("multiplicacion", {"a": 2, "b": 3, "c": 4}, {"resultado": 24}),
        ("promedio", {"a": 10, "b": 20}, {"resultado": 15}),
        ("no_existe", {"a": 10, "b": 20}, {"error": "Operación no soportada"})
    ]

    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200

        for operacion, parametros, respuesta_mock in operaciones:
            mock_post.return_value.json.return_value = respuesta_mock

            start_time = time.perf_counter()
            response = client.post("/getRemoteTask/", json={
                "imagen_docker": "tasks_image:latest",
                "calculo": operacion,
                "parametros": parametros
            })
            duration_ms = (time.perf_counter() - start_time) * 1000

            print(f"\n⏱ Tiempo de respuesta ({operacion}): {duration_ms:.2f} ms")

            assert response.status_code == 200
            if "resultado" in respuesta_mock:
                assert response.json()["resultado"] == respuesta_mock["resultado"]
            else:
                assert response.json()["error"] == respuesta_mock["error"]
