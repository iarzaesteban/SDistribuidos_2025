import requests

URL = "http://34.28.246.155/upload"
IMG_PATH = "test.jpg"  # Cambialo por la imagen que quieras

for i in range(10):
    with open(IMG_PATH, "rb") as f:
        files = {"image": f}
        res = requests.post(URL, files=files)
        print(f"[{i}] Status: {res.status_code} - Respuesta: {res.text}")
